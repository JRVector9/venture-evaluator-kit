#!/usr/bin/env python3
"""Render a private, self-contained Korean HTML report from validated JSON.

Python 3.9+, standard library only. No model calls, web requests, remote fonts,
account access, automatic browser launch, or raw HTML injection. Existing files
are never overwritten. This renders an assessment; it does not perform one.
"""
from __future__ import annotations

import argparse
import base64
from datetime import date
from decimal import Decimal
import hashlib
from html import escape
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.1.2'
DIMENSIONS = (
    ('significant', 'Significant', '시장 기회'),
    ('scalable', 'Scalable', '확장성'),
    ('sustainable', 'Sustainable', '지속가능성'),
    ('frequency', 'Frequency', '고빈도'),
    ('network', 'Network effect', '네트워크 효과'),
    ('retention', 'Retention', '리텐션'),
    ('standardization', 'Standardization', '표준화'),
    ('distribution', 'Distribution', '유통·고객 획득'),
    ('demand', 'Existing demand', '기존 수요·경험 개선'),
    ('monetization', 'Monetization', '수익화'),
    ('ai_defensibility', 'AI defensibility', 'AI 기능 방어력'),
    ('customization', 'Customization independence', '커스텀 독립성'),
)
RATING_MEANING = {'◎': '강한 구조', '○': '유리하나 미검증 조건 존재', '△': '구조적 약점', '×': '구조적 부적합', '?': '근거 부족'}


class ReportError(ValueError):
    """A helpful error for invalid or unsafe report data."""


def text(value: Any) -> str:
    return escape(str(value), quote=True)


def lines(value: str) -> str:
    return text(value).replace('\n', '<br>')


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReportError(message)


def schema_check(value: Any, spec: dict, root: dict, path: str = '$') -> None:
    """Validate the exact JSON Schema subset used by this bundled schema.

    This is intentionally not advertised as a general JSON Schema engine.
    The published schema is also usable by full JSON Schema validators.
    """
    if '$ref' in spec:
        resolved = root
        for segment in spec['$ref'][2:].split('/'):
            resolved = resolved[segment]
        schema_check(value, resolved, root, path)
        return
    if 'const' in spec:
        require(value == spec['const'], f'{path}: expected {spec["const"]!r}')
    if 'enum' in spec:
        require(value in spec['enum'], f'{path}: expected one of {spec["enum"]}')
    types = spec.get('type', [])
    types = [types] if isinstance(types, str) else types
    checks = {
        'string': lambda v: isinstance(v, str),
        'object': lambda v: isinstance(v, dict),
        'array': lambda v: isinstance(v, list),
        'integer': lambda v: isinstance(v, int) and not isinstance(v, bool),
        'boolean': lambda v: isinstance(v, bool),
        'null': lambda v: v is None,
    }
    if types:
        require(any(checks[t](value) for t in types), f'{path}: expected {types}, got {type(value).__name__}')
    if isinstance(value, dict):
        props = spec.get('properties', {})
        for key in spec.get('required', []):
            require(key in value, f'{path}: required field {key!r} is missing')
        if spec.get('additionalProperties') is False:
            require(not (set(value) - set(props)), f'{path}: unknown fields {sorted(set(value)-set(props))}')
        for key, child in value.items():
            if key in props:
                schema_check(child, props[key], root, f'{path}.{key}')
    elif isinstance(value, list):
        require(len(value) >= spec.get('minItems', 0), f'{path}: too few items')
        require(len(value) <= spec.get('maxItems', 100000), f'{path}: too many items')
        if spec.get('uniqueItems'):
            require(len({json.dumps(v, sort_keys=True) for v in value}) == len(value), f'{path}: duplicate items')
        for i, child in enumerate(value):
            schema_check(child, spec.get('items', {}), root, f'{path}[{i}]')
    elif isinstance(value, str):
        require(len(value) >= spec.get('minLength', 0), f'{path}: blank value')
        require(len(value) <= spec.get('maxLength', 1000000), f'{path}: text too long')
        if 'pattern' in spec:
            # fullmatch: Python's `$` would otherwise accept a trailing newline ("E1\n") that breaks HTML ids.
            require(bool(re.fullmatch(spec['pattern'], value)), f'{path}: invalid format')
        require('\x00' not in value, f'{path}: NUL characters are not allowed')
        require('' not in value and '' not in value, f'{path}: replace host-only citation tokens with evidence IDs such as E1')
    elif isinstance(value, int) and not isinstance(value, bool):
        require(value >= spec.get('minimum', -10**30), f'{path}: value below minimum')
        require(value <= spec.get('maximum', 10**30), f'{path}: value above maximum')


