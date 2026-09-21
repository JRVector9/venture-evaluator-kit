# Venture Evaluator · Report Edition

**사업계획서나 접근 가능한 사업 대화를 읽고, GSR+ 평가를 흰색 컨설팅 보고서형 HTML로 만드는 스킬**입니다.
Claude Code와 Codex에서 쓸 수 있습니다.

최종 결과를 채팅 표로만 보여주지 않고 **브라우저에서 읽는 `.html` + 재생성용 `.json`**으로
만듭니다. 새 서버, Node, 웹서비스 배포 없이 HTML 파일 하나를 열면 됩니다.
작성은 Python 3.9+ 표준 라이브러리 렌더러를 사용하고, 보고서 열람에는 Python이 필요 없습니다.

버전 `1.1.2` · 루브릭 `gsr-plus-1.0` · 설치 문서 확인일 `2026-09-21`

이 패키지는 GSR, Anthropic, OpenAI의 공식 제품이나 투자 심사 도구가 아닙니다.
사용자가 제시한 3S와 사업 논점을 재사용 가능한 자체 분석 지침으로 구성했습니다.

## 설치

### 가장 쉬운 방법: 설치 프롬프트 붙여 넣기

아래 문장을 **복사해서 Claude Code 또는 Codex 대화 입력창에 그대로 붙여 넣으면**, 에이전트가
저장소를 받아 설치까지 진행합니다. Python 3.9 이상과 git이 있으면 가장 빠릅니다.

**Claude Code**

```text
venture-evaluator 스킬을 설치해줘.
1. 임시 폴더에 받는다: git clone --depth 1 --branch v1.1.2 https://github.com/JRVector9/venture-evaluator-kit.git
2. 받은 폴더에서 python3 install.py --target claude --dry-run 을 실행해 설치될 위치를 보여준다.
3. python3 install.py --target claude 로 설치한다. "Existing skill differs"가 나오면 --replace 를 붙여 다시 실행한다. 기존 버전은 ~/.claude/skill-backups/ 에 보관된다.
4. python3 install.py --action check --target claude 결과를 알려주고, 임시 폴더를 지운다.
Python 3.9 이상이 없으면 받은 폴더의 venture-evaluator 폴더를 ~/.claude/skills/ 아래에 통째로 복사한다.
```

**Codex**

```text
venture-evaluator 스킬을 설치해줘.
1. 임시 폴더에 받는다: git clone --depth 1 --branch v1.1.2 https://github.com/JRVector9/venture-evaluator-kit.git
2. 받은 폴더에서 python3 install.py --target codex --dry-run 을 실행해 설치될 위치를 보여준다.
3. python3 install.py --target codex 로 설치한다. "Existing skill differs"가 나오면 --replace 를 붙여 다시 실행한다. 기존 버전은 ~/.agents/skill-backups/ 에 보관된다.
4. python3 install.py --action check --target codex 결과를 알려주고, 임시 폴더를 지운다.
Python 3.9 이상이 없으면 받은 폴더의 venture-evaluator 폴더를 ~/.agents/skills/ 아래에 통째로 복사한다.
```

두 도구를 모두 쓴다면 어느 쪽에서든 `--target claude` / `--target codex`를 `--target both`로 바꾸면 됩니다.
설치가 끝나면 **새 세션을 열고** Claude Code에서는 `/venture-evaluator`, Codex에서는 `$venture-evaluator`로 부릅니다.

프롬프트는 에이전트가 GitHub에서 파일을 받아 설치 스크립트를 실행하게 합니다. 에이전트가 명령 실행 권한을
물으면 내용을 확인하고 승인하세요. 설치 스크립트는 스킬 폴더를 복사할 뿐, 앱 설정 변경·계정 연결·대화 수집·
`sudo`를 하지 않습니다.

### 직접 설치 (터미널)

```bash
git clone --depth 1 --branch v1.1.2 https://github.com/JRVector9/venture-evaluator-kit.git
cd venture-evaluator-kit
bash install.sh --target both          # Claude Code만: --target claude / Codex만: --target codex
bash install.sh --action check --target both
```

- git이 없으면 GitHub 페이지의 **Code → Download ZIP**으로 받아 푼 폴더에서 같은 명령을 실행합니다.
- 실행 전에 무엇이 바뀌는지 보려면 `--dry-run`을 붙입니다.
- 이미 설치돼 있고 내용이 다르면 설치기가 멈춥니다. `--replace`를 붙이면 기존 버전을 백업한 뒤 교체합니다.
- Windows: `py -3 install.py --target both` (Python 런처가 없으면 `python install.py --target both`).
  WSL에서 실행하면 WSL 홈에 설치됩니다. Windows 앱에서의 실제 로딩은 별도로 검증하지 않았습니다.

