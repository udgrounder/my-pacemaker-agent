# 독립 문서·방법론 검토 — 2026-10-13

판정: P2 1건, P3 1건. 핵심 현재/이력 분리, 승인 전 후보 유지, reqspec-v1 기존 내부 표 점진 전환, 실패 증빙 유지, minor 조건부 이력 생성은 서로 일치한다.

## 범위·격리

기준: /Users/kjkim/Study/my-pacemaker-agent/workspace/tasks/active/20261013_plan_current_state_history/plan.md의 목적·완료 기준·제약. plan의 기존 검토 완료 주장과 테스트 수는 판정 근거로 삼지 않았다.

지정된 core 4개, inject 4개, templates 3개, discovery_classification, guidebook, architecture, test_todo_policy, test_policy_consistency의 미커밋 diff와 현재 내용을 검토했다. 필요 대조로 hooks/plan_hash.py, code_gate.py, turn_end.py, inject/_agent_execution_priority.md 및 관련 Runtime/설명 참조를 검색했다. 기존 critique·review 산출물·작업 changelog·구현 대화는 읽지 않았다. 보고서 외 파일은 수정하지 않았다. 줄 번호는 검토 당시 working tree 기준이다.

## 필수 수정 지적

### [P2] 새 승인 복구 절차를 필수 detail 로드 경로에 연결해야 한다

- 위치: /Users/kjkim/Study/my-pacemaker-agent/.mpa/runtime/core/agent_rules_detail.md:81-86.
- 상황: 두 파일 승인 갱신 중단으로 .plan-renewal.json이 남는다. code_gate는 이 사유를 기존 _approval_recovery_message에 넣어 '구현 승인 기록 복구 필요'를 출력한다. 항상 로드되는 agent_rules.md:24-25는 이 알림에서 detail의 '구현 승인 재확인', 승인 직전에는 '승인 기록 처리'만 읽게 한다.
- 영향: 섹션별 detail을 읽는 에이전트는 새 JSON 복구 절차를 전달받지 못한다. 기존 재확인 경로는 재승인→approve 또는 renew-spec을 안내하지만 새 도구는 JSON 잔존 시 이를 거부한다. 저장 중단을 재승인 문제로 처리해 불필요한 사용자 질문과 반복 실패가 생긴다. 우회가 막히므로 잘못된 해시 저장을 직접 발생시키는 문제라고 주장하지 않는다.
- 근거: detail:43-60에 새 복구 섹션 참조가 없고 :64-77도 복구 시 기존 '구현 승인 재확인'으로만 보낸다. 새 :81-86에는 필수 로드 트리거나 앞선 두 섹션의 연결이 없다. plan_hash.py는 JSON 잔존을 check/audit/approve/renew-spec에서 검사한다. code_gate.py의 _approval_recovery_message는 기존 재승인 안내를 사용한다. source 전용 architecture와 guidebook의 참조는 설치 프로젝트의 필수 Runtime 로드 경로를 대신하지 못한다.
- 수정 방향: JSON 복구 사유에서 먼저 '승인 이력 저장과 복구'를 읽도록 trigger/기존 복구 경로를 연결하고 gate 안내에서 저장 중단과 명세 변경을 구분한다.

### [P3] 구현 후 발견을 운영 안내 섹션 밖에 두어야 한다

- 위치: /Users/kjkim/Study/my-pacemaker-agent/.mpa/runtime/templates/plan_template.md:173-180.
- 상황: '## 실행 중 변경 기록'과 '## 명세 변경 이력' 제거 후 '### 구현 후 발견'은 유지했다. 마지막 상위 제목이 '## 운영 시 안내 사항'이므로 미처리 발견·명세 변경·신규 작업 링크가 운영 안내의 하위 내용이 된다.
- 영향: 템플릿 :167은 운영 안내에 사용자·운영자 행동만 두고 구현·설계·검증 후속 작업은 별도 작업으로 분리하라고 한다. 그런데 그 하위 표 :180에는 현재 plan/승인 이력 갱신이 필요한 미처리 항목이 있다. 현재 수행할 변경과 정보성 운영 안내의 경계가 충돌해 섹션별 읽기·정리 시 현재 미처리 상태 유지 의도가 흐려진다.
- 근거: 기존 diff에는 발견 제목 앞에 '## 명세 변경 이력'이 있었으며 이번 삭제로 운영 안내 아래에 편입된다. inject/layer1_discovery.md:65-73은 미처리 보완/명세 변경을 현재 plan에 유지하고 재구현으로 보내며 운영자의 정보성 행동으로 취급하지 않는다. 명시된 섹션 역할과 내용의 불일치다.
- 수정 방향: 발견을 별도 최상위 섹션이나 실행·검증 영역으로 옮기고 minor 생략 대상 제목도 실제 배치와 맞춘다.

## 변경 이전부터 남은 참조 불일치

/Users/kjkim/Study/my-pacemaker-agent/.mpa/runtime/core/agent_rules.md:232는 검증 중·테스트 중 재개에 changelog를 Phase 2 필수로 둔다. inject/layer1_review.md:125-134는 1차 전에는 읽지 않고 2차에서만 추가 로드하게 한다. 이번 diff가 만든 충돌은 아니며 더 구체적인 단계별 금지를 따르면 독립성을 유지할 수 있다. 회귀 지적 개수에 넣지 않았다. 전체 참조 정리 시 필수 표도 1차/2차 구분에 맞출 수 있다.

취향·일반 개선 제안은 추가하지 않았다.

## 검증·한계

- python3 -m unittest discover -s tests -p test_todo_policy.py: 1개 통과.
- python3 -m unittest discover -s tests -p test_policy_consistency.py: 15개 통과.
- 문자열·계약 존재 검사이며 detail 섹션별 도달 가능성과 Markdown 내용 경계를 보장하지 않는다.
- 승인 도구의 전체 실패 주입·동시성 검사와 실제 설치 에이전트 재개 시뮬레이션은 수행하지 않았다. 별도 승인 코드 리뷰를 대체하지 않는다.
- source/dist 전체 parity는 별도 재검증하지 않았다.
