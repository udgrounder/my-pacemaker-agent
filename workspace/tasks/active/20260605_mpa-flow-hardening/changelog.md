# Changelog — MPA 흐름 강화

## 변경 내용

- `code_gate.py`
  - 승인해시가 비어 있을 때 자동 `approve`를 실행하던 흐름을 제거했다.
  - `GATE 1 복구 필요` 차단 메시지와 3가지 명시적 복구 경로를 추가했다.

- `hooks/README.md`
  - 승인해시 없음 복구 절차를 문서화했다.
  - 자동 복구하지 않고 사용자 승인 이력 확인 후 `approve`하도록 정리했다.

- `core/agent_rules.md`
  - 승인해시 없음 자동 차단과 복구 분기를 추가했다.
  - minor 태스크를 최소 기록 + 자동 완료 fast-path로 더 단순화했다.
  - 완료 처리를 에이전트가 제안할 수 있게 하되, 사용자 승인 없이 완료 처리하지 못하도록 문구를 수정했다.

- `inject/layer1_design.md`
  - minor에서 생략하는 설계 항목을 명확히 했다.

- `inject/layer1_implement.md`
  - minor fast-path를 추가해 일반 changelog/review/test/docs/memory 후처리를 우회하게 했다.

- `inject/layer1_review.md`
  - 서브에이전트가 `review_summary.md`를 추가 저장하도록 했다.
  - 메인 에이전트는 phase 상세 파일 대신 메타 요약만 읽고 사용자에게 전달한다.
  - 완료 처리 질문 금지 문구를 제거하고, 무승인 완료 처리만 금지하도록 수정했다.

- `dist/.mpa-workspace/`
  - 설치본 변경과 동일한 내용을 배포 소스에도 반영했다.

## 검증

- `env PYTHONPYCACHEPREFIX=/private/tmp/mpa_pycache python3 -m py_compile .mpa-workspace/hooks/code_gate.py dist/.mpa-workspace/hooks/code_gate.py`
- 승인해시 없는 `구현 중` plan.md에 대해 `code_gate.py`가 exit code `2`와 `GATE 1 복구 필요` 메시지를 반환하는 것을 확인했다.
- `.mpa-workspace/`와 `dist/.mpa-workspace/`의 차이는 `.mpa-version`, upgrade-candidates 차이만 남는 것을 확인했다.
