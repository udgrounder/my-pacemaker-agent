## 비평 결과

### 🚨 실패 시나리오
- 시나리오 1: 자동화 계정이 `deploy`를 실행하고 사람이 `--verified-by`에 검증자를 넣는다 → 계획이 `verified_by`를 “실제 실행자이자 복구 책임 주체”로 재해석하면, receipt/history는 실행·복구 책임을 지지 않은 사람을 책임자로 기록한다. 현재 가이드도 이 값을 `<검증자>`로 표기하므로, 단순 인자 제거만으로 역할 의미가 바뀌지 않는다.
- 시나리오 2: 배포 또는 rollback이 Runtime 교체 뒤 receipt/history 기록 전에 실패한다 → 현재 실패 receipt에는 `verified_by`도 없다. 성공 기록에서만 책임자를 남기는 계획대로면, 가장 복구 책임 추적이 필요한 실패·자동복구 시나리오의 책임 주체가 사라진다.
- 시나리오 3: `deploy`·`rollback`만 수정한 뒤 운영자가 `history-cleanup --apply` 또는 `migrate-runtime-backups`를 실행한다 → 두 명령은 여전히 `--rollback-owner`를 요구·기록한다. 제품 규칙의 “별도 복구 담당자 입력·검증·기록 제거”와 실제 CLI 계약이 다시 충돌하고, 책임자 제거가 일부 명령에서만 적용된다.
- 시나리오 4: 함수 직접 호출 fixture만 바꾸고 parser 회귀를 검사하지 않는다 → `deploy`/`rollback` argparse에 `--rollback-owner`가 남거나 `--verified-by` 요구가 약화되어도 unit test가 통과할 수 있다. 계획의 “없는 정상 CLI” 완료 기준을 검증하지 못한다.

### ⚠️ 숨은 가정 (파급효과 높은 순)
- 가정 1: `verified_by`가 실행자 식별자라는 전제 / 틀렸을 때: 기존 계약·문서가 뜻하는 검증자와 책임자/실행자가 합쳐져 감사 의미가 변하고, 자동화·대리 실행에서 잘못된 사람이 책임자로 남는다.
- 가정 2: 책임 주체는 성공 deploy·rollback receipt/history에만 기록하면 충분하다는 전제 / 틀렸을 때: 실패 receipt, rollback 실패, 자동 복구 등 실패비용이 큰 경로에서 책임 추적 계약이 공백이 된다.
- 가정 3: `rollback_owner`의 모든 사용처가 deploy·rollback과 그 문서에만 있다는 전제 / 틀렸을 때: `history-cleanup`, `migrate-runtime-backups`, command contract 및 deployment profile이 옛 gate를 계속 강제한다.
- 가정 4: 과거 receipt/history가 새 필드 부재 계약과 안전하게 공존한다는 전제 / 틀렸을 때: 현재 또는 후속 audit/consumer가 새 기록에는 키 부재, 과거 기록에는 키 존재를 처리하지 못하거나 스키마 비교가 깨질 수 있다.
- 가정 5: `workspace/memory/shared/contracts.md`가 없거나 최신 계약이 필요 없다는 전제 / 틀렸을 때: 계획이 요구하는 shared 계약 검증 없이 source 문서와 Runtime 문서의 서로 다른 책임자 정의를 임의로 확정하게 된다. 해당 파일은 현재 존재하지 않는다.

### ❓ 미해소 비가시적 위임
- 항목 1: `verified_by`의 정확한 의미를 결정하지 않았다. “CLI를 실행한 운영자”, “배포 결과를 검증한 사람”, “자동화 service account”, “사용자가 지정한 책임자” 중 어느 값을 허용하고 receipt에 어떤 용어로 설명할지 사용자 결정이 필요하다.
- 항목 2: 책임자 일원화의 적용 범위를 결정하지 않았다. `history-cleanup`과 `migrate-runtime-backups`도 같은 책임자 모델을 써야 하는지, 아니면 deploy/rollback 전용 예외인지 명세에 적어야 한다.
- 항목 3: 새/실패 receipt와 대상 history 각각에 책임 주체를 어떤 필드와 불변성으로 남길지 결정하지 않았다. “별도 필드는 없다”와 “`verified_by`가 책임 주체로 해석된다”만으로는 실패 기록, redaction, 누락/공백 값 거부 계약이 정해지지 않는다.
- 항목 4: legacy receipt/history 호환 정책이 “재작성하지 않는다”를 넘지 못한다. 기존 `rollback_owner`를 읽는 소비자의 허용 여부와 새 record의 키 부재를 명시적으로 허용하는 schema/audit 검증이 없다.

### 🔧 구조적 문제
- 항목 1: Step 1이 `verified_by`의 의미와 기록 스키마를 조용히 확정한 뒤 Step 3에서 계약 문서를 맞추는 순서다. 먼저 책임자 의미·적용 명령·성공/실패 기록 계약을 명세와 command contract에서 확정하고, 그 계약에 맞춰 CLI·receipt·history를 변경해야 한다.
- 항목 2: 수정 대상에는 `release_manager.py`만 있지만 실제 동일 필드의 parser·검증·출력은 `history-cleanup`과 `migrate-runtime-backups`에도 남아 있다. 범위에서 의도적으로 제외한다면 command contract/deployment profile의 “rollback 책임자” 일반 규정을 deploy/rollback에 한정하도록 분리해야 하고, 포함한다면 코드·tests·문서 대상에 추가해야 한다.
- 항목 3: Step 2의 테스트 계획은 정상 성공과 승인 메타데이터만 다룬다. `--rollback-owner`가 argparse에서 사라졌는지, `--verified-by` 공백/누락이 거부되는지, deploy와 rollback 각각의 성공·실패 local receipt 및 target history에서 키 부재/책임자 값이 일관되는지, legacy 기록을 읽은 뒤 새 작업이 가능한지를 검증하지 않는다.
- 항목 4: `map-product-rules/deployment-coordination.md`와 `map-product-rules/command-contract.md`는 현재 dry-run·승인·rollback 책임자를 apply gate로 한 묶음으로 규정한다. 계획은 이 계약 충돌을 파일 변경 목록으로만 적고, 승인 gate에서 무엇을 대체 검증하는지와 `verified_by`의 필수성/정제 규칙을 명세화하지 않아 gate가 의도치 않게 약화될 여지가 있다.
