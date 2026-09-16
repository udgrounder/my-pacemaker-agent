## 2차 독립 검증 결과

### 결론

1차 검토의 즉시 수정 필요 4건과 재검토의 public path baseline 1건은 실제 구현에서 해소됐다. changelog의 핵심 주장(모든 V1 public field baseline 고정, JSON diagnostic, source/dist parity, authority 강제)은 source와 dist 코드 및 회귀 테스트와 일치한다. 다만 제한 profile parser가 배열 문자열의 `\\/` escape를 허용해, profile 문서가 말하는 standard-TOML subset과 일치하지 않는 주의 사항 1건이 남아 있다.

### 실제 대조 및 검증 근거

- `python3 .mpa/runtime/hooks/contract_reference.py --runtime-root .mpa/runtime`와 dist의 동일 validator는 각각 code 0 JSON을 반환했다.
- `python3 -m unittest tests/test_contract_reference.py`는 13개 테스트를 통과했다.
- `diff -qr .mpa/runtime dist/.mpa/runtime`는 차이를 보고하지 않았다. 새 contract/profile/validator와 marker를 가진 core 문서가 dist에 동기화돼 있다.
- `git diff --check`도 통과했다.
- contract의 path, lifecycle, reference는 모두 `usage = "inspect-only"`, `authority = "not-invokable"`를 명시하며 validator가 baseline 및 Markdown marker/anchor와 대조한다.

### 1차 지적 해소 확인

| 이전 지적 | 판정 | 실제 근거 |
|---|---|---|
| 손상 입력의 JSON diagnostic | 해소 | `main()`이 `ContractError` 외 `UnicodeError`, `OSError`, `TypeError`, `ValueError`도 schema code 21 JSON으로 정규화한다. number owner anchor의 CLI 검증도 code 21 JSON으로 종료함을 재현했다. |
| 새 reference의 V1 safe stop | 해소 | `REFERENCE_BASELINES`와 reference set 동일성 검사로 새 entry는 code 20이 된다. 회귀 테스트가 추가 reference를 확인한다. |
| lifecycle 동시 변경의 version 보호 | 해소 | `LIFECYCLE_BASELINES`가 id, label, transition을 고정하고 V1 변경은 code 20으로 중단한다. |
| source/dist validator와 산출물 parity | 해소 | dist validator를 직접 CLI 실행하고 contract/profile/hook 바이트 동치를 검사하며, Runtime 전체 `diff -qr`도 현재 일치한다. |
| path field의 same-version 의미 변경 | 해소 | `PATH_BASELINES`와 marker 비교로 문서 marker와 TOML을 함께 바꿔도 code 20이다. 회귀 테스트가 이 경우를 다룬다. |

### ⚠️ 주의 필요 (1)

1. 배열 안의 비표준 TOML escape `\\/`를 profile parser가 허용한다. `contract_reference.py`의 scalar string parser는 이를 거부하지만, array parser는 `json.loads()` 결과만 검사한다. `parse_profile('[contract]\\nprotocol = ["bad\\\\/escape"]\\n[paths]\\n')`는 성공하고, 독립 `tomli`는 같은 입력을 `TOMLDecodeError`로 거부한다. 현재 complete V1 contract에서는 뒤의 schema/baseline 검사로 결국 실패하므로 허용된 유효 계약으로 통과하지는 않는다. 그러나 profile의 “standard-TOML subset” 및 “profile 밖 입력 거부” 설명과 parser 자체의 경계가 어긋난다. array raw value에도 `\\/` 거부를 적용하고 이 fixture를 회귀 테스트로 추가하는 편이 명세를 정확히 유지한다.

### 📝 조용한 결정 (1)

- 계획의 제외 범위에는 hook CLI를 public 실행 API로 만들지 않는다고 되어 있으나, profile과 guidebook은 validator CLI를 “supported read-only validation tool”로 명시한다. 이는 실행 권한을 주지 않는 검사 명령이라는 좁은 예외로 실제 계약·문서가 서로 일치한다. 향후 API 범위 해석에서 이 구분을 유지해야 한다.

### 🔍 틀린 에이전트 가정 (0)

- 검증한 범위에서는 추가로 틀린 가정을 확인하지 못했다. 읽기 전용 권한 경계, source/dist 동기화, 같은 V1 내 public 값 변경의 safe stop은 코드와 문서에서 확인됐다.

### changelog 및 명세 이력 판정

- changelog의 “독립 검토 보완” 내용은 구현과 일치한다. 특히 path baseline, lifecycle/reference baseline, authority, duplicate marker, CLI JSON 정규화, source/dist 검증은 실제 코드와 테스트에 존재한다.
- plan과 architecture의 experimental inspect-only 경계, 설치본 discovery, release/deploy 비포함 정책은 guidebook 및 contract/profile과 일치한다.
- changelog가 profile을 “TOML profile”로 표현한 부분은 배열 `\\/` 예외 때문에 엄밀한 standard-TOML subset이라는 주장에는 주의가 필요하다. 위 1건을 보완하면 이력과 구현의 차이는 없다.

### 권장 다음 행동

배열 escape 검사를 보완하기 전에도 현재 V1 contract의 정상/실패 경로와 dist parity는 테스트 진행 가능 상태다. profile 경계를 명세 그대로 보장하려면 주의 사항 1건을 후속 수정으로 처리한다.
