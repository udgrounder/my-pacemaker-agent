## 독립 시행 검증 결과

### 판정

통과. 계획서의 V1 experimental·inspect-only 계약 범위와 구현이 일치한다. source와 `dist/.mpa/runtime/`의 계약, profile, validator는 각각 byte parity이며, 양쪽 Runtime에서 discovery와 CLI validation이 성공했다. 독립 검증 중 재현된 malformed TOML·경로 이탈·symlink·Markdown marker drift·version 오류는 모두 JSON 한 줄을 출력하고 변경 권한 없이 안전 중단했다.

### 실행 근거

- source와 dist의 `contracts/agent_reference.toml`, `contracts/agent_reference_profile.md`, `hooks/contract_reference.py`에 `shasum -a 256` 및 `cmp -s`를 실행했다. 각 쌍의 SHA-256은 각각 `6887308d5f1cdefb63d096dc0247abfc8ca0348d4730cac79a6da62c7728c814`, `941ff49c4c65386bd31fbb07363a3b95268df3122f0e237ebeb6f3299c5c64ac`, `ef21535d87cb9a92394b3e7c9aa892c92745e5de6e9288b6da0a7d259d7ba30c`로 동일했다. Runtime 규칙 문서 두 파일도 source/dist diff가 없었다.
- Python `3.9.6`에서 임시 pycache를 사용해 source/dist validator를 `py_compile`했고, source `--runtime-root`, dist `--runtime-root`, source `--project-root .`, dist `--project-root dist` CLI를 실행했다. 모두 종료 코드 0과 JSON 성공 진단을 반환했다.
- `PYTHONPYCACHEPREFIX=/private/tmp/contract_reference_pycache python3 -m unittest -v tests/test_contract_reference.py`를 실행했다. 13개 테스트가 모두 통과했다. 표준 TOML oracle, source/dist, BOM·inline comment·unknown key·비표준 escape, version, lifecycle/reference/path version 변경, owner marker drift/중복, anchor/path escape, symlink, 손상 입력 JSON, project-root read-only consumer를 포함한다.
- 임시 Runtime 복사본에서 validator CLI를 직접 실행해 다음 오류 경계를 확인했다. `contract_version = 2`는 JSON `code: 20`; `docs_root = 4`는 `code: 21`; `owner_path = "../outside.md"`는 `code: 22`; path binding marker를 `workspace/docs`로 바꾼 경우는 `code: 23`; owner Markdown을 Runtime 밖 파일을 가리키는 symlink로 바꾼 경우는 `code: 22`를 반환했다. 각 출력은 `code`, `field_id`, `path`, `message` 네 키만 가진 한 줄 JSON이었다.
- 계약의 모든 public entry/lifecycle가 `usage = "inspect-only"`, `authority = "not-invokable"`를 명시한다. validator에는 hook 실행·승인·배포·파일 쓰기 호출이 없고, project-root consumer 테스트는 Runtime 파일의 전후 byte map이 동일함을 확인했다. 검사 후 source/dist Runtime에 `.pyc` 또는 `__pycache__`가 생기지 않았고, 검증은 대상 구현 파일을 수정하지 않았다.

### 발견 사항

발견된 결함 없음. 최초 `py_compile`은 macOS 기본 pycache cache 경로에 대한 샌드박스 권한 때문에 실패했으며, 임시 pycache 경로로 재실행해 Python 3.9 컴파일 및 전체 테스트를 정상 확인했다. 이는 validator 구현 또는 Runtime 동작의 실패가 아니다.
