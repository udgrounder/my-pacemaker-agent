# Release Preparation Profile

`dist/.mpa-workspace/` allowlist의 해시만 release ID 입력으로 사용한다. 준비 시 같은 asset map을 `workspace/releases/packages/<release-id>/`에 불변 스냅샷으로 저장하고 manifest는 그 스냅샷과 함께만 유효하다. Git은 scoped diff와 HEAD를 보조 정보로만 기록하며 release를 차단하지 않는다.

`__pycache__`, `.DS_Store`, symlink는 Runtime release 자산으로 허용하지 않는다.

배포 전에 `release_manager.py release-audit`으로 모든 활성 manifest와 package의 대응 관계를 확인한다. package를 복원할 수 없는 과거 manifest는 활성 manifest 경로에 두지 않고 legacy 이력으로 분리한다.
