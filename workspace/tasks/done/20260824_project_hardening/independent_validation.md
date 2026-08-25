# 독립 검증 결과

## 실행 명령과 결과

- `git diff --check` — 통과 (exit 0, 출력 없음)
- `python3 -m unittest discover -s tests -p 'test_install.py' -v` — 통과 (16개)
- `python3 -m unittest discover -s tests -p 'test_release_manager.py' -v` — 통과 (48개)

## 통과한 보장

- clean install에서 Claude·Codex·Antigravity의 진입점·native rule과 Claude/Codex hook 설정이 `.mpa/runtime`를 참조하고, 필요한 hook 스크립트가 존재함을 검증한다.
- 현재 `.mpa/runtime/hooks` marker를 이미 등록된 hook으로 인식한다.
- Runtime 상위 `.mpa`, backup, `workspace` symlink는 각각 dry-run·deploy·필수 디렉터리 준비 단계에서 거부된다.
- config 파일 symlink는 외부 파일을 읽지 않고 warning으로 처리되며, ZIP FIFO 같은 특수 파일은 extraction 전에 거부된다.

## 발견한 문제

- **M2 — config 경로의 상위 symlink와 deploy/rollback 경로에서의 거부 동작은 회귀 테스트가 없다.** `project_config.py`의 `_has_symlink_component()`은 `.mpa`, `.mpa/config`, `config.yaml` 모두 검사하지만 `tests/test_install.py:test_config_symlink_is_warning_instead_of_internal_error`는 최종 `config.yaml` symlink만 만든다. 또한 `tests/test_release_manager.py`에는 deploy의 config symlink 및 rollback의 Runtime/backup/config symlink 거부를 호출하는 테스트가 없다. 따라서 구현 의도는 읽을 수 있으나, 관리 경로의 모든 symlink 경계가 실제로 테스트된다는 완료 기준은 충족했다고 판단하기 어렵다.
- **M2 — ZIP 파일 유형 검사 분기 전체가 검증되지 않는다.** `release_manager.py:_extract_runtime()`은 symlink, FIFO를 포함한 특수 파일, directory/file type 불일치를 구분하지만 `tests/test_release_manager.py:test_extract_runtime_rejects_special_file`은 FIFO 하나만 검증한다. symlink 및 type mismatch 분기는 이 변경분에 대한 회귀 증거가 없다.

## 판정

**수정 필요.** 실행된 테스트와 정적 검토에서 즉시 실패하는 구현 결함은 발견하지 못했지만, critical 경계 완료 기준에 필요한 symlink·ZIP 거부 분기 회귀 테스트가 부족하다.
