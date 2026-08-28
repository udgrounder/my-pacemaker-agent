# 변경 기록: 소스 로그 메시지 이모지 금지 기본 규칙

## 변경 내용

- `.mpa/runtime/core/agent_rules.md`의 항상 로드되는 규칙 상단에 `소스 로그 작성 규칙` 섹션을 추가했다.
- 소스 코드가 남기는 진단·운영 로그 메시지는 재처리 호환성을 위해 이모지·이모티콘 없이 일반 텍스트로 작성하도록 했다.
- UI 문구, 문서, 에이전트 대화처럼 로그가 아닌 텍스트는 적용 대상에서 제외했다.
- `python3 release_manager.py sync-runtime`을 실행해 source Runtime을 `dist/.mpa/runtime/`에 동기화했다.

## 검증 근거

- `cmp -s .mpa/runtime/core/agent_rules.md dist/.mpa/runtime/core/agent_rules.md`가 성공해 두 규칙 파일의 일치를 확인했다.
- `git diff --check`이 성공해 공백 오류가 없음을 확인했다.