def check_source_url(url: str) -> None:
    if not url:
        return
    require(not any(c.isspace() or ord(c) < 32 for c in url), 'Source URL contains whitespace/control characters')
    try:
        parsed = urlsplit(url)
        host = parsed.hostname
    except ValueError as exc:
        raise ReportError(f'Invalid source URL: {exc}') from exc
    require(parsed.scheme in ('https', 'http') and bool(host), 'Source URL must use https:// or http:// with a host')
    require(parsed.username is None and parsed.password is None, 'Credentials are not allowed in source URLs')


def validate(data: dict) -> None:
    schema = json.loads((ROOT / 'assets/report.schema.json').read_text(encoding='utf-8'))
    schema_check(data, schema, schema)
    try:
        date.fromisoformat(data['meta']['date'])
    except ValueError as exc:
        raise ReportError('meta.date must be a real ISO date') from exc
    ids = [s['id'] for s in data['sources']]
    require(len(ids) == len(set(ids)), 'Duplicate source IDs')
    ventures = [v['id'] for v in data['ventures']]
    require(len(ventures) == len(set(ventures)), 'Duplicate venture IDs')
    known = set(ids)

    def walk(node: Any, path: str = '$') -> None:
        if isinstance(node, dict):
            if 'evidence' in node:
                missing = set(node['evidence']) - known
                require(not missing, f'{path}: unknown evidence references {sorted(missing)}')
            for key, val in node.items():
                walk(val, f'{path}.{key}')
        elif isinstance(node, list):
            for i, val in enumerate(node):
                walk(val, f'{path}[{i}]')
    walk(data)
    for v in data['ventures']:
        for key, rating in v['ratings'].items():
            if rating['current'] != '?':
                require(bool(rating['evidence']), f'{v["id"]}.{key}: a non-unknown rating needs evidence references')
            potential = rating.get('potential')
            if potential is not None and potential != rating['current']:
                require(bool(rating.get('condition', '').strip()), f'{v["id"]}.{key}: a changed potential needs an explicit condition')
                require(bool(rating['evidence']), f'{v["id"]}.{key}: potential needs evidence references')
    for exp in data['experiments']:
        require(exp['venture_id'] in ventures, f'Experiment references unknown venture: {exp["venture_id"]}')
    for src in data['sources']:
        check_source_url(src.get('url', ''))
    for item in data.get('budget', {}).get('items', []):
        if item['low'] is not None and item['high'] is not None:
            require(item['low'] <= item['high'], f'Budget {item["name"]}: low must not exceed high')


def refs(ids: List[str]) -> str:
    return ''.join(f'<a class="source-ref" href="#source-{text(i)}" aria-label="근거 {text(i)}">[{text(i)}]</a>' for i in ids)


def claim(c: dict, cls: str = 'claim') -> str:
    return f'<p class="{cls}">{lines(c["text"])}{refs(c["evidence"])}</p>'


def rating_markup(r: dict) -> str:
    current = r['current']
    css = 'strong' if current == '◎' else 'unknown' if current == '?' else ''
    value = f'<span class="rating {css}" aria-label="현재: {text(RATING_MEANING[current])}">{text(current)}</span>'
    potential = r.get('potential')
    if potential is not None and potential != current:
        value += f'<span class="conditional" aria-label="조건 충족 시: {text(RATING_MEANING[potential])}"><span class="rating-arrow" aria-hidden="true">→</span><span class="rating-to">{text(potential)}</span></span>'
    return value


