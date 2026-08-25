# 1차 독립 검토 결과

## 정합성

- **[즉시수정]** 계획의 “active source와 패키징된 Runtime에서 이전 경로 문자열 검사” 요구사항이 구현되지 않았다. `release_manager.py`의 `validate_packaged_runtime()`은 ZIP member의 traversal/symlink, asset map, 두 hook의 `--help`만 확인한다. Runtime 파일 내용에 `.mpa-workspace`, `.mpa-runtime`, `.mpa-project`, `.mpa-config` 등 제거 대상 문자열이 남아도 manifest가 그 asset map으로 작성되면 검증을 통과한다. 따라서 plan.md의 78행 및 108행의 재발 방지 조건과 운영 문서의 “경로 검사” 설명이 성립하지 않는다. source와 ZIP 해제본 모두를 대상으로 명시적 금지 문자열 검사를 추가하고, 각각의 실패 회귀 테스트를 추가해야 한다.

- **[주의]** current-layout preflight는 `.mpa/runtime`이 디렉터리인지 하나만 검사한다. 계획·문서가 활성 설치 구조를 `.mpa/runtime`, `.mpa/config`, `.mpa/backups`로 정의한 것과 달리 config/backups의 구조적 안전성은 검사하지 않는다. 특히 `.mpa/config` 또는 `.mpa/backups`가 일반 파일·symlink인 대상은 deployment transaction 중간에 실패할 수 있다. preflight에서 해당 경로의 타입과 symlink를 명시적으로 거부하거나, 문서의 계약을 “runtime만 사전 존재, 나머지는 deploy가 생성”으로 좁혀야 한다.

## 주의

- **[주의]** ZIP hook 검증은 `subprocess.run([python, hook, "--help"], cwd=runtime)`으로 패키지의 Python top-level 코드를 현재 프로세스 권한·환경변수로 실행한다. release-audit은 self-consistent하게 수정된 bundle도 이 경로로 실행할 수 있고, manifest/package에는 서명 또는 외부 immutable 저장소 검증이 없다. `--help`가 hook의 실제 이벤트 경로를 검증하지 못하는 데 비해, top-level side effect·환경 비밀 접근·파일 접근 위험은 남는다. 실행을 요구한다면 최소 권한 환경(allowlist env, isolated interpreter, 네트워크/쓰기 제한 가능 환경)과 실행 계약을 마련하고, 그렇지 않으면 정적 import/AST 검사와 별도 신뢰된 sandbox 검증으로 분리해야 한다.

- **[주의]** hook 검증의 timeout은 `validate_packaged_runtime()`에서 `subprocess.TimeoutExpired`를 `ValueError`로 변환하지 않는다. `prepare-release`는 넓은 예외 처리로 staging을 정리하지만, `release-audit`은 `TimeoutExpired`를 포착하지 않아 `invalid release artifacts: ...`라는 집계 오류 대신 traceback으로 종료된다. 운영자가 audit 결과를 일관된 artifact 실패로 처리하기 어렵다.

## 즉시수정

- `validate_packaged_runtime()`에 ZIP 해제본의 이전 경로 문자열 검사를 추가하고, source Runtime에도 같은 검사를 적용한 뒤 `prepare-release`가 ZIP 생성 전에 실패하도록 한다. 검사는 금지 대상 목록을 한 곳에 정의하고, 텍스트가 아닌 파일은 안전하게 건너뛰거나 명시적으로 처리해야 한다.

- 테스트에 다음 실패 케이스가 없다: source Runtime에 이전 경로 문자열이 있을 때 prepare-release 거부, ZIP 내부 파일에 그 문자열이 있을 때 audit 거부, `session_start.py`/`code_gate.py` 누락·nonzero·timeout일 때 prepare-release와 audit의 오류 형식. 현재 테스트 helper가 두 개의 항상 성공하는 인공 hook을 주입하므로 실제 Runtime hook의 실행 계약은 검증하지 못한다.

- hook timeout을 `validate_packaged_runtime()`에서 포착해 설명 가능한 `ValueError`로 정규화하고, audit의 artifact별 오류 집계가 유지되는지 테스트한다.

## 조용한 결정

- 이전 구조에서 자동 변환하지 않고 `.mpa/runtime` 부재를 오류로 처리한 결정은 코드와 install/deployment 문서에 반영되어 있다. 다만 위 preflight 범위를 config/backups까지 확장할지, 아니면 runtime만 필수로 명문화할지는 운영 계약으로 확정해야 한다.

- `.mpa/config/config.toml`은 deploy migration·rollback snapshot 대상이 아니지만, 현재 구현은 이를 수정하지 않으므로 값 보존 자체는 우연히 유지된다. 향후 TOML migration을 다시 도입할 여지가 있다면 backup/rollback 제외를 명시적 불변식과 테스트로 고정해야 한다.

## 가정검증

- 계획의 “이전 경로 구조를 사용하는 배포 대상은 없다”는 구현으로 검증되지 않는다. current-layout 부재 대상의 dry-run 거부 테스트는 있으나, 실제 대상 inventory 또는 legacy 경로가 존재하는 대상에 대해 파일 변경 없이 거부되는 deploy preflight 테스트는 없다.

- source/runtime 동기화와 새 immutable bundle의 실제 검증은 이 검토 범위의 테스트에서 증명되지 않는다. 테스트는 helper가 만든 최소 Runtime만 패키징하며, 현재 Runtime의 두 실 hook을 대상으로 한 prepare-release/release-audit 회귀 검증이 없다.
