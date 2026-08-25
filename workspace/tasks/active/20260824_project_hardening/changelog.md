# 태스크 내역서: 20260824_project_hardening

**작업일:** 2026-08-24
**계획서:** `plan.md`

---

## 변경 파일 목록

| 파일 경로 | 변경 유형 | 설명 |
|---------|---------|------|
| `.claude/agents/mpa_pacemaker.md`, `.codex/agents/mpa_pacemaker.toml`, `.agents/rules/mpa_pacemaker.md` | 수정 | source native agent rule의 Runtime import 경로를 `.mpa/runtime`으로 통일 |
| `.claude/settings.json`, `.codex/hooks.json` | 수정 | source hook 명령과 Claude 권한 경로를 현재 Runtime 위치로 수정 |
| `agent-specs/*/files/` | 수정 | clean install이 복사하는 Claude·Codex·Antigravity native rule을 현재 Runtime 경로로 수정 |
| `install.py` | 수정 | 현재 hook 명령을 인식하는 idempotency marker로 변경 |
| `tests/test_install.py` | 수정 | clean-install native wiring 및 current marker 회귀 테스트 추가 |
| `project_config.py`, `release_manager.py` | 수정 | config·Runtime·backup·필수 설치 경로의 symlink 및 package 특수 파일 방어 |
| `tests/test_release_manager.py` | 수정 | Runtime parent·backup symlink와 package 특수 파일 거부 회귀 테스트 추가 |

---

## 상세 변경 내역

### agent wiring과 hook 등록

- **대상:** source 설정, agent spec, `install.py`
- **변경 유형:** 수정
- **내역:** retired `.mpa-workspace` 참조를 활성 `.mpa/runtime` 경로로 바꾸고, 현재 hook 블록을 중복 등록하지 않도록 marker를 맞췄다.

### clean-install 회귀 검증

- **대상:** `tests/test_install.py`
- **변경 유형:** 추가
- **내역:** Claude·Codex·Antigravity clean install에서 root entrypoint·native rule·자동 hook이 현재 Runtime을 참조하고 hook 파일이 존재하는지 검증한다.

### 경로·archive 경계

- **대상:** `project_config.py`, `release_manager.py`
- **변경 유형:** 수정
- **내역:** Runtime·backup 및 install이 생성하는 사용자 루트의 symlink를 사전 거부하고, config path의 symlink는 외부 파일을 읽지 않는 warning으로 처리한다. ZIP extraction은 symlink·traversal뿐 아니라 특수 파일도 거부한다.

---

## 요구사항 명세 대비 변경 사항

| 변경 | 이유 | 명세 영향 | 보고 |
|---|---|---|---|
| current hook marker 회귀 테스트 추가 | 현재 `.mpa/runtime` hook이 이미 등록됐을 때의 중복 등록을 막기 위함 | 없음 | 1단계 완료 보고에 포함 |
| backup·config·package 파일 유형 경계 회귀 테스트 추가 | deploy/rollback이 target root 밖을 읽거나 쓰지 않게 하기 위함 | 없음 | 최소 preflight 완료 보고에 포함 |

---

## 검증 포인트

- [x] 정상 경로 확인: Claude·Codex·Antigravity clean install이 현재 Runtime을 참조한다.
- [x] 실패 경로 확인: retired path가 source 설정·agent spec·install.py에 남지 않는다.
- [x] 실패 경로 확인: Runtime parent·backup·config symlink 및 ZIP 특수 파일이 변경 전 거부된다.
- [x] plan.md 완료 기준 충족 여부: Runtime wiring과 최소 boundary preflight 완료. 전체 계획은 계속 진행 중.
- [x] 독립 검증 후속: config 상위 경로·deploy/rollback symlink·ZIP symlink/type mismatch 회귀 테스트를 보강했다. — install 17개, release manager 51개 통과