def money(value: Optional[int]) -> str:
    return '미산정' if value is None else f'{value:,}'


def compact_money(value: int) -> str:
    if value >= 10000:
        n = Decimal(value) / Decimal(10000)
        return format(n, ',f').rstrip('0').rstrip('.') if '.' in format(n, ',f') else format(n, ',f')
    return f'{value:,}'


def budget_totals(budget: dict) -> dict:
    low = high = missing = 0
    for item in budget['items']:
        if item['low'] is None or item['high'] is None:
            missing += 1
            continue
        mult = budget['period_months'] if item['cadence'] == 'monthly' else 1
        low += item['low'] * mult
        high += item['high'] * mult
    return {'low': low, 'high': high, 'missing': missing}


def section(section_id: str, number: str, english: str, title: str, body: str, intro: str = '') -> str:
    return f'''<section id="{section_id}" class="chapter" aria-labelledby="{section_id}-heading">
<div class="chapter-head"><div><div class="eyebrow">{text(english)}</div><h2 id="{section_id}-heading">{text(title)}</h2>{f'<p class="lede">{lines(intro)}</p>' if intro else ''}</div><span class="chapter-num" aria-hidden="true">{number}</span></div>{body}</section>'''


def scorecard(data: dict) -> str:
    headers = ''.join(f'<th scope="col">{text(label if key not in ("frequency", "network") else korean)}<small>{text(korean) if key not in ("frequency", "network") else ""}</small></th>' for key, label, korean in DIMENSIONS[:5])
    rows = []
    for v in data['ventures']:
        cells = ''.join(f'<td><a href="#criterion-{v["id"]}-{key}" title="{text(r["reason"])}">{rating_markup(r)}</a></td>' for key, _, _ in DIMENSIONS[:5] for r in [v['ratings'][key]])
        rows.append(f'<tr><td><a class="venture-name" href="#venture-{v["id"]}">{text(v["name"])}</a><span class="venture-subtitle">{text(v["category"])} · {text(v["stage"])}</span></td>{cells}<td>{text(v["verdict"])}{refs(v["evidence"])}<span class="venture-subtitle">근거 신뢰도: {text(v["confidence"])}</span></td></tr>')
    return f'''<div class="exhibit-heading"><div><div class="exhibit-label">EXHIBIT 01</div><div class="exhibit-title">현재 사업 구조와 조건부 잠재력 비교</div></div><div class="segmented js-only" role="group" aria-label="평가 표시 방식"><button type="button" data-rating-view="current" aria-pressed="false">현재 기준</button><button type="button" data-rating-view="conditional" aria-pressed="true">개선 조건 포함</button></div></div>
<div class="table-wrap" tabindex="0" role="region" aria-label="GSR+ 비교표. 작은 화면에서는 가로로 스크롤할 수 있습니다."><table class="scorecard" data-view="conditional"><caption class="sr-only">Significant, Scalable, Sustainable, 고빈도, 네트워크 효과와 GSR+ 잠재력</caption><thead><tr><th scope="col">서비스</th>{headers}<th scope="col">GSR+ 잠재력<small>조건부 판단</small></th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<div class="legend"><span>◎ 강한 구조</span><span>○ 유리하나 조건 존재</span><span>△ 구조적 약점</span><span>× 구조적 부적합</span><span>? 근거 부족</span></div><p class="conditional-note">화살표 오른쪽은 현재 실적이 아닌 조건부 가설입니다. 기호를 누르면 해당 판정의 근거와 개선 조건으로 이동합니다.</p><p class="sr-only" id="rating-status" aria-live="polite">현재 판정과 조건부 개선 가능성을 함께 표시합니다.</p>
<div class="portfolio-note"><strong>비교표를 읽는 방법</strong><p>잠재력과 당장 실행하기 좋은 순서는 다릅니다. 시장성·실적이 미확인이라면 판단을 유보하며, 낮은 VC 적합성이 낮은 수익성을 뜻하지는 않습니다. 사업별 자료의 범위와 신뢰도는 아래 상세 분석에서 확인합니다.</p></div>'''


