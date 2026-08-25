# 독립 비평

## 실패 시나리오

- `workspace/docs`를 deploy·backup 경계 검사 대상으로 넣으면, 현재 아키텍처의 “deployment와 rollback은 workspace·docs를 읽거나 변경하지 않는다”는 계약과 충돌한다. 해당 경로를 어느 명령이 왜 검증하는지 분리하지 않으면 정상 설치·배포가 불필요하게 실패하거나 경계가 확장된다.
- lexical path 검사만으로 root 탈출을 막으면 검사 뒤 교체되는 symlink(TOCTOU), ZIP 안의 symlink·special file·중첩 traversal, hardlink 및 권한 변경으로 우회될 수 있다. 해제·검사·교체의 원자성 및 허용 파일 유형이 계획에 없다.
- 외부 파일 수정은 “명시 승인과 정확한 경로”만으로는 부족하다. 승인 뒤 대상이 symlink 교체되거나 내용·inode가 바뀌면 다른 파일을 수정할 수 있다. 승인 시점의 실경로·무결성·재확인 규칙이 없다.
- agent별 E2E가 실제 native agent 실행 파일·환경변수·설치 위치를 모두 재현하지 못하면, 존재 여부만 통과한 hook이 실제 제품 환경에서 실패한다. 지원 agent별 실행 가능 범위와 대체 검증이 정해지지 않았다.
- 민감 절대 경로 검사가 package 본문만 다루면 예외 메시지, CI 로그, dry-run 출력, manifest/receipt의 중첩 필드에서 다시 유출될 수 있다. “민감”의 정의와 기록·표시·마스킹 지점이 없다.

## 고위험 숨은 가정

- 이 plan은 `상태: 구현 중`인데 TODO에는 승인 후 `approve`로 구현 전환한다고 되어 있다. 승인해시 불일치를 이미 재현했다고 하면서, 현재 plan 자체가 유효한 승인 절차를 거쳤다는 근거는 없다. critical 작업의 구현 선행 승인 불변식이 이미 깨진 상태에서 보완을 시작할 위험이 있다.
- `contracts.md`가 실제로 존재하지 않는다. 그런데 plan은 contracts에 의존하는 설치·배포·hook 계약을 변경한다. 누락된 계약을 허용하는지, 복구가 선행 조건인지 결정되지 않았다.
- “critical은 기본 block” 정책은 Runtime의 현행 “기본 hook은 경고, `MPA_GATE=block`에서만 불일치 차단”과 직접 충돌한다. 어느 gate가 어떤 task의 실패비용을 신뢰하고, 환경변수로 critical 차단을 해제할 수 있는지 불명확하다.
- source/runtime-dist parity가 파일 바이트 동일성만 뜻하는지, 생성물 제외 규칙과 asset map·실행 가능 권한까지 포함하는지 정해지지 않았다. 동기화 후에도 실행 계약이 드리프트할 수 있다.

## 미해소 결정

- `workspace`, `docs`, `backups` 각각에 대해 install·deploy·rollback·audit가 읽기/쓰기/검증할 권한 매트릭스가 필요하다. 특히 architecture의 사용자 데이터 보존 원칙과 Step 4의 검사 범위가 충돌한다.
- legacy 실행 참조의 정확한 탐색 root, allowlist, 생성 파일 포함 여부, 실패 메시지 및 false positive 처리 기준이 없다.
- release audit이 “모든 활성 hook”으로 간주할 등록 원천과 Python 외 hook의 정적/동적 검증 기준이 없다.
- agent별 “지원”을 native hook 실제 실행까지 뜻하는지, 설치 파일 생성만 뜻하는지와 CI에서 사용할 agent binary/fixture 정책이 없다.
- invalid active plan의 복구 책임자, 사용자 재개 요청의 식별 방식, 복구 전 진단이 source 변경을 어느 정도까지 허용하는지가 없다.

## 구조적 순서 문제

- Step 1의 clean-install E2E를 먼저 추가하면, 아직 symlink·root-escape 방어가 없는 installer를 테스트 fixture에서 실행하게 된다. 경계 preflight의 최소 구현과 악성 fixture를 Step 1과 함께 선행해야 한다.
- Step 2의 gate 정책과 Step 3의 승인 무결성은 하나의 차단 판단 경로를 공유한다. 별도 단계로 구현하면 Step 2가 일시적으로 invalid plan을 warn 또는 통과시키는 회귀를 만들 수 있으므로 단일 변경·단일 회귀 매트릭스로 설계해야 한다.
- release audit 강화는 Step 5에 있으나, Step 1에서 생성·실행하는 package/agent E2E의 신뢰 전제가 먼저 확정되지 않았다. package 해제 및 asset-map 경계 검증을 실행 테스트보다 앞에 배치해야 한다.
