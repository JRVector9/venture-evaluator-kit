# 사업 평가 작업 공간

이 폴더는 사업 자료와 맥락을 보관합니다. 설치된 스킬 폴더와 분리돼 있습니다.
초기화 스크립트는 비어 있는 템플릿만 만들며 대화나 계정 자료를 수집하지 않습니다.

- `business-input.md`: 새로운 사업 설명을 아는 범위에서 작성합니다.
- `venture-context.md`: 이전 대화의 결정·관측·미채택 아이디어를 정리합니다.
- `sources/`: 사용자가 선택한 사업계획서, 지표, 대화 요약을 넣습니다.
- `projects/`: 사업별로 맥락이 길어질 때 분리합니다.
- `evaluations/`: 저장을 요청한 평가 보고서를 보관합니다.

Claude Code 예:
`/venture-evaluator portfolio .venture/venture-context.md brief`

Codex 예:
`$venture-evaluator portfolio .venture/venture-context.md brief`

자연어 예:
“venture-evaluator를 사용해 이 폴더의 사업계획서와 맥락을 평가해줘.”

민감 자료가 실수로 Git에 추가되지 않도록 이 폴더의 `.gitignore`는 기본적으로
README와 .gitignore 외의 새 파일을 무시합니다. Git에 이미 추적 중인 파일에는
소급 적용되지 않습니다. 공유가 필요할 때만 내용을 검토한 후 설정을 바꾸세요.

평가 스킬은 과거 대화를 자동 조회하는 기능이나 모델 재학습 기능이 아닙니다.
자료를 읽는 AI 호스트의 데이터 처리 정책과 권한도 확인하세요.

## HTML 보고서 (v1.1+)

최종 평가의 기본 산출물은 `reports/<timestamp>-<slug>.html`과 `.json`입니다.
HTML은 로컬 브라우저에서 열고, JSON은 동일 보고서 재생성에 사용합니다.
보고서 작성이 기존 맥락을 자동 갱신하지는 않습니다. 기본적으로 비공개 자료로
다루고, 외부 공유 전 민감 정보와 근거의 공개 권한을 확인하세요.