def detail(v: dict, n: int) -> str:
    rows = []
    for key, label, korean in DIMENSIONS:
        r = v['ratings'].get(key, {'current': '?', 'reason': '이 항목을 판정할 자료가 제공되지 않았습니다.', 'evidence': []})
        condition = f'<span class="condition">개선 조건: {lines(r["condition"])}</span>' if r.get('condition') else ''
        rows.append(f'<tr id="criterion-{v["id"]}-{key}"><th scope="row">{text(korean)}<span class="venture-subtitle">{text(label)}</span></th><td style="width:82px">{rating_markup(r)}</td><td>{lines(r["reason"])}{refs(r["evidence"])}{condition}</td></tr>')
    strengths = ''.join(claim(c) for c in v['strengths']) or '<p class="claim">확인된 강점 자료가 없습니다.</p>'
    risks = ''.join(claim(c) for c in v['risks']) or '<p class="claim">위험 검토 자료가 부족합니다. 위험이 없다는 뜻은 아닙니다.</p>'
    return f'''<article class="venture-detail" id="venture-{v['id']}"><div class="venture-detail-header"><div><div class="venture-label">BUSINESS {n:02d} / {text(v['category'])}</div><h3>{text(v['name'])}</h3></div><div class="detail-verdict"><strong>{text(v['verdict'])}{refs(v['evidence'])}</strong><span class="confidence">{text(v['stage'])} · 근거 신뢰도 {text(v['confidence'])}</span></div></div><p class="venture-thesis">{lines(v['thesis'])}{refs(v['evidence'])}</p><div class="analysis-grid"><div class="analysis-block"><h4>강한 이유</h4>{strengths}</div><div class="analysis-block risk"><h4>핵심 위험</h4>{risks}</div></div><div class="next-move"><div class="eyebrow">PRIORITY MOVE</div>{claim(v['next_move'])}</div><p class="confidence">평가 범위: {text(v['basis'])}<br>신뢰도 판단: {lines(v['confidence_note'])}</p><details><summary>12개 평가 항목 · 판정 근거와 개선 조건</summary><div class="table-wrap" tabindex="0" role="region" aria-label="{text(v['name'])} 상세 평가"><table class="detail-table"><thead><tr><th scope="col">평가 항목</th><th scope="col" style="width:82px">현재 → 조건부</th><th scope="col">근거와 조건</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></details></article>'''


