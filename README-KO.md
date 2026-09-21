# Venture Evaluator · Report Edition

**사업계획서나 접근 가능한 사업 대화를 읽고, GSR+ 평가를 흰색 컨설팅 보고서형 HTML로 만드는 스킬**입니다.

최종 결과를 채팅 표로만 보여주지 않고 **브라우저에서 읽는 `.html` + 재생성용 `.json`**으로
만듭니다. 새 서버, Node, 웹서비스 배포 없이 HTML 파일 하나를 열면 됩니다.
작성은 Python 3.9+ 표준 라이브러리 렌더러를 사용하고, 보고서 열람에는 Python이 필요 없습니다.

버전 `1.1.1` · 루브릭 `gsr-plus-1.0` · 설치 문서 확인일 `2026-09-21`

이 패키지는 GSR, Anthropic, OpenAI의 공식 제품이나 투자 심사 도구가 아닙니다.
사용자가 제시한 3S와 사업 논점을 재사용 가능한 자체 분석 지침으로 구성했습니다.

## 1.1.0에서 달라진 것

| 변경 | 내용 |
|---|---|
| 기본 결과 | HTML 보고서 + 재생성용 JSON. `md` / `no-save`로 채팅 출력 선택 가능 |
| 디자인 | 흰 배경, 네이비 제목, 블루 포인트, 큰 타이포, 넓은 여백, 얇은 구분선 |
| 보고서 구성 | 표지 → 경영진 요약 → GSR+ 비교표 → 사업별 분석 → 구조 개선 → 검증·실행 계획 → 예산 → 미확인 → 근거 |
| 탐색 | 목차, 현재/조건부 기호 전환, 기호 클릭으로 상세 근거 이동, 12항목 펼치기 |
| 휴대성 | CSS·JS가 포함된 단일 HTML. 외부 폰트/CDN/추적기/자동 네트워크 요청 없음 |
| 비용 검산 | 월/일회성 지출 구분, 기간별 합산, 미산정 항목과 창업자 노동 별도 표시 |
| 유지된 원칙 | 현재와 미래 구분, 실제 자료의 근거, 미확인 `?`, 기존 파일 보호·업데이트 백업 |

디자인은 컨설팅 보고서의 편집적 분위기를 참고한 **독립 Venture Evaluator 스타일**입니다.
KPMG·McKinsey의 로고·서명·서체 파일은 포함하지 않으며 그 회사가 작성한 보고서가 아닙니다.

### 디자인부터 확인

설치 패키지 안의 `examples/venture-report-sample.html`을 브라우저로 열어보세요.
샘플은 가상 사업 3개와 가정 예산으로만 구성한 디자인 시연입니다. 사용자의 실제 사업에
대한 새로운 평가가 아닙니다. 실제 평가 시 스킬은 제공한 사업계획서·맥락을 읽어 새로 채웁니다.

### 기존 1.0.0 설치본 업데이트

새 `venture-evaluator-kit-v1.1.1.zip`을 풀고 다음을 실행합니다.
압축 안의 폴더명은 이전과 같이 `venture-evaluator-kit`입니다.

```bash
cd ~/Downloads/venture-evaluator-kit
bash install.sh --target both --replace
bash install.sh --action check --target both
```

이전 다운로드와 폴더가 겹치면 **새 ZIP을 별도 위치에 풀어** 그 폴더에서 실행하세요.
수동으로 파일을 섞어 덮어쓰지 마세요. `--replace`는 설치된 기존 스킬을 각각의
`skill-backups/`에 보존한 뒤 교체합니다. 프로젝트 `.venture/`의 사업 자료는 바꾸지 않습니다.

## 무엇을 받게 되나요?

| 서비스 | Significant | Scalable | Sustainable | 고빈도 | 네트워크 효과 | GSR+ 잠재력 |
|---|---|---|---|---|---|---|
| 입력한 사업 | 근거에 따른 기호 | 근거에 따른 기호 | 현재→조건부 | 기호 | 기호 | 조건부 판단 |

