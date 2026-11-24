## 검토 결과

- 대상: `task_documents.py inputs workspace/tasks/active/20261124_collected_issue_improvements/plan.md --stage review2`의 승인 기준·실행 기록, `review_phase1.md`, `changelog.md`, 지정 실제 source와 테스트·아키텍처. 구현 대화·전체 diff는 읽지 않았다. contracts.md는 존재하지 않는다.
- 판정: **제품의 즉시 수정 결함은 발견되지 않았다. R1 해결 확인. 현재 계획 기록 정리 후 테스트 진행 가능.** 실제 호스트 자동 호출은 미확인이다. 사용자 완료 승인 전 done 이동·원본 정리는 허용되지 않는다.
- 실행일: 2026-11-24. source·tests·plan·memory를 수정하지 않았다.

### ✅ 정합성 확인

#### 1차 R1의 수정 확인

- `install.py:54-74`의 현재 wrapper는 Runtime 또는 hook 파일 부재 시 script 종류와 정규화된 MPA_GATE를 구분한다. code_gate off는 출력 없이 0, warn은 critical 검사 미확인 진단과 0, block은 진단과 2이며 session_start·turn_end는 진단과 0이다. 구현자의 설명만으로 종결하지 않았다.
- 별도 임시 빈 디렉터리에서 `subprocess.run(install._hook_cmd(script, agent), shell=True, cwd=directory, input='{}', text=True, capture_output=True, env={**os.environ, 'MPA_GATE': mode})`로 현재 생성 명령 전체를 재실행했다. 양 agent × 세 script × 세 mode, 총 18조합의 실제 결과는 다음과 같다. 진단의 `미확인` 문구와 code_gate off의 무출력도 assert로 확인했다.

| agent | script | warn | block | off |
|---|---|---:|---:|---:|
| claude | code_gate.py | 0 | 2 | 0 |
| claude | session_start.py | 0 | 0 | 0 |
| claude | turn_end.py | 0 | 0 | 0 |
| codex | code_gate.py | 0 | 2 | 0 |
| codex | session_start.py | 0 | 0 | 0 |
| codex | turn_end.py | 0 | 0 | 0 |

- `test_hook_project_root.py`의 현재 15개 테스트도 전체 suite에서 실행됐다. 기존 정상 wrapper의 nested cwd·JSON cwd 누락·상대 파일, 중첩 Git/공백 경로와 실패 Runtime, 추가된 모드 대소문자·주변 공백, hook 파일 누락을 포함한다. hook 파일 누락의 직접 회귀는 Codex 경로이며 두 agent의 생성 wrapper는 같은 분기를 사용한다. 1차의 실패 원문은 보존한다.

#### 승인 기준·기록과 실제 결과

- **A1/A2:** `project_root.py`의 physical script 위치와 core marker 검사, `execution_cwd`·`relative_path`, `code_gate.py`의 호출 순서와 SessionStart/Stop의 소유 루트 조회를 대조했다. 정상 요청은 실행 cwd에서 절대화한 뒤 소유 루트에 상대화한다. 경계 밖·외부 symlink는 workspace 허용으로 처리되지 않고 일반 source 판정 및 선택 critical 검사로 이어진다. 정상 승인·해시 변경·승인 누락, warn/block/off, nested·foreign cwd/환경변수, Bash mv와 done 쓰기 회귀가 실행됐다. shell 전체 해석까지 보장한다는 주장은 없다.
- **A3:** `install.py:78-97,394-496,655-673`과 `test_install.py`를 대조했다. 정확한 관리 명령만 갱신하며 사용자 hook 순서·matcher·추가 필드·미확인 명령을 보존한다. fsync/replace 실패 주입에서 원본 바이트·권한·임시 파일 정리, 명시 repair CLI와 dry-run의 설정 외 파일 보존이 실제 테스트됐다. 원자적 설치 전체 transaction이나 동시 외부 변경의 완전한 직렬화를 주장하지 않는다.
- **B1/B2:** `core/agent_rules.md:17-22`, `layer1_implement.md:96`, `layer1_review.md:227-231`은 HTTP·비 HTTP 로그의 정상·실패 경로와 헤더·URL·본문·예외·오류 응답을 포함한다. 관련 코드 변경에는 확인 의무가 있고 일반 문서·무관 변경에는 일괄 적용되지 않는다. 가상 HTTP 인증 헤더 로그 및 비 HTTP 예외 로그 변경은 점검 대상, 일반 문서는 제외됨을 규칙으로 대조했다. 실제 마스킹 기능 구현이나 새로운 자동 검사 설치 완료로 확대하지 않는다.
- **C1/C2:** `layer1_design.md:139`, `layer1_review.md:233-235`에 준비 절차 누락 문서의 검증, 유효한 공통 운영 문서 연결 허용, 인프라 없는 모듈의 무관 항목 제외, 현재 외부 서비스의 구체 식별·혼동 가능성에 한정한 대안 비교가 대응한다. 원천 프로젝트 재현이나 특정 서비스 사용이 공통 합격 조건으로 추가되지 않았다.
- **D1/D2/D3:** `agent_rules_detail.md:191-198`, `layer2_checkpoint.md:150-186`은 정상 완료의 결과 저장·위치/미해결 상태/연결 보고와 날짜 한 줄 마커, 제안·중단·미완료·저장 실패의 마커 금지, 지정 위치 우선·동일 점검 기존 문서 재사용·같은 날 별도 문서 구분을 유지한다. 미해결 방법론 개선과 기능·설계 항목의 연결도 구분한다. 실제 Layer 2 점검·과거 자산 이관은 이번 검증에서 실행하지 않았다.
- **X1:** `python3 -m unittest discover -s tests`를 실제 실행해 exit 0을 확인했다. 현재 discovery loader의 테스트 수는 291개이며 changelog의 수정 후 수와 일치한다. 관련 helper·세 hook·두 core·네 inject, 10개 source/dist 파일의 바이트를 별도로 assert해 모두 일치했다. 전체 구조 parity 테스트도 suite에 포함된다. 이번 검증은 sync-runtime을 재실행해 배포본을 변경하지 않았다.
- `plan_hash.py check <task>/plan.md`: `일치: reqspec-v1:b4ebda0685c88ace`, exit 0. `task_documents.py inspect <task>/plan.md`: roles-v1, documents=[], issues=[], exit 0. `.plan-renewal.json` 잔존 없음. 선택 문서 없음은 승인된 구성과 일치한다.
- changelog의 구현·설정 보존·R1 수정·호스트 미확인 주장은 현재 코드와 실행으로 뒷받침된다. 1차가 발견한 누락 실패 경로는 수정 이력에 추가됐으며 남은 코드 결함으로 유지할 근거는 없다. 전체 suite에서 출력된 release/deploy 경로는 임시 fixture 경로이며 실제 배포 완료의 증거로 쓰지 않았다. architecture의 source/dist·사용자 자산 보존·완료 승인 경계와 충돌하는 지정 소스 변경은 발견되지 않았다.

