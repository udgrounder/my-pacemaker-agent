# minor 태스크 생성 시 INDEX.md 등록이 반복적으로 누락됨
**타입**: 방법론 개선
**발견 상황**: 2026-07-03 세션에서 minor 태스크 5개를 연달아 생성했는데, 그중 4개(`arcstudio_rule_absorption`, `version_timestamp_precision`, `gate_hash_scope_reduction`, `hook_path_robustness`)에서 생성 시점에 INDEX.md 등록을 빠뜨리고 완료 처리 시점에야 뒤늦게 알아채 등록했다. Layer 2 체크포인트에서 발견됨.
**적용 범위**: 모든 프로젝트

## 현재 방식
`agent_rules.md` "minor 경량 처리 절차"·`agent_rules_detail.md` "minor 경량 처리 절차"는 plan.md 작성·approve·구현·완료 보고 단계를 명시하지만, **INDEX.md 등록 시점**을 minor 절차 안에서 명시적인 체크 항목으로 강제하지 않는다. major 절차(`layer1_design.md`)는 "세션 종료 시" 6번 항목에 "tasks/INDEX.md 업데이트 → 새 태스크 항목 추가"가 명시돼 있어 상대적으로 덜 누락되지만, minor는 "완료 시 INDEX 갱신"만 있고 "생성 시 INDEX 등록"이 절차 텍스트에 별도 단계로 없어 에이전트가 건너뛰기 쉽다.

## 개선 방안
`agent_rules_detail.md`의 "minor 경량 처리 절차" 1~3단계(계획 제시 → plan.md 작성 → approve 실행) 사이 또는 직후에 "INDEX.md에 상태(구현 중)로 즉시 등록" 단계를 명시적으로 추가한다. 이상적으로는 `plan_hash.py approve` 실행 시 INDEX.md 등록 여부를 함께 안내하거나(예: approve 성공 메시지에 "INDEX.md 등록 확인" 리마인더 추가) 기계적으로 강제하는 방법도 고려할 수 있다(단, 이건 스크립트 수정이 필요해 별도 설계 필요).

## 적용 대상 파일
- `.mpa-workspace/core/agent_rules_detail.md` ("minor 경량 처리 절차" 섹션)
- (선택) `.mpa-workspace/hooks/plan_hash.py` (approve 성공 메시지에 리마인더 추가)
