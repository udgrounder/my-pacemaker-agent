# 정책·사용자 개입 감사

기준일: 2026-09-09. 승인된 plan의 완료 기준 1~9를 대상으로 한다. 과거 done·토론·release는 현재 실행 정본으로 취급하지 않는다.

## 정의 원본과 실제 진입 경로

| 정책 | 정의 원본 | 호출자·검토 범위 | 변경 전 문제 | 변경 후 기대 행동 |
|---|---|---|---|---|
| P1 사용자 부담 | `core/agent_rules.md` 사용자 부담 최소화 | detail, design/implement/review, 모든 workflows, session_protocol, implementer/system_designer, template, direction | 단계·심각도·내부 기록만으로 반복 확인 | 의도·승인 재사용, 실제 사용자 판단만 질문 |
| P2 독립 실행 | `inject/_agent_execution_priority.md` | core, critique/review/implement, workflows, session_protocol, system_designer, architecture, guidebook, agent specs | 도구 존재를 격리로 간주; 비평 자가 대체/새 스레드 혼재 | 대화 상속 없는 입력과 유효 결과; 비평·검증 폴백 구분 |
| P3 minor | `core/agent_rules_detail.md` minor 경량 처리 절차 | core, design, implement fast-path, template, workflows, session_protocol, architecture, guidebook | 자동 승인과 선행 응답 대기 충돌; 구현 fast-path에서 확인 누락 | 명확한 실행 요청만 자동 승인; 최소 확인·미확인 기록 |
| P4 실패비용 | `core/agent_rules_detail.md` 실패비용 추정 기준 | minor 정본, workflows, design, session_protocol | 없는 core 섹션을 정본으로 지칭; 인간에게 추정 전가 | 에이전트 조사·재판정, 위험·범위 변화만 필요한 확인 |
| P5 승인·hook 보장 | 실제 `hooks/code_gate.py`, `hooks/plan_hash.py`, `install.py`; 설명은 guidebook 보장표 | agent specs 및 문서 검토 | warn 예외 누락, 실제 호스트 작동을 단정 | 설정/스크립트 테스트와 호스트 통합을 분리 |
| P6 Runtime 동기화 | `MAP_PRODUCT_RULES.md`, architecture, system designer | MPA 수정 detail·persona·guidebook | source/dist 동기화와 설치 대상 배포를 혼동 | source→dist만 자동 동기화, 설치 대상은 별도 요청 |
| P7 minor 직접 진입 | detail minor 절차 | implement fast-path | 계획만 요청한 minor plan을 실행 가능 | `구현 중`·유효 승인해시 후에만 fast-path |

경로는 별도 표기가 없으면 `.mpa/runtime/` 기준이다. stage worker는 core를 이미 읽었다고 가정하지 않고 해당 정본의 경로를 명시적으로 읽게 연결했다. `tests/test_policy_consistency.py`의 REFERENCES가 핵심 직접 참조를 검사하며 모든 자연어 의미를 검사하지 않는다.

## 사용자 개입의 필요성

| 개입 지점 | 실제로 필요한 이유 | 기존 정보 재사용 | 에이전트 처리·보고 |
|---|---|---|---|
| 명확한 minor 실행 | 추가 결정 없음 | 요청·조건 재사용 | plan·approve·확인 수행; 시작 재질문 제거 |
| 계획만 요청 | 구현 권한 없음 | 계획 요청 범위 | 계획까지만 수행 |
| major 최초 구현 | 완성 계획의 사용자 판단 | 동일 명세의 유효 승인 | 이미 승인됐으면 반복하지 않음 |
| 명세·중요 위험 변경 | 기존 위임 범위 밖 판단 | 기존 요구·제약을 비교 기준으로 활용 | 영향·권장안·변경분을 묶어 질문 |
| 내부 재판정·재시도 | 사용자 결정 없음 | 승인 범위 유지 확인 | 범위 유지 시 계속하고 누적 보고 |
| 독립 비평 미완료 | 검토 한계 수용 판단 | 동일 상황의 생략 승인 | 일시 오류만 1회 재시도 후 필요한 확인 |
| 구현 검증 미완료 | 자가 검증 한계 고지 | 기존 구현 승인 | 자가 검증·미확인 기록, 사용자에 도구 수리 전가 금지 |
| 검증 지적 수정 | 명세 내 수정은 이미 위임됨 | 유효한 구현 승인 | 상세 근거 읽기·수정·재검증; 심각도만으로 승인 요구 금지 |
| 검토 전용 요청 | 수정 권한 없음 | 검토 범위 | 발견 보고, 임의 수정 금지 |
| 결과·완료 확인 | 결과의 사용자 적합성 판단 | 이미 받은 명시적 결과/완료 확인 | 확인한 테스트 반복 요구 금지; 기록·이동은 에이전트 |

## 고정 사례의 문서 대조

아래 “충족”은 현재 문서 경로를 읽어 기대 지침에 도달함을 확인한 결과다. 실제 호스트/모델의 자연어 준수 실행은 모두 별도 미확인이며, 이 표를 실사용 성공률로 사용하지 않는다. 독립 검토에서 발견된 누락은 review 파일과 verification 기록으로 보완한다.