`◎ / ○ / △ / × / ?`를 사용하고, `○→◎`를 제시하면 필요한 구조 변화와 검증 조건을
함께 설명합니다. 미래 계획을 현재 실적으로 계산하지 않습니다.

사업별 강점·핵심 위험·구조 개선안, 작은 유료 검증 실험, 예산과 중단 기준까지
연결합니다. `deep` 요청에는 12항목과 근거표를 더합니다.

## 가장 빠른 설치: macOS / Linux의 Claude Code + Codex

다운로드한 `venture-evaluator-kit-v1.1.1.zip`을 풀고, **이 README와 install.sh가 있는 폴더**에서
터미널을 엽니다. 표준 라이브러리만 사용하는 Python 3.9 이상이 필요합니다.

```bash
bash install.sh --target both
```

다운로드 폴더에서 압축을 풀었다면 다음과 같이 실행할 수 있습니다.

```bash
cd ~/Downloads/venture-evaluator-kit
bash install.sh --target both
```

실행 전 동작을 확인하려면:

```bash
bash install.sh --target both --dry-run
```

한쪽만 설치하려면:

```bash
bash install.sh --target claude
bash install.sh --target codex
```

설치 경로:

| 도구 | 개인 설치 경로 |
|---|---|
| Claude Code | `~/.claude/skills/venture-evaluator/` |
| Codex | `~/.agents/skills/venture-evaluator/` |

이 설치기는 스킬 폴더만 복사합니다. 앱 설치·업데이트, 계정 연결, API 결제,
권한 우회, 전역 설정 수정, 대화 수집은 하지 않습니다. `sudo`는 사용하지 마세요.
같은 파일이면 그대로 두고, 기존 파일이 다르면 `--replace` 없이 덮어쓰지 않습니다.

앱에서 보이지 않으면 세션을 다시 열거나 앱을 재시작합니다. 조직의 스킬 제한이나
앱 버전에 따른 차이는 있을 수 있습니다. Codex는 현재 공식 문서의 `.agents/skills`
경로를 사용하며 `.codex/skills`에 중복 설치하지 않습니다.

## Python 없이 직접 설치

처음 설치할 때 `venture-evaluator` 폴더 전체를 아래 위치로 복사해도 됩니다.
`SKILL.md`만 옮기면 상세 참조 파일이 빠집니다.

```text
Claude Code: ~/.claude/skills/venture-evaluator/SKILL.md
Codex:       ~/.agents/skills/venture-evaluator/SKILL.md
```

기존 같은 이름의 폴더가 있으면 덮어쓰지 말고 먼저 백업·비교하세요.
핵심 평가는 Markdown 지침입니다. 제공 렌더러로 같은 디자인의 HTML을 만들 때는 Python 3.9+가
필요합니다. Python이 없는 호스트에서는 쓰기 도구가 허용되면 정적 HTML을 직접 만들고,
쓰기 기능도 없으면 HTML 미생성을 알리고 텍스트로 보고하도록 설계했습니다.

## 특정 프로젝트에만 설치

기존 프로젝트 폴더를 지정합니다. 현재 디렉터리가 어디인지에 의존하지 않습니다.

```bash
python3 install.py --target both --scope project --project "/path/to/my-project"
```

다음 두 위치에 설치됩니다.

```text
/path/to/my-project/.claude/skills/venture-evaluator/
/path/to/my-project/.agents/skills/venture-evaluator/
```

한 호스트에서 같은 이름을 개인/프로젝트에 중복 설치하면 선택·우선순위가
혼동될 수 있으므로 특별한 이유가 없으면 한 가지 설치 범위만 사용하세요.
클라우드 실행은 로컬 홈 폴더를 읽지 못할 수 있으므로 해당 저장소/실행 환경에
스킬과 평가할 문서가 제공돼 있어야 합니다.

## Windows

Python 3.9 이상이 설치되어 있다면 압축을 푼 폴더에서 실행합니다.

