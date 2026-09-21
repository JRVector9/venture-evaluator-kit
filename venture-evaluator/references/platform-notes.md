# 플랫폼 참고 · 확인일 2026-09-21

이 파일은 설치·호출 형식의 출처를 기록한다. 사업 평가 사실의 출처가 아니다.
계정 정책·버전에 따라 UI와 로딩 방식은 달라질 수 있다.

## 공식 문서

| 항목 | 확인한 내용 | 원문 |
|---|---|---|
| Agent Skills 규격 | SKILL.md, name/description, 상대경로 자료 구성 | `https://agentskills.io/specification` |
| Claude Code | 개인 ~/.claude/skills, 프로젝트 .claude/skills, /skill-name 호출 | `https://code.claude.com/docs/en/skills` |
| Codex | 개인 ~/.agents/skills, 프로젝트 .agents/skills, $ 이름 또는 /skills 선택 | `https://developers.openai.com/codex/skills` |
| OpenAI 문서 이동 대상 | 확인 시 Build skills 페이지로 연결됨 | `https://learn.chatgpt.com/docs/build-skills` |
| Claude 업로드 | 스킬 폴더를 루트로 가진 ZIP 구성 | `https://support.claude.com/en/articles/12512198-how-to-create-custom-skills` |
| Claude UI | Customize > Skills > Create skill > Upload a skill, 코드 실행 설정 | `https://support.claude.com/en/articles/12512180-use-skills-in-claude` |

Codex 설치기는 현재 문서의 `.agents/skills` 경로를 사용한다. 예전 예시에서
보이는 `.codex/skills`에 중복 설치하지 않는다. 다른 경로를 요구하는 구버전이나
조직 설정에서는 해당 환경 문서/관리자 설정을 확인한다.

Claude Code 로컬 설치와 Claude 웹 업로드는 같은 파일을 사용하는 별도 방법이다.
로컬 설치만으로 웹 업로드가 완료되는 것은 아니다. 클라우드 실행은 로컬 디스크를
읽을 수 없을 수 있으므로 프로젝트 스킬과 자료가 그 환경에도 제공돼야 한다.

Python 3.9+는 설치·초기화·HTML 렌더러에 사용한다. 추가 pip 패키지는 필요 없다.
HTML 보고서는 단일 파일이며 보고서를 열 때 Python이나 AI 계정이 필요하지 않다.
모델의 자료 분석과 HTML 생성 과정은 별도다. 핵심 평가 스킬은 지침과 참조
파일이며 자체 LLM API 호출, 비밀키 요구, 백그라운드 서비스가 없다. 평가 모델의
이용료·웹 기능·파일 읽기는 실행하는 Claude/Codex 환경에 따른다.

## HTML 시각 결과물 근거

Claude Code 공식 Skills 문서는 스킬에 스크립트를 묶어 self-contained HTML을 생성하는
시각 결과물 패턴을 설명한다. Codex 공식 문서 역시 scripts/assets를 포함한 스킬을
지원한다. 이 패키지는 그 범위에서 로컬 렌더러만 추가한다.

디자인 방향 참고: 컨설팅 보고서의 편집적 위계·여백·근거 표기. 외부 사이트의 실제
자산이나 글꼴을 복사하지 않았으며 해당 회사 보고서임을 표시하지 않는다.

- `https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights`
- `https://kpmg.com/xx/en/our-insights.html`
