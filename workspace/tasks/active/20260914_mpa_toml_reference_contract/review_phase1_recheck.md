## 검토 결과

V1의 lifecycle 및 reference 집합은 validator 내부 baseline으로 고정되어 있으며, 손상된 계약은 CLI에서 JSON 진단으로 종료된다. 다만 `paths.tasks_root`와 `paths.docs_root`는 계약과 Markdown binding marker를 함께 바꾸면 `contract_version = 1`인 채 validator를 통과한다. 이 두 값도 외부 consumer가 읽는 public field이므로, 같은 버전에서 의미가 바뀌어도 consumer가 호환성 중단을 할 수 없다.

## 정합성 확인

- source와 `dist/.mpa/runtime` 전체는 `diff -qr`에서 차이가 없었다. 계약 TOML, profile 문서, validator도 byte 단위로 동일하다.
- source 및 dist validator를 각각 실행해 모두 code 0 JSON 진단으로 성공했다.
- `python3 -m unittest tests/test_contract_reference.py`는 12개 테스트를 통과했다.
- 계약의 모든 lifecycle/reference에는 `usage = "inspect-only"`와 `authority = "not-invokable"`가 기계적으로 명시되어 있고, validator도 이를 강제한다. reference에는 hook 경로나 실행 인자가 없다.
- profile은 지원 문법을 제한하고, BOM·inline comment·unknown key/table·경로 이탈·symlink·중복 binding marker를 거부한다. CLI의 ContractError 및 일반 입출력/형 오류 경로는 JSON 단일 진단으로 안전 종료한다.
- lifecycle id·label·transition 및 reference set/owner 변경은 V1 baseline과의 비교에서 code 20으로 차단되고, Markdown marker 값 drift는 code 23으로 차단된다.

## 주의 필요

- 정상 source contract는 테스트에서 Python API로 검증하고, dist만 정상 CLI invocation을 검증한다. CLI가 public validator interface이므로 source의 정상 `--runtime-root` CLI JSON 출력도 회귀 테스트로 고정하면 source/dist 실행 증빙이 대칭적이다.
- 테스트는 lifecycle id와 reference 추가만 version 보호 사례로 다룬다. lifecycle label·transition, 기존 reference owner/anchor, 그리고 경로 field의 compatibility policy를 각각 명시적으로 회귀화해야 정책 변경 시 의도를 잃지 않는다.

## 즉시 수정 필요

- `paths.tasks_root`와 `paths.docs_root`를 V1 baseline 또는 명시적인 compatibility 정책으로 고정해야 한다. 현재는 계약 값과 `core/agent_rules.md` marker를 함께 `workspace/tasks_v2`처럼 변경해도 validator가 성공한다. public 경로의 의미 변경을 V2로 올려 code 20 안전 중단하게 하거나, V1에서 허용하는 변경이라면 consumer migration/호환성 규칙을 profile에 명시해야 한다.

## 조용한 결정 목록

- 경로 field는 lifecycle/reference와 달리 같은 V1에서 정본과 동시 변경할 수 있다는 정책이 코드에만 존재하며, profile의 version 설명에는 드러나지 않는다.
- validator CLI의 인자 자체가 잘못된 경우(`argparse` 사용 오류)는 JSON diagnostic 계약 밖이다. 손상된 계약 입력에는 해당하지 않지만, “항상 JSON 한 줄”을 CLI 호출 오류까지 약속하려면 별도 처리 범위를 정해야 한다.

## 에이전트 가정 검증

- “V1은 inspect-only이며 consumer에게 hook 실행·수정·승인·배포 권한을 주지 않는다”는 가정은 계약 metadata, validator 강제, guidebook 설명, 비변경 consumer test로 확인됐다.
- “source와 dist가 같은 Runtime 계약을 제공한다”는 가정은 현재 파일 parity와 양쪽 validator 실행으로 확인됐다.
- “같은 contract_version에서 public field 의미가 변하면 안전하게 보호된다”는 가정은 경로 field에서 성립하지 않았다.