설치 위치:

| 도구 | 개인 설치 경로 |
|---|---|
| Claude Code | `~/.claude/skills/venture-evaluator/` |
| Codex | `~/.agents/skills/venture-evaluator/` |

앱에서 보이지 않으면 세션을 다시 열거나 앱을 재시작합니다. 조직의 스킬 제한이나 앱 버전에 따라
차이가 있을 수 있습니다. Codex는 현재 공식 문서의 `.agents/skills` 경로를 사용합니다.

**Python 없이 설치:** `venture-evaluator` 폴더 전체를 위 경로로 복사해도 됩니다. `SKILL.md`만 옮기면
참조 파일이 빠집니다. 같은 이름의 폴더가 있으면 덮어쓰지 말고 먼저 백업하세요. 이 경우 평가 지침은
그대로 쓸 수 있지만, 보고서 HTML은 에이전트가 직접 작성하거나 Markdown으로 대신 보고합니다.

**특정 프로젝트에만 설치:**

```bash
python3 install.py --target both --scope project --project "/path/to/my-project"
```

`/path/to/my-project/.claude/skills/`와 `/path/to/my-project/.agents/skills/`에 설치됩니다.
같은 이름을 개인·프로젝트에 중복 설치하면 선택이 혼동될 수 있으니 한 가지 범위만 쓰세요.
클라우드 실행 환경은 로컬 홈 폴더를 읽지 못할 수 있으므로 그 환경에 스킬과 평가 자료가 있어야 합니다.

### Claude 웹 / 데스크톱 앱