def render(data: dict) -> str:
    validate(data)
    meta = data['meta']
    summary = data['summary']
    css = (ROOT / 'assets/report/report.css').read_text(encoding='utf-8')
    js = (ROOT / 'assets/report/report.js').read_text(encoding='utf-8')
    digest = base64.b64encode(hashlib.sha256(js.encode('utf-8')).digest()).decode('ascii')
    flag = ''
    if meta['status'] == 'sample':
        flag = '<div class="sample-flag">DESIGN SAMPLE · 가상 사업·가정 수치로 구성한 디자인 시연입니다.</div>'
    elif meta['status'] == 'template':
        flag = '<div class="sample-flag">INPUT TEMPLATE · 실제 자료를 채우기 전의 빈 보고서입니다.</div>'
    cover = f'''<section class="cover" id="cover" aria-labelledby="report-title"><div class="cover-top"><div class="eyebrow">VENTURE STRATEGY / GSR+ ASSESSMENT</div><div class="doc-id">{text(meta['report_id'])}</div></div>{flag}<h1 id="report-title">{lines(meta['title'])}</h1><p class="subtitle">{lines(meta['subtitle'])}</p><div class="cover-rule"></div><p class="cover-thesis">{lines(summary['headline'])}</p><div class="cover-meta"><div><span class="meta-label">PREPARED FOR</span><span class="meta-value">{text(meta['prepared_for'])}</span></div><div><span class="meta-label">ASSESSMENT DATE</span><span class="meta-value">{text(meta['date'].replace('-', '.'))}</span></div><div><span class="meta-label">REPORT SCOPE</span><span class="meta-value">{len(data['ventures'])}개 사업 · {text(meta['mode'])}</span></div></div></section>'''
    recs = ''.join(f'<div class="recommendation"><span class="index">{i:02d}</span><div><h3>{text(r["title"])}</h3><p>{lines(r["body"])}{refs(r["evidence"])}</p></div></div>' for i, r in enumerate(summary['recommendations'], 1))
    exec_body = f'''<p class="key-message">{lines(summary['headline'])}</p><p class="summary-body">{lines(summary['thesis'])}</p><div class="recommendations">{recs}</div><div class="decision-strip"><div><div class="eyebrow">NOW / 지금 검증할 것</div><p>{lines(summary['now'])}</p></div><div><div class="eyebrow">LATER / 나중에 할 것</div><p>{lines(summary['later'])}</p></div><div><div class="eyebrow">NOT NOW / 하지 않을 것</div><p>{lines(summary['avoid'])}</p></div></div><div class="scope-note"><p><strong>입력 범위</strong> · {lines(meta['input_scope'])}</p><p><strong>외부 확인</strong> · {lines(meta['external_research'])}</p><p><strong>분석 기준</strong> · {text(meta['rubric_version'])} / {text(meta['author'])}</p></div>'''
    chapters = [
        ('summary', '01', 'Executive summary', '경영진 요약', exec_body),
        ('scorecard', '02', 'Portfolio assessment', '사업 구조를 한눈에', scorecard(data)),
        ('analysis', '03', 'Business deep dive', '판정의 이유와 핵심 위험', '<div class="exhibit-heading"><div class="exhibit-title">사업별 강점 · 반대 근거 · 다음 행동</div><button type="button" class="quiet-button js-only" id="expand-details" aria-expanded="false">상세 근거 모두 보기</button></div>' + ''.join(detail(v, n) for n, v in enumerate(data['ventures'], 1))),
    ]
    shifts = []
    for v in data['ventures']:
        for tr in v.get('transformations', []):
            shifts.append(f'''<article class="transformation"><div class="exhibit-label">{text(v['name'])} / STRUCTURAL MOVE</div><div class="transition"><div class="transition-side"><div class="eyebrow">AS IS / 현재 구조</div><div class="transition-name">{text(tr['from'])}</div></div><div class="transition-arrow" aria-hidden="true">→</div><div class="transition-side target"><div class="eyebrow">TO BE / 조건부 구조</div><div class="transition-name">{text(tr['to'])}</div></div></div><p class="shift-explanation">{lines(tr['why'])}{refs(tr['evidence'])}</p><div class="conditions-grid"><div><h4>필요한 조건·권리</h4><p>{lines(tr['requirements'])}</p></div><div><h4>추가 비용·운영 부담</h4><p>{lines(tr['cost'])}</p></div><div><h4>전환을 허용할 검증 기준</h4><p>{lines(tr['gate'])}</p></div></div></article>''')
    chapters.append(('redesign', '04', 'Strategic redesign', '기능 추가가 아닌, 구조의 개선', ''.join(shifts) or '<p class="empty-note">근거가 있는 구조 변경안이 아직 없습니다. 네트워크나 마켓플레이스 전환을 억지로 가정하지 않습니다.</p>'))
    exps = []
    names = {v['id']: v['name'] for v in data['ventures']}
    for n, exp in enumerate(data['experiments'], 1):
        exps.append(f'''<article class="experiment"><div class="experiment-header"><div><div class="exhibit-label">EXPERIMENT {n:02d} / {text(names[exp['venture_id']])}</div><h3>{text(exp['title'])}</h3></div><div class="experiment-meta">{text(exp['duration'])} · 제안 실험</div></div><p class="hypothesis">검증할 가설: {lines(exp['hypothesis'])}{refs(exp['evidence'])}</p><p class="method"><strong>대상</strong> · {lines(exp['audience'])}<br><strong>방법</strong> · {lines(exp['method'])}</p><div class="experiment-grid"><div><div class="eyebrow">PASS / 제안 성공 기준</div><p>{lines(exp['success'])}</p></div><div><div class="eyebrow">STOP / 중단·재설계 기준</div><p>{lines(exp['stop'])}</p></div></div><p class="experiment-cost">비용 가정 · {lines(exp['cost'])}</p></article>''')
    roadmap = []
    for phase in data['roadmap']:
        roadmap.append(f'<div class="roadmap-step"><span class="period">{text(phase["period"])}</span><h4>{text(phase["title"])}</h4>{"".join(f"<p>{lines(a)}</p>" for a in phase["actions"])}<p class="gate"><strong>다음 단계 조건</strong><br>{lines(phase["gate"])}{refs(phase["evidence"])}</p></div>')
    plan_body = ''.join(exps) or '<p class="empty-note">실험 설계에 필요한 정보가 부족합니다. 성공·중단 기준을 임의로 채우지 않았습니다.</p>'
    if roadmap:
        plan_body += '<div class="roadmap"><h3 class="roadmap-title">단계별 실행 계획</h3><div class="roadmap-grid">'+''.join(roadmap)+'</div></div>'
    chapters.append(('validation', '05', 'Validation roadmap', '작게 검증하고, 조건부로 확대한다', plan_body))
    budget = data.get('budget')
    if budget:
        totals = budget_totals(budget)
        enough = all(totals[k] >= 10000 for k in ('low', 'high'))
        if enough:
            total_str = compact_money(totals['low']) + ('–' + compact_money(totals['high']) if totals['high'] != totals['low'] else '')
            unit = '만원'
        else:
            total_str = money(totals['low']) + ('–' + money(totals['high']) if totals['high'] != totals['low'] else '')
            unit = '원'
        subtotal_label = '산정 항목 소계' if totals['missing'] else '검증 현금 예산'
        rows = []
        for item in budget['items']:
            multiplier = budget['period_months'] if item['cadence'] == 'monthly' else 1
            cadence = f'월 × {multiplier}' if item['cadence'] == 'monthly' else '일회성'
            low = None if item['low'] is None else item['low']*multiplier
            high = None if item['high'] is None else item['high']*multiplier
            rows.append(f'<tr><td>{text(item["name"])}</td><td>{cadence}</td><td class="number">{money(low)}</td><td class="number">{money(high)}</td><td>{lines(item["note"])}{refs(item["evidence"])}</td></tr>')
        missing_note = f'미산정 항목 {totals["missing"]}개는 위 소계에서 제외했습니다. 전체 필요 예산이 아닙니다.' if totals['missing'] else '표시 금액은 기간 전체의 현금 지출입니다. 월 반복 항목은 기간을 곱해 합산했습니다.'
        exclusions = '<br>'.join(lines(s) for s in budget['exclusions'])
        budget_body = f'''<div class="budget-summary"><div><div class="eyebrow">{text(subtotal_label)}</div><div class="budget-total">{total_str}<small>{unit}</small></div></div><div class="budget-context">{text(budget['title'])}<br>{budget['period_months']}개월 기준 · {text(budget['basis'])}{refs(budget['evidence'])}</div></div><div class="exhibit-heading"><div><div class="exhibit-label">EXHIBIT 02</div><div class="exhibit-title">기간 내 비용 항목과 산정 근거</div></div><small>단위: 원 / KRW</small></div><div class="table-wrap" tabindex="0" role="region" aria-label="검증 예산"><table class="budget-table"><thead><tr><th scope="col">항목</th><th scope="col">산정 방식</th><th scope="col" class="number">하한</th><th scope="col" class="number">상한</th><th scope="col">가정·근거</th></tr></thead><tbody>{''.join(rows)}</tbody><tfoot><tr><td colspan="2">{text(subtotal_label)}</td><td class="number">{money(totals['low'])}</td><td class="number">{money(totals['high'])}</td><td>{'미산정 '+str(totals['missing'])+'개 별도' if totals['missing'] else '현금 기준'}</td></tr></tfoot></table></div><p class="budget-note">{missing_note}<br>세금: {lines(budget['tax_note'])}<br>창업자 노동: {lines(budget['founder_labor'])}</p>{f'<div class="scope-note"><strong>예산 제외 항목·주의사항</strong><br>{exclusions}</div>' if exclusions else ''}'''
    else:
        budget_body = '<p class="empty-note">산정할 예산 자료가 없습니다. 인건비·기간·세금·반복 지출의 범위를 확인한 뒤 별도로 계산해야 합니다.</p>'
    chapters.append(('budget', '06', 'Investment & resources', '예산은 검증 단위로 배분한다', budget_body))
    unknown_body = ''.join(f'<div class="unknown-item"><span class="unknown-index">{i:02d}</span><div><h3>{text(u["question"])}</h3><p>{lines(u["impact"])}</p><p><strong>확인 방법</strong> · {lines(u["next_step"])}</p></div></div>' for i, u in enumerate(data['uncertainties'], 1)) or '<p class="empty-note">추가 질문이 입력되지 않았습니다. 불확실성이 없다는 뜻은 아닙니다.</p>'
    chapters.append(('questions', '07', 'Decision gates', '결론을 바꿀 미확인 질문', unknown_body))
    source_parts = []
    for src in data['sources']:
        link = f'<a class="external-source" href="{text(src["url"])}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer">원문 확인 ↗</a>' if src.get('url') else ''
        source_parts.append(f'<article class="source-item" id="source-{src["id"]}"><div class="source-id">{src["id"]}</div><div><div class="source-title">{text(src["title"])}<span class="source-type">{text(src["type"])}</span></div><div class="source-location">{text(src["date"])} · {lines(src["locator"])}</div><p class="source-text">{lines(src["summary"])}</p>{link}</div></article>')
    limitation_text = [
        'GSR+는 3S 논점에서 영감을 받은 독립 분석 프레임입니다. GSR의 공식 심사표나 투자 의견이 아닙니다.',
        '◎·○·△·×·?는 정성적 구조 판단입니다. 미래 잠재력, 성공 확률, 실제 성과를 서로 대체하지 않습니다.',
        '이 문서는 Venture Evaluator가 생성한 보고서입니다. KPMG·McKinsey가 작성·검토하거나 보증한 자료가 아닙니다.',
    ] + data['limitations']
    appendix = '<p class="sources-intro">본문의 [E번호]는 아래 근거 원장으로 연결됩니다. 관측 · 사용자진술 · 추론 · 가정 · 미확인을 구분하며, 자료 수 자체를 신뢰도 점수로 계산하지 않습니다.</p>' + ''.join(source_parts)
    if not source_parts:
        appendix += '<p class="empty-note">등록된 근거가 없습니다. 모든 판정의 불확실성을 먼저 확인하세요.</p>'
    if data.get('changes'):
        appendix += '<h3 class="roadmap-title">이전 평가 대비 변경</h3><div class="table-wrap"><table class="detail-table"><thead><tr><th>항목</th><th>이전</th><th>이번</th><th>변경 근거</th></tr></thead><tbody>' + ''.join(f'<tr><th scope="row">{text(c["item"])}</th><td>{lines(c["before"])}</td><td>{lines(c["after"])}</td><td>{lines(c["reason"])}{refs(c["evidence"])}</td></tr>' for c in data['changes']) + '</tbody></table></div>'
    appendix += '<div class="limitations"><h3>평가 방법과 한계</h3>' + ''.join(f'<p>{lines(t)}</p>' for t in limitation_text) + '</div>'
    chapters.append(('sources', '08', 'Evidence & methodology', '근거와 평가 방법', appendix))
    nav = '<a class="active" href="#cover" aria-current="location"><span>00</span><span>보고서 표지</span></a>' + ''.join(f'<a href="#{c[0]}"><span>{c[1]}</span><span>{text(label)}</span></a>' for c, label in zip(chapters, ['경영진 요약','GSR+ 비교표','사업별 상세 분석','구조 개선안','검증·실행 계획','예산·자원 배분','미확인 질문','근거·평가 방법']))
    content = cover + ''.join(section(*c) for c in chapters)
    report_title = text(meta['title'].replace('\n', ' '))
    csp = f"default-src 'none'; script-src 'sha256-{digest}'; style-src 'unsafe-inline'; img-src data:; font-src 'none'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"
    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light"><meta name="referrer" content="no-referrer"><meta http-equiv="Content-Security-Policy" content="{text(csp)}"><meta name="generator" content="Venture Evaluator {VERSION}"><title>{report_title} — Venture Evaluator</title><style>{css}</style></head>
