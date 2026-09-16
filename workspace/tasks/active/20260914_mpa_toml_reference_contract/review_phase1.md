## 검토 결과

### 정합성 확인

- 계약은 작업/문서 기본 경로, major/minor 상태, Markdown 진입점만 노출하며 `plan_hash.py`·`code_gate.py` 같은 기존 실행 권한을 참조하지 않는다.
- source와 `dist/.mpa/runtime`의 현재 계약은 validator로 정상 검증됐고, `tests/test_contract_reference.py`의 8개 테스트도 통과했다.

### 즉시 수정 필요

1. 손상 입력이 항상 안정된 JSON diagnostic으로 끝나지 않는다. `validate()`는 `ContractError`만 잡는다. UTF-8이 아닌 contract/Markdown, 읽기 권한 오류, 그리고 string이어야 할 `paths.*`, `owner_anchor`, `state_ids` 자리에 number가 들어간 profile-허용 값은 `UnicodeDecodeError`·`OSError`·`TypeError` traceback과 exit 1로 끝날 수 있다. 완료 기준의 “손상 계약 ... 안정된 종료 코드와 machine-readable diagnostic” 및 profile의 “one JSON line”을 위반한다. 모든 파일/형식 예외를 21 또는 22의 `ContractError`로 정규화하고 CLI fixture를 추가해야 한다.

2. V1의 향후 field 추가 안전 중단이 구현되지 않았다. `[[references]]`는 임의 개수와 임의 `field_id`를 허용한다. 따라서 producer가 새 reference table을 더해도 구 validator는 code 0을 반환한다. profile과 계획은 선택 field를 포함한 schema 변경을 새 `contract_version`으로 올리고 구 consumer가 code 20으로 중단해야 한다고 정한다. V1 reference의 허용 ID/set을 고정하거나, 새 reference가 version error가 되도록 검사와 회귀 fixture를 추가해야 한다.

3. lifecycle 호환성 정책도 강제되지 않는다. TOML의 state id/label/transition과 Markdown marker를 함께 바꾸면 `_lifecycle_binding()` 비교는 여전히 일치하여 code 0이다. 하지만 명세는 id 변경·전이 제거를 version bump 대상으로 규정한다. 현재 marker는 같은 변경자가 함께 바꿀 수 있는 동시 변경물이라 호환성 기준점이 될 수 없다. V1 canonical lifecycle을 validator에 고정하거나, versioned baseline fixture를 별도 신뢰 기준으로 두고 label/id/transition 변경 fixture를 검사해야 한다.

4. source/dist parity 회귀 검증이 없다. `test_distribution_contract_validates`는 source에서 import한 validator로 dist contract를 읽을 뿐, dist의 `hooks/contract_reference.py`를 실행하지도 않고 contract/profile/hook의 동치도 비교하지 않는다. plan step 5와 checklist가 요구한 source/dist validator 각각의 실행 및 artifact parity를 테스트로 고정해야 한다. 현재 수동 실행이 성공해도 다음 sync 누락을 막지 못한다.

### 주의 필요

- 계획의 `not-invokable`은 public contract의 모든 reference에 있어야 하지만 현재 TOML과 profile에는 `usage = "inspect-only"`만 있고 별도 authority 값과 검증이 없다. 문서의 자연어 금지만으로는 consumer가 기계적으로 실행 불가를 판정할 수 없다.
- profile은 “standard-TOML subset”과 독립 TOML oracle을 요구하지만 `json.loads()`는 TOML이 허용하지 않는 JSON escape(예: `\\/`)도 수용한다. 유효 contract를 standard parser도 읽어야 한다는 반례를 validator가 보장하지 못한다. TOML-compatible escape를 직접 제한하고 그런 fixture를 추가해야 한다.
- 독립 TOML oracle 테스트는 `tomli`가 없으면 skip하며, 프로젝트에 개발 의존성으로 선언돼 있지 않다. skip 시 source validator 검증도 함께 건너뛴다. Python 3.11+ `tomllib` fallback 또는 명시적 test dependency와 별도 source validation을 두어야 한다.
- plan step 4가 요구한 label/id/transition 변경, anchor rename, non-execution 가상 consumer fixture는 테스트에 없다. 현재 테스트는 version, 한 path marker, anchor 누락, path escape, symlink만 다룬다.

### 조용한 결정 목록

- “hook 경로·CLI·인자·출력을 public 실행 API로 공개하지 않는다”는 제외 범위와 달리 guidebook은 `.mpa/runtime/hooks/contract_reference.py --project-root .`를 외부 도구의 실행 명령으로 공개한다. architecture에는 validator CLI가 명시돼 있으므로 의도된 예외인지, public validator API로 승격한 것인지 계약에 명확히 기록해야 한다.
- Markdown marker 추출은 `dict(MARKER.findall(...))`이다. 같은 `field_id` marker가 두 번 있으면 마지막 marker만 신뢰하고 모순을 drift로 거부하지 않는다. 정본 marker가 하나라는 전제를 profile에 적거나 중복을 code 23으로 거부해야 한다.
- reference owner는 Runtime 안의 임의 Markdown 파일/anchor를 허용한다. 현재 V1의 세 entry ID와 각 owner의 고정 대응을 보장하지 않아 producer가 같은 version에서 entry 의미를 바꿀 수 있다.

### 에이전트 가정 검증

| 가정 | 판정 | 근거 |
|---|---|---|
| 1차 계약은 읽기 전용이어야 한다 | 부분 충족 | 기존 승인·수정·배포 hook과 연결하지 않았고 validator도 쓰기 동작은 없다. 다만 `not-invokable` 기계 표현과 consumer fixture가 누락됐다. |
| 제한 profile은 유지 비용을 통제할 수 있다 | 부분 충족 | Python 3.9 표준 라이브러리 구현은 지켰지만 JSON parser 허용 범위가 standard-TOML subset보다 넓고 손상 입력의 안정 진단이 없다. |
| 문서에 binding marker를 둘 수 있다 | 부분 충족 | marker로 단일 파일 drift는 잡지만 lifecycle 동시 변경과 중복 marker를 막지 못해 version/정본 보호 가정은 성립하지 않는다. |