```powershell
py -3 install.py --target both
```

Python 런처가 없고 `python` 명령만 있다면 `python install.py --target both`를 사용합니다.
WSL에서 실행하면 WSL 홈에 설치됩니다. Windows 호스트에 설치하려면 Windows에서 실행하세요.
이 배포본의 Windows 실제 앱 로딩은 별도 검증하지 않았습니다.

## Claude 웹/일반 데스크톱에서 사용

웹 업로드에는 설치기 포함 ZIP이 아니라 **`venture-evaluator-v1.1.1.zip`**을 사용합니다.
이 ZIP은 `venture-evaluator/SKILL.md`가 있는 스킬 폴더 하나만 포함합니다.

공식 도움말 확인 기준 절차:

`Customize → Skills → + → Create skill → Upload a skill`

ZIP 업로드 후 활성화합니다. `Code execution and file creation` 설정이 필요하며,
조직 계정에서는 관리자 정책에 따라 업로드가 제한될 수 있습니다.
메뉴 이름이 달라지면 `references/platform-notes.md`의 공식 문서를 확인하세요.

스킬을 올린 뒤 사업계획서나 사업 대화 요약을 **별도로** 제공하고:

> venture-evaluator를 사용해서 첨부한 사업계획서를 GSR+ 기준으로 평가해줘.

라고 요청하면 됩니다. 설치한 스킬에 사용자 사업 내용이 미리 들어 있지는 않습니다.

## 실행 예시

아래 명령은 **터미널 명령이 아니라 Claude Code/Codex의 대화 입력창**에 입력합니다.
실제 파일은 해당 세션에서 접근 가능한 위치에 있어야 합니다.

### Claude Code

```text
/venture-evaluator evaluate 이 프로젝트의 README와 PRD를 읽고 사업을 평가해줘.
```

```text
/venture-evaluator portfolio 이 대화에서 논의한 사업들을 위 표 형식으로 비교해줘.
```

### Codex

```text
$venture-evaluator evaluate 이 프로젝트의 README와 PRD를 읽고 사업을 평가해줘.
```

```text
$venture-evaluator portfolio .venture/venture-context.md brief
```

Codex CLI/IDE에서 `/skills`로 선택할 수도 있습니다. 대화형 자연어로
“venture-evaluator를 사용해 이 사업을 평가해줘”라고 요청하는 방법도 있습니다.

### 공통 요청

```text
venture-evaluator redesign: 현재 사업의 약점을 먼저 보여주고,
고객별 개발 없이 확장하도록 바꾸는 방안을 비교해줘.
```

```text
venture-evaluator validate: 현금 예산 500만원, 내가 개발, 4주 이내.
유료 수요를 확인할 가장 작은 실험과 중단 기준을 잡아줘.
```

```text
venture-evaluator evaluate deep offline:
첨부 자료만으로 평가하고, 최신 경쟁 정보는 확인하지 않았다고 표시해줘.
```

```text
venture-evaluator update:
이전 평가와 이번 달 KPI를 비교하고 달라진 판정의 근거를 설명해줘.
결과를 .venture/evaluations/에 새 파일로 저장해줘.
```

`offline`은 외부 자료 확인을 하지 않는 모드입니다. AI 호스트 자체를 인터넷 없이
실행한다는 의미가 아닙니다. **평가 모드는 HTML+JSON 작성이 기본**입니다.
`context`의 기존 맥락 저장·갱신은 별도 요청이 있어야 합니다. 파일이 필요 없으면
`md` 또는 `no-save`를 요청하세요.

## HTML 보고서 사용

설치 후 Claude Code 대화 입력창에서:

```text
/venture-evaluator portfolio
현재 대화와 지정한 사업 자료를 읽고 최종 보고서를 만들어줘.
흰색 컨설팅 보고서 스타일로 HTML 파일을 생성해줘.
```

Codex 대화 입력창에서:

```text
$venture-evaluator evaluate deep
이 프로젝트의 README와 PRD를 읽고 사업을 평가해줘.
현재 상태, 조건부 개선안, 검증 계획과 예산을 HTML 보고서로 만들어줘.
```

HTML이 기본이므로 매번 디자인을 설명할 필요는 없습니다. 계정 전체 과거 대화를
자동으로 읽지는 않으므로 해당 세션에서 접근할 수 있는 맥락 자료를 제공합니다.
호스트 정책이나 실행 도구에 따라 파일 생성 지원은 달라질 수 있습니다.

### 만들어지는 파일

```text
.venture/reports/
  YYYY-MM-DD-HHMMSS-portfolio.html
  YYYY-MM-DD-HHMMSS-portfolio.json
```

날짜·시간은 실제 생성 시점으로 바뀝니다. HTML 파일을 브라우저로 열면 됩니다.
JSON은 검토 근거·기호·예산을 동일 디자인으로 다시 생성하는 중간 결과물입니다.
둘 다 민감 정보가 들어갈 수 있으므로 공유 전에 내용을 확인하세요.

### 샘플을 직접 다시 생성하기

새로 푼 패키지 루트에서:

```bash
python3 venture-evaluator/scripts/render_report.py \
  --input venture-evaluator/assets/report.sample.json \
  --output ./sample-report-new.html
```

이 명령은 **샘플 JSON을 HTML로 바꾸는 것**입니다. 새 사업 평가를 수행하지는 않습니다.
실제 평가는 스킬을 사용하는 AI가 자료를 읽고 새 JSON을 작성한 뒤 같은 생성기를 사용합니다.
기존 출력 파일이 있으면 다른 이름을 지정하세요. 렌더러는 덮어쓰지 않습니다.

### 기존 평가 JSON으로 보고서 재생성

```bash
python3 ~/.agents/skills/venture-evaluator/scripts/render_report.py \
  --input .venture/reports/my-evaluation.json \
  --output .venture/reports/my-evaluation-revised.html
```

Claude Code 개인 설치 경로는 `~/.claude/skills/venture-evaluator/`입니다.
프로젝트 범위 설치라면 실제 설치 경로를 사용하세요.

### 인쇄·PDF 저장

보고서 오른쪽 위 `인쇄 / PDF`를 누르면 브라우저 인쇄 기능을 사용합니다.
인쇄용 CSS에서 목차·버튼은 숨기고 상세 근거는 펼칩니다. A4, 배율 100%,
브라우저 머리글/바닥글 끄기를 기준으로 보되, 브라우저 미리보기에서 표와 페이지 나눔을
확인하세요. 이번 검증은 인쇄 CSS와 상태 전환까지이며 **실제 PDF 파일의 페이지별 검수는 아닙니다.**

### 자체 테스트

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

50개 설치·렌더러 테스트는 Python 표준 라이브러리만 사용합니다.
선택적 `tests/browser_smoke.py`는 개발 검수용이며 Playwright와 Chromium이 별도로
필요합니다. 정상 설치·보고서 생성·열람에는 Playwright가 필요하지 않습니다.

## 이전 대화를 활용하는 방법

**설치만으로 ChatGPT·Claude·Codex의 모든 과거 대화를 자동 조회하지는 않습니다.**
현재 보이는 대화, 사용자가 제공한 요약/내보내기 파일, 호스트가 실제 접근 가능한
검색 결과만 활용합니다. 숨김 로그나 계정 저장소를 뒤지는 기능은 없습니다.

기존 대화에서 다음 요청으로 이식할 맥락을 만드세요.

```text
지금까지 논의한 사업들을 venture-context.md로 정리해줘.
내가 채택한 결정과 AI가 제안했을 뿐인 아이디어를 구별하고,
실적을 확인하지 못한 숫자는 미확인으로 남겨줘.
```