| 사례 | 로드 경로·근거 섹션 | 기대 행동 | 문서 대조 |
|---|---|---|---|
| minor 수정 요청 | core → detail minor 1~5 | 재질문 없이 계획·자동 승인·최소 확인 | 충족 |
| 계획만 작성 | design minor → detail 1 | approve/구현 없이 계획만 | 충족 |
| 구현 워커 직접 진입 | implement fast-path → detail | 최소 확인 정본 도달 | 충족 |
| 새 기능 비평 | new_feature → critique → priority | 격리 서브에이전트·정본 폴백 | 충족 |
| 결과 검토 | code_review → review → priority | 검증 폴백 구분 | 충족 |
| 비평 도구 없음/격리 불가 | priority 실패 처리 | 미완료·생략 확인 | 충족 |
| 호출 실패/빈 산출물 | priority 완료 조건·실패 처리 | 일시 오류만 1회 재시도 | 충족 |
| 구현 검증 실패 | review → priority 자가 검증 | 한계·미확인 기록 | 충족 |
| 요청 내 가역적 동작 수정 | implement → detail 7 | 재판정 후 응답 대기 없이 재개 | 충족 |
| 예상 밖 계약/위험 변화 | detail 7 → 실패비용 | major/critical 전환·필요 승인 | 충족 |
| 확인 수단 없음 | detail 5 | 미확인 보고·통과 주장 금지 | 충족 |
| 동일한 유효 승인 존재 | core 사용자 부담 → detail 4 | 기존 승인 재사용 | 충족 |
| 실행 방법 선택 | implementer → core | 에이전트 조사·판단·기록 | 충족 |
| 관련 결정 여러 개 | core 사용자 부담 | 영향·권장안과 묶어 질문 | 충족 |
| 내부 재판정 무변화 | detail 7, core 사용자 부담 | 응답 대기 없이 진행·누적 보고 | 충족 |
| 기록·상태 정리 | detail 6, review 메인 처리 | 에이전트 관리 | 충족 |
| 신규 발견만 있고 완료 승인 없음 | discovery 4단계·종료 처리 → core | 원래 작업을 active에 유지, 완료 승인 후에만 done | 수정 후 충족 |
| 승인해시 기록만 누락 | detail 구현 승인 재확인 | 당시 명시 승인·명세·위험 동일성이 입증될 때만 정상 복구; 불명확하면 재승인 | 수정 후 충족 |

## 검사 근거와 한계

- 정적 회귀: 핵심 정본 파일/참조와 알려진 충돌 문구를 검사한다. 누락 참조·정의 삭제·옛 폴백 삽입의 변이 입력으로 검출 능력을 확인한다.
- 동작 회귀: 실제 gate를 임시 cwd에서 실행해 인식된 소스의 block/warn/off와 미상 도구·미상 경로·허용 접두사·Bash 일반 쓰기 미검사 경계를 확인한다. 입력 command 문자열은 실행하지 않는다.
- 기존 `test_plan_hash.py`: selected critical 및 명세 변경과 실행 기록 변경 구분을 계속 검증한다.
- 기존 `test_install.py`: 설정 생성·스크립트 smoke·중첩 cwd 발견을 검증한다. 실제 호스트의 event dispatch·차단 수용은 입증하지 않는다.
- 실제 사용자 프로젝트 배포, 모델별 장기 준수 평가, 모든 자연어 모순의 자동 탐지는 수행하지 않는다.

## 추가로 발견한 활성 참조

`personas/implementer.md`의 모든 미명세 기술 결정 질문, `layer1_review.md`의 상세 결과 읽기 금지·사용자 수동 요약 요구, `session_protocol.md`의 모든 inject 새 스레드 강제, workflows의 인간 실패비용 추정·무조건 커밋 요구를 대상 정책의 활성 호출자로 포함했다. 사용자 변경을 보존하는 가역성 확인과 실제 의도·위험 경계는 유지한다. 이 보완은 승인 명세의 사용자 부담 최소화·활성 호출자 감사 범위 안이다.

1차 독립 검토에서 `layer1_discovery.md`의 완료 승인 우회와 detail의 승인 기록 누락 재확인을 발견했다. 두 경로를 수정하고 발견 분류의 호출자 `skills/analysis/discovery_classification.md`까지 사용자 부담 원칙에 연결했다. 초기 정적 검사 8개가 이 두 의미적 충돌을 놓쳤다는 한계를 유지한다. 발견 후 완료 승인 우회 문구에 대한 변이 회귀 검사 1개를 추가했으며, 이것도 모든 승인 오류를 검출하는 장치는 아니다.

2차 검토에서 팀 workflow의 두 단계에 남아 있던 새 스레드 지시를 발견해 현재 작업에서 해당 지침을 읽는 것으로 수정했다. 알려진 옛 단계 지시를 금지 문구 검사에 추가했고, 최종 전체 151개 테스트와 58개 Runtime asset parity를 확인했다.
