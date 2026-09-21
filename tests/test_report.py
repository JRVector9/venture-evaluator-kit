"""Offline renderer regression tests. No models, network, or optional packages."""
import copy
import importlib.util
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

KIT = Path(__file__).resolve().parents[1]
SKILL = KIT / 'venture-evaluator'
SCRIPT = SKILL / 'scripts/render_report.py'
spec = importlib.util.spec_from_file_location('venture_report_renderer', SCRIPT)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
SAMPLE = json.loads((SKILL / 'assets/report.sample.json').read_text(encoding='utf-8'))


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.ids = []
        self.hrefs = []
        self.scripts = []
        self.loads = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a' and 'href' in attrs:
            self.hrefs.append(attrs['href'])
        if tag == 'script':
            self.scripts.append(attrs)
        if tag in ('script', 'img', 'iframe', 'link', 'source'):
            self.loads.append((tag, attrs))


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.data = copy.deepcopy(SAMPLE)

    def test_sample_and_empty_template_validate(self):
        renderer.validate(self.data)
        template = json.loads((SKILL / 'assets/report.template.json').read_text(encoding='utf-8'))
        renderer.validate(template)
        self.assertIn('INPUT TEMPLATE', renderer.render(template))

    def test_sample_is_clearly_labeled(self):
        html = renderer.render(self.data)
        self.assertIn('DESIGN SAMPLE', html)
        self.assertIn('실제 사업 평가가 아닙니다', html)

    def test_assessment_does_not_inherit_demo_banner(self):
        self.data['meta']['status'] = 'assessment'
        html = renderer.render(self.data)
        self.assertNotIn('DESIGN SAMPLE', html)
        self.assertIn('배포 전 민감 정보', html)

    def test_all_evidence_anchors_exist_and_ids_unique(self):
        doc = Document(renderer.render(self.data))
        self.assertEqual(len(doc.ids), len(set(doc.ids)))
        for href in doc.hrefs:
            if href.startswith('#'):
                self.assertIn(href[1:], doc.ids)
        self.assertEqual(sum(i.startswith('source-') for i in doc.ids), 5)

    def test_no_remote_assets_or_dynamic_imports(self):
        html = renderer.render(self.data)
        doc = Document(html)
        self.assertEqual(len(doc.scripts), 1)
        self.assertFalse(any('src' in attrs or 'href' in attrs for _, attrs in doc.loads))
        for token in ('fetch(', 'XMLHttpRequest', 'sendBeacon', '@import', '@font-face', 'localStorage'):
            self.assertNotIn(token, html)
        self.assertIn("connect-src &#x27;none&#x27;", html)

    def test_user_html_is_escaped(self):
        attack = '<script>alert("XSS")</script><img src=x onerror=alert(1)>'
        self.data['summary']['thesis'] = attack
        self.data['meta']['title'] = attack
        self.data['sources'][0]['summary'] = attack
        html = renderer.render(self.data)
        self.assertNotIn(attack, html)
        self.assertIn('&lt;script&gt;', html)
        self.assertEqual(len(Document(html).scripts), 1)

    def test_unsafe_source_schemes_rejected(self):
        for url in ('javascript:alert(1)', 'data:text/html,test', 'file:///etc/passwd', '//example.com/a'):
            with self.subTest(url=url):
                self.data['sources'][0]['url'] = url
                with self.assertRaises(renderer.ReportError):
                    renderer.validate(self.data)

    def test_credential_and_control_urls_rejected(self):
        for url in ('https://user:password@example.com', 'https://example.com/\nfoo', 'https://exa mple.com'):
            with self.subTest(url=url):
                self.data['sources'][0]['url'] = url
                with self.assertRaises(renderer.ReportError):
                    renderer.validate(self.data)

    def test_https_source_with_escaped_query(self):
        self.data['sources'][0]['url'] = 'https://example.com/?a=1&b=2'
        html = renderer.render(self.data)
        self.assertIn('https://example.com/?a=1&amp;b=2', html)
        self.assertIn('rel="noopener noreferrer"', html)

    def test_invalid_rating_rejected(self):
        self.data['ventures'][0]['ratings']['scalable']['current'] = '100%'
        with self.assertRaises(renderer.ReportError):
            renderer.validate(self.data)

    def test_future_rating_requires_condition(self):
        self.data['ventures'][0]['ratings']['sustainable']['condition'] = ''
        with self.assertRaises(renderer.ReportError):
            renderer.validate(self.data)

    def test_known_rating_requires_evidence(self):
        self.data['ventures'][0]['ratings']['scalable']['evidence'] = []
        with self.assertRaises(renderer.ReportError):
            renderer.validate(self.data)

    def test_trailing_newline_in_ids_rejected(self):
        # "E1\n" passed re.search and produced a broken id="source-E1\n" in the HTML.
        # The id and every reference to it are renamed together so only the pattern check can reject it.
        for old in (self.data['sources'][0]['id'], self.data['ventures'][0]['id']):
            with self.subTest(id=old):
                raw = json.dumps(self.data, ensure_ascii=False).replace(f'"{old}"', f'"{old}\\n"')
                with self.assertRaises(renderer.ReportError):
                    renderer.validate(json.loads(raw))

    def test_missing_evidence_reference_rejected(self):
        self.data['summary']['recommendations'][0]['evidence'] = ['E999']
        with self.assertRaises(renderer.ReportError):
            renderer.validate(self.data)

    def test_duplicate_source_ids_rejected(self):
        self.data['sources'].append(copy.deepcopy(self.data['sources'][0]))
        with self.assertRaises(renderer.ReportError):
            renderer.validate(self.data)

    def test_duplicate_venture_ids_rejected(self):
        self.data['ventures'][1]['id'] = self.data['ventures'][0]['id']
        with self.assertRaises(renderer.ReportError):
            renderer.validate(self.data)

    def test_orphan_experiment_rejected(self):
        self.data['experiments'][0]['venture_id'] = 'not-in-report'
        with self.assertRaises(renderer.ReportError):
            renderer.validate(self.data)

    def test_bad_date_rejected(self):
        self.data['meta']['date'] = '2026-02-30'
        with self.assertRaises(renderer.ReportError):
            renderer.validate(self.data)

    def test_host_only_citation_rejected(self):
        self.data['summary']['thesis'] = '사실 citeturn0search0'
        with self.assertRaises(renderer.ReportError):
            renderer.validate(self.data)

    def test_unknown_field_rejected(self):
        self.data['success_probability'] = 99
        with self.assertRaises(renderer.ReportError):
            renderer.validate(self.data)

    def test_budget_period_and_totals(self):
        self.assertEqual(renderer.budget_totals(self.data['budget']), {'low': 3000000, 'high': 6000000, 'missing': 0})
        self.data['budget']['period_months'] = 3
        self.assertEqual(renderer.budget_totals(self.data['budget']), {'low': 3400000, 'high': 6800000, 'missing': 0})
        html = renderer.render(self.data)
        self.assertIn('월 × 3', html)
        self.assertIn('3,400,000', html)

    def test_unknown_budget_not_treated_as_zero(self):
        self.data['budget']['items'][0]['high'] = None
        html = renderer.render(self.data)
        self.assertIn('산정 항목 소계', html)
        self.assertIn('미산정 항목 1개', html)
        self.assertEqual(renderer.budget_totals(self.data['budget'])['low'], 1800000)

    def test_invalid_budget_values_rejected(self):
        for low, high in ((-1, 2), (20, 10), (True, 100), (1.2, 4)):
            with self.subTest(low=low, high=high):
                self.data['budget']['items'][0]['low'] = low
                self.data['budget']['items'][0]['high'] = high
                with self.assertRaises(renderer.ReportError):
                    renderer.validate(self.data)

    def test_budget_optional(self):
        del self.data['budget']
        self.assertIn('산정할 예산 자료가 없습니다', renderer.render(self.data))

    def test_missing_extended_dimensions_are_unknown(self):
        del self.data['ventures'][0]['ratings']['retention']
        html = renderer.render(self.data)
        self.assertIn('이 항목을 판정할 자료가 제공되지 않았습니다', html)
        self.assertIn('criterion-workflow-a-retention', html)

    def test_single_venture_without_optional_sections(self):
        self.data['ventures'] = self.data['ventures'][:1]
        self.data['experiments'] = []
        self.data['roadmap'] = []
        self.data['ventures'][0]['transformations'] = []
        self.assertIn('1개 사업', renderer.render(self.data))

    def test_change_log_rendered(self):
        self.data['changes'] = [{'item':'지속가능성','before':'미확인','after':'미확인','reason':'새 관측 자료 없음','evidence':['E4']}]
        self.assertIn('이전 평가 대비 변경', renderer.render(self.data))

    def test_report_renders_same_bytes(self):
        self.assertEqual(renderer.render(self.data), renderer.render(self.data))

    def test_cli_output_unicode_and_non_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / '한글 보고서' / 'report.html'
            args = [sys.executable, str(SCRIPT), '--input', str(SKILL / 'assets/report.sample.json'), '--output', str(out)]
            result = subprocess.run(args, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            original = out.read_bytes()
            result = subprocess.run(args, text=True, capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(original, out.read_bytes())

    def test_validate_only_writes_nothing(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'not-created.html'
            result = subprocess.run([sys.executable, str(SCRIPT), '--input', str(SKILL / 'assets/report.sample.json'), '--validate-only', '--output', str(out)], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(out.exists())

    def test_render_inside_skill_rejected(self):
        out = SKILL / 'should-never-be-created.html'
        result = subprocess.run([sys.executable, str(SCRIPT), '--input', str(SKILL / 'assets/report.sample.json'), '--output', str(out)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(out.exists())

    def test_nonfinite_json_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'bad.json'
            path.write_text('{"test": NaN}')
            with self.assertRaises(renderer.ReportError):
                renderer.load_report(path)

    def test_no_font_binaries_packaged(self):
        fonts = [p for p in KIT.rglob('*') if p.suffix.lower() in ('.ttf','.otf','.woff','.woff2','.ttc')]
        self.assertEqual(fonts, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