그 파일을 새 세션에 첨부하거나 현재 프로젝트의 `.venture/venture-context.md`로 두세요.
Claude Code와 Codex가 **같은 폴더를 열 때** 같은 맥락을 읽을 수 있습니다.
다른 앱·기기·클라우드에 자동 동기화되는 것은 아닙니다.

### 빈 작업 공간 만들기 — 선택 사항

설치 여부와 관계없이 배포 폴더에서 실행할 수 있습니다.

```bash
python3 venture-evaluator/scripts/init_workspace.py --project "/path/to/my-project"
```

또는 설치된 스킬에 요청합니다.

```text
/venture-evaluator init 이 프로젝트에 사업 평가용 빈 작업 공간을 만들어줘.
```

다음 구조를 만듭니다. 기존 파일은 보존합니다.

```text
.venture/
  README.md
  business-input.md
  venture-context.md
  .gitignore
  sources/
  projects/
  evaluations/
  reports/
```

`.gitignore`는 새로 만든 민감 자료가 실수로 Git에 추가되는 것을 줄이는 기본값입니다.
이미 추적 중인 파일에는 적용되지 않으므로 공유 전에는 직접 내용을 확인하세요.

## 확인 · 업데이트 · 제거

```bash
# 설치 파일 및 무결성 확인 — 모델 출력의 품질 검사는 아님
bash install.sh --action check --target both

# 기존 버전을 보존한 뒤 교체
bash install.sh --target both --replace

# 제거도 삭제 대신 백업 폴더로 이동
bash install.sh --action uninstall --target both
```

백업 위치는 각각 `~/.claude/skill-backups/`, `~/.agents/skill-backups/`입니다.
프로젝트 범위에서는 해당 프로젝트의 같은 상대경로를 사용합니다.
제거는 설치기가 만든 표시 파일이 있는 복사본에만 적용됩니다.
직접 복사하거나 웹에 업로드한 스킬은 해당 경로/UI에서 직접 관리하세요.

## 파일 구성

```text
venture-evaluator-kit/
  README-KO.md
  install.sh
  install.py
  TEST-REPORT.md
  CHANGELOG.md
  examples/venture-report-sample.html
  tests/
  venture-evaluator/
    SKILL.md
    LICENSE
    agents/openai.yaml
    references/
      rubric.md
      evidence-policy.md
      output-format.md
      context-workflow.md
      validation-budget.md
      examples.md
      platform-notes.md
      html-report.md
    assets/
      venture-context.template.md
      business-input.template.md
      workspace-readme.template.md
      report.schema.json
      report.template.json
      report.sample.json
      report/report.css
      report/report.js
    scripts/
      init_workspace.py
      render_report.py
    evals/evals.json
    evals/html-evals.json
```

`evals/evals.json`은 모델 결과를 점검할 12개 회귀 테스트 사례이고,
`evals/html-evals.json`에는 HTML 보고서 관련 6개 추가 시나리오가 있습니다.
테스트 사례가 포함돼 있다는 뜻이지 실제 Claude/Codex의 답변 검증을 완료했다는 뜻은 아닙니다.
실제로 실행한 파일·설치기 검사는 `TEST-REPORT.md`에 적었습니다.

## 한계와 데이터 처리

이 스킬 자체는 별도 API 키·서버·구독을 요구하지 않습니다. 실행하는 Claude/Codex의
이용 조건·모델 사용량은 별개입니다. PDF/DOCX/PPTX 등 읽기는 호스트의 지원 기능에
의존하며 별도 문서 파서를 패키지에 넣지 않았습니다.

파일이 로컬에 있다고 해서 모델 처리까지 로컬인 것은 아닙니다. 선택한 호스트의
데이터 처리 정책·권한을 확인하고 민감 정보는 최소화하세요.
이 스킬은 점수 체계를 제공하지만 같은 자료에 대한 모델의 판단이 항상 같다고
보장하지 않으며, 사업 성공이나 투자 수익도 보장하지 않습니다.

설치 근거 및 공식 문서는 `venture-evaluator/references/platform-notes.md`에 있습니다.