웹에는 스킬 폴더만 담은 **[`venture-evaluator-v1.1.2.zip`](https://github.com/JRVector9/venture-evaluator-kit/releases/download/v1.1.2/venture-evaluator-v1.1.2.zip)**을 올립니다.

`Customize → Skills → + → Create skill → Upload a skill`

ZIP 업로드 후 활성화합니다. `Code execution and file creation` 설정이 필요하며, 조직 계정에서는
관리자 정책에 따라 업로드가 제한될 수 있습니다. 메뉴 이름이 달라지면
`venture-evaluator/references/platform-notes.md`의 공식 문서를 확인하세요.
스킬을 올린 뒤 사업계획서나 사업 대화 요약을 **따로** 첨부하고 평가를 요청합니다.

### 업데이트 · 확인 · 제거

새 버전을 받은 폴더에서:

```bash
bash install.sh --target both --replace        # 기존 버전을 백업한 뒤 교체
bash install.sh --action check --target both   # 설치 파일 무결성 확인 (모델 출력 품질 검사는 아님)
bash install.sh --action uninstall --target both   # 삭제 대신 백업 폴더로 이동
```

백업 위치는 `~/.claude/skill-backups/`, `~/.agents/skill-backups/`입니다. 제거는 설치기가 만든
표시 파일이 있는 복사본에만 적용됩니다. 직접 복사하거나 웹에 올린 스킬은 해당 경로·화면에서 관리하세요.

## 사용법

### 기본 형식

```text
/venture-evaluator [모드] [옵션...] 요청 내용     ← Claude Code
$venture-evaluator [모드] [옵션...] 요청 내용     ← Codex
```

아래 명령은 **터미널이 아니라 Claude Code/Codex의 대화 입력창**에 입력합니다.
모드와 옵션은 생략할 수 있고, 생략하면 `evaluate` · `founder` 관점 · HTML 보고서로 동작합니다.
“venture-evaluator를 사용해서 이 사업을 평가해줘”처럼 자연어로 요청해도 됩니다.
Codex CLI/IDE에서는 `/skills`로 골라도 됩니다.

### 모드

| 모드 | 언제 쓰나 | 결과 |
|---|---|---|
| `evaluate` (기본) | 사업 하나를 평가할 때 | 비교표 1행, 강점·위험, 개선안, 가장 작은 검증 실험 |
| `portfolio` | 여러 사업·아이디어를 같은 기준으로 비교할 때 | 사업별 1행 비교표와 사업별 분석 |
| `redesign` | 약점을 먼저 보고 구조를 바꾸는 방안이 필요할 때 | 현재 평가 + 구조 변경안 최대 3개 |
| `validate` | 돈·시간을 쓰기 전에 핵심 가설을 확인하고 싶을 때 | 실험, 성공·중단 기준, 예산 |
| `update` | 이전 평가 이후 새 자료(KPI 등)가 생겼을 때 | 이전 대비 바뀐 판정과 그 근거 |
| `context` | 긴 대화·자료를 다른 세션으로 옮길 맥락 파일로 정리할 때 | `venture-context.md` 초안 (저장은 요청할 때만) |
| `init` | 프로젝트에 평가용 빈 폴더 구조를 만들 때 | `.venture/` 폴더와 빈 템플릿 |

### 옵션

| 옵션 | 뜻 |
|---|---|
| `founder` (기본) / `investor` | 창업자 관점(구조 개선 중심) / 투자 검토 관점(반대 근거·실사 질문 중심) |
| `brief` / `deep` | 표와 핵심만 / 12항목 근거표·실험·예산까지 |
| `offline` | 웹 검색 등 외부 확인을 하지 않습니다. 최신 정보는 “최신 확인 안 됨”으로 표시합니다. AI 앱 자체를 인터넷 없이 쓴다는 뜻은 아닙니다. |
| `html` (기본) / `md` / `no-save` | HTML + JSON 파일 / Markdown 출력 / 파일 없이 대화로만 |

### 평가 자료 주는 법

- README, PRD, 사업계획서, KPI 파일처럼 읽을 자료의 경로를 요청에 적습니다.
- PDF·DOCX 등은 사용하는 앱이 읽을 수 있어야 합니다. 읽지 못하면 스킬이 텍스트로 달라고 요청하고, 내용을 추측하지 않습니다.
- 자료가 없어도 한두 줄 설명으로 1차 평가를 받을 수 있습니다. 판단할 근거가 없는 항목은 `?`로 남습니다.
- 스킬은 지정하지 않은 다른 폴더나 계정의 과거 대화를 스스로 찾아 읽지 않습니다.

### 결과 읽는 법

| 기호 | 뜻 |
|---|---|
| ◎ | 강한 구조이고 구체적인 근거가 있음 |
| ○ | 유리하지만 검증할 조건이 남음 |
| △ | 근거가 있는 약점 또는 구조적 위험 |
| × | 구조적으로 맞지 않거나 반증이 있음 |
| ? | 판단할 근거가 부족함 (약하다는 뜻이 아님) |

- `△→○`처럼 화살표가 있으면 오른쪽은 **조건을 충족했을 때의 가설**입니다. 조건은 보고서의 12개 항목 상세에 적혀 있습니다.
- 마지막 열 **GSR+ 잠재력**은 `높음(조건부)` / `중간(검증 필요)` / `제한적(현금흐름형)` / `판단 보류` 중 하나이며, 성공 확률이나 투자 의견이 아닙니다.
- 본문의 `[E1]` 같은 표시를 누르면 보고서 끝의 근거 목록으로 이동합니다. 근거마다 관측 · 사용자진술 · 추론 · 가정 · 미확인 중 무엇인지 표시됩니다.

## 사용 예

아래는 Claude Code 기준입니다. Codex에서는 `/venture-evaluator` 대신 `$venture-evaluator`로 시작합니다.

### 1. 사업계획서 하나 평가하기

```text
/venture-evaluator evaluate docs/사업계획서.pdf와 README.md를 읽고 평가해줘.
```

비교표 1행, 강한 이유와 핵심 위험, 가장 먼저 해 볼 검증 실험이 담긴 HTML 보고서가 만들어집니다.

### 2. 아이디어 여러 개 비교하기

```text
/venture-evaluator portfolio brief
1) 동네 세탁소 예약 앱  2) 소규모 팀 납품 요청 관리 SaaS  3) 파일 형식 변환 유틸리티
한 줄 설명뿐이니 모르는 항목은 ?로 남겨줘.
```

사업별 1행 비교표가 나옵니다. 잠재력과 지금 실행하기 좋은 순서는 따로 표시합니다.

### 3. 투자자 관점으로 약점 찾기

```text
/venture-evaluator evaluate investor deep
첨부한 IR 자료를 읽고 반대 근거와 실사 질문을 정리해줘.
```

### 4. 돈을 쓰기 전에 검증 계획 세우기

```text
/venture-evaluator validate
현금 예산 500만원, 개발은 내가 직접, 4주 안에.
유료 수요를 확인할 가장 작은 실험과 중단 기준을 잡아줘.
```

가설, 대상·기간, 성공·중단 기준, 일회성·월 반복 비용을 나눈 예산표가 나옵니다.
창업자 본인의 노동 시간은 0원으로 숨기지 않고 따로 적습니다.

### 5. 구조 바꾸기

```text
/venture-evaluator redesign
지금은 고객마다 맞춤 개발을 하고 있어. 맞춤 개발 없이 확장하는 방안을 비교해줘.
```

### 6. 한 달 뒤 다시 평가하기

```text
/venture-evaluator update
.venture/reports/에 있는 지난 평가 JSON과 이번 달 KPI.csv를 비교해서 달라진 판정의 근거를 설명해줘.
```

새 근거가 없으면 판정을 억지로 바꾸지 않고 그 사실을 적습니다.

### 7. 외부 조사 없이 첨부 자료만으로

```text
/venture-evaluator evaluate deep offline
첨부 자료만으로 평가하고, 최신 경쟁 정보는 확인하지 않았다고 표시해줘.
```

### 8. 긴 대화를 맥락 파일로 옮기기

```text
/venture-evaluator context
이 대화에서 내가 채택한 결정과 AI가 제안만 한 아이디어를 구분해서 정리해줘.
확인되지 않은 숫자는 미확인으로 남기고, .venture/venture-context.md에 저장해줘.
```

### 9. 파일 없이 대화로만

```text
/venture-evaluator evaluate brief no-save
한 줄 아이디어: 반려견 산책 대행 구독 서비스.
```

## 만들어지는 파일

```text
.venture/reports/
  YYYY-MM-DD-HHMMSS-<사업 또는 portfolio>.html
  YYYY-MM-DD-HHMMSS-<사업 또는 portfolio>.json
```

HTML 파일을 브라우저로 열면 됩니다. 외부 폰트·CDN·추적기가 없는 단일 파일이라 인터넷 없이도 열립니다.
JSON은 같은 디자인으로 보고서를 다시 만들 때 쓰는 원본 데이터입니다. 둘 다 민감 정보가 들어갈 수 있으니
공유 전에 내용을 확인하세요. 기존 파일은 덮어쓰지 않고 새 이름으로 만듭니다.

JSON을 고친 뒤 보고서를 다시 만들려면:

```bash
python3 ~/.claude/skills/venture-evaluator/scripts/render_report.py \
  --input .venture/reports/my-evaluation.json \
  --output .venture/reports/my-evaluation-revised.html
```

Codex 설치라면 `~/.agents/skills/venture-evaluator/`, 프로젝트 범위 설치라면 실제 설치 경로를 쓰세요.

**인쇄·PDF:** 보고서 오른쪽 위 `인쇄 / PDF`를 누르면 브라우저 인쇄 기능을 씁니다. 인쇄할 때는 목차·버튼을
숨기고 상세 근거를 펼칩니다. A4, 배율 100%, 머리글/바닥글 끄기를 기준으로 미리보기에서 페이지 나눔을 확인하세요.

## 이전 대화를 활용하는 방법

**설치만으로 ChatGPT·Claude·Codex의 모든 과거 대화를 자동으로 읽지는 않습니다.**
현재 보이는 대화, 사용자가 제공한 요약·내보내기 파일, 호스트가 실제로 접근할 수 있는 검색 결과만 씁니다.

기존 대화에서 사용 예 8번(`context`)으로 `venture-context.md`를 만든 뒤, 새 세션에 첨부하거나 프로젝트의
`.venture/venture-context.md`로 두세요. Claude Code와 Codex가 **같은 폴더를 열 때** 같은 맥락을 읽을 수 있습니다.
다른 앱·기기·클라우드에 자동으로 동기화되지는 않습니다.

평가용 빈 폴더 구조가 필요하면 `/venture-evaluator init 이 프로젝트에 사업 평가용 빈 작업 공간을 만들어줘.`라고
요청합니다. `.venture/` 아래에 템플릿과 `reports/` 등 하위 폴더를 만들고, 기존 파일은 보존합니다.
함께 만드는 `.venture/.gitignore`는 민감 자료가 실수로 Git에 들어가는 것을 줄이는 기본값입니다.

## 한계와 데이터 처리

이 스킬 자체는 별도 API 키·서버·구독을 요구하지 않습니다. 실행하는 Claude/Codex의
이용 조건·모델 사용량은 별개입니다. PDF/DOCX/PPTX 등 읽기는 호스트의 지원 기능에
의존하며 별도 문서 파서를 패키지에 넣지 않았습니다.

파일이 로컬에 있다고 해서 모델 처리까지 로컬인 것은 아닙니다. 선택한 호스트의
데이터 처리 정책·권한을 확인하고 민감 정보는 최소화하세요.
이 스킬은 점수 체계를 제공하지만 같은 자료에 대한 모델의 판단이 항상 같다고
보장하지 않으며, 사업 성공이나 투자 수익도 보장하지 않습니다.

## 파일 구성

```text
venture-evaluator-kit/
  README.md
  LICENSE
  install.py            설치·확인·제거 (Python 3.9+ 표준 라이브러리)
  install.sh            install.py 실행용 래퍼
  venture-evaluator/    실제로 설치되는 스킬 폴더
    SKILL.md
    LICENSE
    agents/openai.yaml
    references/         평가 기준·근거 규칙·출력 형식·HTML 계약 등
    assets/             보고서 스키마·템플릿·CSS/JS
    scripts/            render_report.py, init_workspace.py
```

MIT License.
