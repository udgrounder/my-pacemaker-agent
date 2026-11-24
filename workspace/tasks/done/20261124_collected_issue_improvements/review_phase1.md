## 검토 결과

- 대상: `inputs --stage review1` 승인·설계·검증 기준과 지정 실제 소스. plan 전체·진행/검증 결과·changelog·전체 diff·기존 비평은 읽지 않았다.
- 판정: **수정 필요**. 생성 hook 명령의 루트 탐색 실패 처리에서 승인 기준 불일치 1건을 재현했다.
- 방법: 정상·실패 경로 추적, 실제 생성 명령 실행, 지정 회귀 테스트, 관련 source/dist 바이트 대조. 제품·테스트·계획·memory는 변경하지 않았다.

### ✅ 정합성 확인

- A1/A2 정상 경로: 물리적 Runtime 소유 루트와 요청 cwd를 분리한다. `project_root.py:11-21,26-47`, `code_gate.py:359-361`을 확인했다. 공백 경로·nested cwd·상대 파일·중첩 Git·외부 cwd/환경변수·symlink 경계와 선택 critical 승인/해시의 실패 경로는 `test_hook_project_root.py` 13개 테스트로 확인했다. 생성 Claude/Codex 명령의 정상 실행도 포함한다. 아래 결함에 해당하는 wrapper 실패 경로는 제외한다.
- A3: `install.py:394-487`의 정확한 구형 명령 매칭·원본 변경 대조·임시 저장·기존 권한 보존을 확인했다. `test_install.py` 26개가 통과했으며 사용자 hook/추가 필드/순서·알 수 없는 명령·손상 설정·저장/교체 실패·명시적 repair 실행의 보존 검증을 포함한다.
- B1/B2: `core/agent_rules.md:17-22`, `inject/layer1_implement.md:96`, `inject/layer1_review.md`의 1.6이 같은 적용 경계를 사용한다. HTTP 헤더 로그 변경과 비 HTTP 스크립트 예외 로그 변경에는 정상·실패 경로 점검이 적용되고, 로그와 무관한 코드 및 일반 문서에는 일괄 점검/새 도구 설치를 요구하지 않는다. 특정 마스킹 구현이 완성됐다는 판정은 하지 않았다.
- C1/C2: `inject/layer1_design.md:139`와 `layer1_review.md`의 1.7을 대조했다. 준비 절차가 빠진 이동 문서는 검증 대상이고 유효한 운영 문서 링크는 허용한다. 외부 인프라가 없는 모듈에는 무관한 준비 절차를 강제하지 않으며 현재 서비스가 불명확한 문서는 식별 대상으로 남는다.
- D1/D2/D3: `core/agent_rules_detail.md:191-198`, `inject/layer2_checkpoint.md:150-186`을 대조했다. 정상 완료는 상세 결과 저장·보고 뒤 날짜 한 줄을 기록한다. 제안·중단·미완료와 결과 저장 실패에는 새 마커를 쓰지 않는다. 프로젝트 지정 위치/동일 점검 기존 문서 우선, 같은 날 별도 점검 덮어쓰기 방지, 미해결 방법론/기능 항목의 연결 구분이 명시돼 있다. 실제 Layer 2 점검·과거 자산 이관은 수행하지 않았다.
- 아키텍처: 소유 루트 helper, 사용자 자산 보존, 명시적 hook repair, source/dist 구분과 모순되는 추가 변경은 지정 소스에서 발견하지 못했다. `contracts.md`는 존재하지 않았다.
- 검증 실행: `python3 -m unittest discover -s tests -p '<파일명>'`으로 `test_hook_project_root.py` 13개, `test_install.py` 26개, `test_plan_hash.py` 53개, `test_policy_consistency.py` 16개, `test_structure_loading.py` 19개, 합계 **127개 통과**. 전체 suite 실행 여부는 이 1차 검토의 근거에 포함하지 않는다.
- 관련 source/dist 10개 파일의 바이트가 일치했다: helper, 세 hook, 두 core 문서, 네 inject 문서. 구조 검증 테스트도 통과했다.

### ⚠️ 주의 필요

- 실제 Claude/Codex 호스트가 hook을 호출하고 exit 2를 어떻게 표시·처리하는지는 미확인이다. shell 명령의 실제 반환 코드는 아래처럼 확인했지만 호스트의 SessionStart/Stop 차단 여부를 실측했다고 주장하지 않는다. `install.md:251`도 실제 호스트 연동을 별도 확인 대상으로 명시한다.

### 🚨 즉시 수정 필요

