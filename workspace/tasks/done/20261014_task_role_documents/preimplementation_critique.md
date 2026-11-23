# 시행 전 독립 계획 비평

## 대상과 범위

- 대상: 현재 작업의 plan.md, implementation.md, verification.md 및 Runtime의 layer1_critique.md, _agent_execution_priority.md.
- 근거 입력: 현재 문서 결과물과 project_identity.md, architecture.md, plan_critic.md. 이전 비평·설계 대화·changelog는 읽지 않았다. shared/contracts.md는 존재하지 않았다.
- 검토 초점: 최소 plan·선택 역할 문서·큰 조사 하위 폴더 허용·implementation 설계/실행 통합, 기존 승인해시와 복구, 선택 문서 audit, 1차 검증의 격리 입력과 결과 계약.

## 비평 결과

### 실패 시나리오

구현을 막는 미해소 실패 시나리오: 발견 없음.

검토한 반례와 문서 근거:

- 선택하지 않은 verification 부재를 차단하거나 선택 문서 누락을 plan으로 대체하는 경로: plan 완료 기준 2와 implementation의 문서 구성 식별·기준 연결, 검사·호환·전환에서 선택 등록만 검사하고 해당 실행을 보류하도록 명시한다.
- approve 또는 renew-spec 뒤 역할 문서 연결 저장이 중단되어 기존 승인 거래를 확대하거나 재승인을 강제하는 경로: implementation의 검사·호환·전환에서 최초 approve의 plan 단독 저장과 renew의 기존 plan/changelog 복구를 구분하며, 승인 상태를 보존하고 빠진 연결만 재개하도록 명시한다. verification은 각 중단/복구 fixture를 별도로 요구한다.
- 1차 검증이 통합 implementation의 진행 주장 또는 task diff를 읽는 경로: implementation의 역할별 읽기 범위는 설계 기준 섹션만 전달하고 실제 diff·읽기에서도 진행/완료 주장을 제외한다. verification의 1차 입력/배제 및 입력 격리 체크리스트는 이 경계를 명시하며 결과 저장은 review_phase1.md의 요구사항별 근거·판정·미확인 항목으로 정한다.

### 숨은 가정

구현 단계 재작성이나 승인 범위 변경을 요구하는 미해소 가정: 발견 없음. 의미 대응은 메인이 검토하고 helper는 등록·존재·기준 checksum의 결정론적 검사만 수행하는 경계가 명시되어 있다. 구체 metadata 표기와 섹션 추출 방식의 확정은 구현 단계 1~3의 기술 작업이며 새 사용자 결정이 아니다.

### 미해소 비가시적 위임

발견 없음. 역할 문서의 선택과 독립 실행을 분리하고 큰 작업/조사의 하위 폴더도 관리 선택으로 한정한다. 기존 단일 수정자·모델 상한·독립 실행 실패 처리를 확대하지 않는다.

### 구조적 문제와 판정

- 판정: 시행 전 blocker 없음.
- 중요도: 차단 사유 없음.
- 현재 Runtime의 plan 단독 비평 지침과 새 역할 문서 입력의 차이는 implementation 단계 4의 명시적 수정 대상이다. 시행 전 모순으로 취급하지 않는다.
- plan의 미승인 표시는 실행 전 기존 승인 절차로 갱신할 상태다. 이번 비평은 승인·Runtime 구현 완료·독립 구현 검증을 대신하지 않는다.
- 아키텍처 충돌: 검토 범위에서 발견 없음. source 수정 후 sync-runtime, 다른 작업 무변경, release/deploy 제외 및 기존 승인/완료 경계를 유지한다.