### ⚠️ 주의 필요

- **W1 / [P3] 현재 plan의 검증 결과에 승인 전 주장이 현재형으로 남아 있다.** `plan.md:181`은 구현 승인을 미발급이라 쓰고, `182`는 구현 결과를 아직 미검증이라 하며, `183`은 archive 3건 및 승인 후 해시 발급을 미래형으로 남긴다. 현재 프론트매터는 검증 중·유효 승인해시이며 같은 문서의 현재 상태는 4건 구현·독립 검증 중이다. changelog에는 승인 전 경위와 4건 구현·R1 수정 이력이 이미 구분돼 있다. 이는 제품 실패나 승인 무효가 아니라 현재 기록 혼선이다. 권장: 현재 plan에서는 이력으로 보존된 승인 전 주장을 정리하고 수정 후 실제 테스트·미확인·독립 검증 상태로 맞춘다. 요구사항·해시·실패 원본·사용자 완료 승인 대기를 바꾸지 않는다.
- **호스트 연동 미확인:** 실제 Claude/Codex 호스트가 등록 hook을 자동 호출하고 exit 2를 어떻게 처리하는지 관측하지 않았다. 이번 shell 명령·fixture 실행은 호스트 통합 검증을 대체하지 않는다. changelog와 설치 안내도 이 경계를 명시하므로 과장으로 분류하지 않는다. 실행 가능한 호스트 환경에서만 남은 연동 확인을 수행하고 그 전에는 미확인으로 유지한다.

### 🚨 즉시 수정 필요

- 없음. 1차 R1은 위 실제 명령 결과로 해결 확인했다.

### 📝 조용한 결정 목록

- 새로 남은 비가시적 결정 없음. 1차의 nearest Runtime/physical owner와 명시 `--repair-hooks` 선택은 설계·A3 위임 범위와 일치한다. 실패를 exit 2로 통일했던 결정은 제거됐다.

### 🔍 에이전트 가정 검증

- Runtime 고정 위치로 소유 프로젝트 식별: 유효. physical resolve·marker·symlink 실패 경로 및 생성 명령 실행으로 확인했다.
- 입력 cwd가 하위 작업 폴더일 수 있음: 유효. 생성 명령에서 JSON cwd 유무·상대/절대 경로의 판정 동등성을 회귀로 확인했다.
- 호스트별 입력 차이 가능성: 방어적 전제로 유효. 실제 호스트 입력 차이는 미확인이며 테스트 결과로 관측했다고 주장하지 않는다.
- 틀린 가정: 새로 발견된 항목 없음.

권장 다음 행동: W1 현재 기록 정리 후 테스트 진행 가능. 에이전트가 이미 수행한 명령 테스트를 사용자에게 반복시키지 않는다. 실제 호스트 미확인·사용자 결과 확인 경계를 보고하고 완료 승인 전 review 원본·필요 입력을 보존한다.