- **R1 / [P2] 생성 wrapper의 루트 탐색 실패가 warn/off 및 비차단 세션 hook에서 모두 exit 2가 된다.**
  - 재현 조건: 상위 경로에 유효한 `.mpa/runtime/core/agent_rules.md`가 없는 cwd에서 `install._hook_cmd(script, agent)`가 반환한 명령 전체를 실행한다. Runtime의 core marker가 누락된 설치, 또는 해당 설치의 상위 탐색 범위 밖 cwd에서 실행되는 경우다. 입력은 `{}`이며 실제 비밀값이나 프로젝트 자산을 사용하지 않았다.
  - 파일/줄 근거: `install.py:57-62`는 script·`MPA_GATE` 구분 없이 루트 실패에 `exit 2`를 실행한다. hook 본문의 `project_root.py` 오류 정책에 도달하지 못한다. 반면 `code_gate.py:350-365`는 off에서 미검사 exit 0, warn에서 경고 exit 0이고 `session_start.py:189-193`, `turn_end.py:49-53`은 루트 오류 진단 후 정상 반환하도록 되어 있다.
  - 실제 실행: 임시 빈 디렉터리를 cwd로 하고 `subprocess.run(install._hook_cmd(script, 'claude'), shell=True, input='{}', env={**os.environ, 'MPA_GATE': mode}, text=True, capture_output=True)`를 실행했다. `script`가 `code_gate.py`, `session_start.py`, `turn_end.py`이고 `mode`가 warn/block/off인 9개 조합 **전부 returncode=2**, stderr는 `MPA Runtime root not found`였다. 두 agent가 동일 wrapper 분기를 사용한다(`install.py:55`).
  - 기대값: 설계의 「루트·경계 오류의 기대값」에 따라 code_gate는 warn=경고/0·block=진단/2·off=미검사/0이며, SessionStart/Stop 루트 실패는 진단/0이어야 한다. warn의 critical 검사 미확인 설명도 현재 wrapper 진단에는 없다.
  - 영향: 설치 명령을 통해 실행하면 hook 본문에 구현한 비차단·off 정책이 실패 경로에서 보존되지 않는다. 직접 hook 실행 테스트가 통과해도 생성 명령 경로는 기준을 충족하지 못한다. 호스트가 실제 종료를 막는지는 위 미확인 항목으로 구분한다.
  - 수정 권고: 생성 wrapper의 루트 실패도 script 종류와 gate 강도에 맞는 종료 코드·진단을 반환하게 한다. code_gate warn에는 critical 검사 미확인을 명시한다. 생성 명령 전체를 Runtime 탐색 실패 상태에서 실행하는 Claude/Codex 회귀 사례를 추가한다. 정상 탐색과 cwd 유지·정확한 기존 명령 이관의 호환성도 유지한다.

### 📝 조용한 결정 목록

- 환경변수나 Git 최상위 대신 가장 가까운 Runtime을 찾고 물리적 script 위치를 상태 소유자로 삼음 / 판단: **의도적 위임**. 설계 기준에 명시된 선택이다.
- 기존 설치에 일반 재설치를 허용하는 대신 `--repair-hooks`를 제공함 / 판단: **의도적 위임**. 명시 실행으로 관리 명령만 갱신하고 배포의 사용자 설정 보존 경계를 유지한다.
- wrapper의 모든 탐색 실패를 exit 2로 통일함 / 판단: **비가시적 위임**. 승인된 실패 기대값과 달라 R1로 분류했다.

### 🔍 에이전트 가정 검증

- 가정 1: 고정 Runtime hook 위치로 소유 프로젝트를 식별할 수 있다 / 결과: **유효** / 영향: 없음. physical resolve와 core marker 검사 및 symlink fixture로 확인했다. 복사 위치가 조건을 충족하지 않으면 진단하는 helper 동작도 확인했다. wrapper 실패 정책은 별도 R1이다.
- 가정 2: hook 입력 cwd는 하위 작업 폴더일 수 있다 / 결과: **유효** / 영향: 없음. nested cwd에서 절대/상대 파일 요청과 생성 명령 cwd 누락 사례를 실제 실행했다.
- 가정 3: 호스트 입력은 agent별로 다를 수 있다 / 결과: **유효한 방어적 전제**, 실제 호스트 차이는 미확인 / 영향: 현재 설계 변경 필요 없음. cwd 유무를 fixture에서 확인했으며 실제 호스트 입력을 관측했다고 주장하지 않는다.

권장 다음 행동: R1 수정 후 생성 wrapper 실패 경로 재검증. 이후 2차에서 실행 기록·changelog와 대조한다.