<body><a class="skip-link" href="#summary">보고서 본문으로 이동</a><header class="topbar"><a class="brand" href="#cover" aria-label="Venture Evaluator 보고서 표지"><span class="brand-mark" aria-hidden="true"></span><span>VENTURE EVALUATOR</span></a><div class="topbar-meta"><span>{text(meta['classification'])}</span><span>{text(meta['date'].replace('-', '.'))}</span><button id="print-report" type="button" class="js-only">인쇄 / PDF</button></div></header>
<div class="layout"><aside class="rail" aria-label="보고서 목차"><div><div class="rail-label">REPORT CONTENTS</div><nav class="toc">{nav}</nav></div><div class="rail-bottom"><div class="progress-track"><div class="progress-line"></div></div><strong>DECISIONS, NOT PREDICTIONS.</strong>현재의 근거와<br>미래의 가능성을 분리합니다.<br><br>{text(meta['rubric_version'])}<br>Report edition {VERSION}</div></aside><main>{content}<footer class="report-footer"><div><div class="footer-wordmark">VENTURE EVALUATOR</div>Independent venture strategy assessment</div><div>{text(meta['report_id'])} · {text(meta['classification'])}<br>{'가상 데이터 디자인 샘플 · 실제 사업 평가가 아닙니다.' if meta['status']=='sample' else '배포 전 민감 정보와 데이터 사용 권한을 확인하세요.'}</div></footer></main></div><script>{js}</script></body></html>'''


def load_report(path: Path) -> dict:
    require(path.is_file(), f'Input file not found: {path}')
    require(path.stat().st_size <= 10_000_000, 'Input JSON exceeds 10 MB; split the portfolio into smaller reports')
    def reject_constant(value: str) -> None:
        raise ReportError(f'Non-finite JSON value is not allowed: {value}')
    return json.loads(path.read_text(encoding='utf-8-sig'), parse_constant=reject_constant)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path, help='Report JSON; see assets/report.schema.json')
    parser.add_argument('--output', type=Path, help='New standalone .html file. Existing files are never overwritten.')
    parser.add_argument('--validate-only', action='store_true', help='Check data without creating a file')
    args = parser.parse_args(argv)
    if sys.version_info < (3, 9):
        parser.error('Python 3.9 or newer is required')
    if not args.validate_only and args.output is None:
        parser.error('--output is required unless --validate-only is used')
    try:
        data = load_report(args.input.expanduser())
        validate(data)
        if args.validate_only:
            print(f'VALID: {len(data["ventures"])} venture(s), {len(data["sources"])} evidence record(s). Narrative accuracy is not tested.')
            return 0
        output = args.output.expanduser()
        require(output.suffix.lower() in ('.html', '.htm'), 'Output extension must be .html or .htm')
        resolved = output.resolve()
        require(ROOT != resolved and ROOT not in resolved.parents, 'Do not save private reports inside the installed skill folder')
        require(not output.exists() and not output.is_symlink(), f'Output already exists; choose a new filename: {output}')
        html = render(data)
        output.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation also protects against a concurrent overwrite/symlink race.
        with output.open('x', encoding='utf-8') as stream:
            stream.write(html)
        print(f'CREATED: {output.resolve()}')
        print('Standalone HTML. Open locally in a browser. No external assets or background network requests.')
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
