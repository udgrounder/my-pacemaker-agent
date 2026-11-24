## 검토 결과

- 대상: `inputs --stage review2`의 승인·설계·실행 기록, `independent_review_phase1.md`, `changelog.md`와 지정된 실제 source 및 관련 테스트 5개.
- 수행: 한국어로 작성하며 코드·식별자·고정 형식을 보존했다. 부모 모델·추론 상속, 별도 override·자식 호출 없음. 구현 대화 없이 받은 파일을 대조했다. 제품·테스트·plan·INDEX·memory는 수정하지 않았다.
- 결론: 새 1차의 P2는 현재 코드에서 독립 재현되어 유지한다. 과거 wrapper 실패 R1의 해결과 현재 개행 실패는 서로 다른 경로다. 기존 테스트 통과는 현재 발견된 결함을 부정하지 않는다.

### ✅ 정합성 확인

- A의 소유 루트와 실행 cwd 분리는 `.mpa/runtime/hooks/project_root.py:11`의 물리 Runtime 식별, `:26`의 실행 cwd, `:36`의 요청 상대화 및 `code_gate.py:359`의 호출에서 확인했다. SessionStart/Stop은 각각 `session_start.py:190`, `turn_end.py:50`에서 소유 루트로 조회한다. 현재 테스트는 nested cwd·외부 cwd·환경변수 불일치·Git·공백·symlink·critical 해시를 실제 임시 Runtime으로 확인한다.
- A3의 알려진 명령 이관은 `install.py:78`, `:476`의 정확한 명령 일치에 한정된다. 사용자 hook·matcher·추가 필드는 유지하며 알 수 없는 수정 명령은 수동 확인 실패로 남긴다. `:404`의 임시 저장·권한 보존·교체와 실패 주입 테스트가 원본 바이트·권한 보존을 확인한다. `--repair-hooks`는 `:655` 이하의 명시 실행 경로이며 Runtime 배포 자동 수정으로 확대되지 않는다.
- B는 `core/agent_rules.md:21`–`22`, `inject/layer1_implement.md:96`, `inject/layer1_review.md`의 개발 로그 보안 절이 정상·실패 경로, 헤더·URL·본문·예외·오류 응답을 다룬다. HTTP/비 HTTP 스크립트에 적용되고 무관한 일반 문서에는 일괄 요구하지 않는다. 프로젝트의 실제 마스킹 기능을 구현했다는 주장은 없다.
- C는 `inject/layer1_design.md:139`와 검토 지침 1.7에 새 소비자의 도입·운영 준비, 해당하는 리소스·권한·배포·확인·장애 대응을 연결한다. 유효한 공통 운영 문서 링크를 허용하고 실제 서비스 식별과 혼동 시 대안 비교만 요구한다. 외부 인프라 없는 모듈에 인프라 구축을 강제하지 않는다.
- D는 `core/agent_rules_detail.md:192`–`198`, `inject/layer2_checkpoint.md:152` 이하에서 결과 문서 경로, 기존 문서 우선, 별도 점검 덮어쓰기 방지, 미해결 상태·연결, 방법론 issue 한정, 저장 실패 시 마커 금지를 일치시킨다. 제안·중단·미완료와 실제 완료를 구별하고 INDEX 날짜 한 줄 및 기존 주기·과거 마커를 보존한다.
- `workspace/memory/shared/architecture.md`의 source 전용 운영 자산·Runtime만 동기화·사용자 완료 승인 전 done 금지와 대조했다. `contracts.md`는 존재하는 경우만 읽는 조건으로 확인했으며 없는 계약을 가정하지 않았다. `install.md`와 `docs/mpa-internal-structure.md:48`–`54`는 명시 hook 갱신과 실제 호스트 미확인 경계를 설명한다.

### ⚠️ 주의 필요

#### [P2 / R2] 개행 명령 경계 소실로 일반 mv의 완료 승인 검사가 생략됨 — 1차 지적 유지

- 위치: `.mpa/runtime/hooks/code_gate.py:294`–`310`, 동일한 dist Runtime. 핵심은 `lexer.whitespace_split = True`와 다음 명령까지 소비하는 operand 수집이다.
- 독립 재현: `tests/test_hook_project_root.py`의 `HookProjectRootTest`를 import하여 `setUp()` → `active_plan()`으로 복사된 실제 Runtime·공백 포함 임시 프로젝트·상태 `설계 완료`·CURRENT_TASK `example`을 만들었다. `cwd=case.nested` (`workspace/tasks`)에서 아래 JSON을 `run_hook`으로 전달했다. hook은 명령 문자열을 검사했으며 실제 mv는 실행하지 않았다.

```json
{"tool_name":"Bash","cwd":"<임시 프로젝트>/workspace/tasks","tool_input":{"command":"mv active/example done/\nprintf finished"}}
```

- Claude/Codex 각각에 직접 스크립트 및 `install._hook_cmd` 생성 wrapper를 실행했다. 각 방식에서 warn/block/off와 단일 명령·`;`·개행의 3종을 조합하여 총 36회 확인했다.

| 명령 꼬리 | warn 실제 | block 실제 | off 실제 |
|---|---|---|---|
| 없음 | exit 0 + 완료 승인 경고 | exit 2 + 완료 승인 진단 | exit 0, 출력 없음 |
| `; printf finished` | exit 0 + 완료 승인 경고 | exit 2 + 완료 승인 진단 | exit 0, 출력 없음 |
| `\nprintf finished` | exit 0, 출력 없음 | exit 0, 출력 없음 | exit 0, 출력 없음 |

- 위 표는 두 agent·직접/생성 명령에서 동일했다. block 정상 진단은 `완료 처리 차단: 'example' plan.md 상태가 '완료 승인'이 아닙니다 (현재: 설계 완료).`이다.
- 기대: 따옴표 밖 개행 뒤 명령과 무관하게 첫 `mv active/example done/`는 warn에서 경고, block에서 exit 2여야 한다. off는 현재처럼 미검사·exit 0이다.
- 원인 추적: 토큰이 `['mv', 'active/example', 'done/', 'printf', 'finished']`가 되어 `finished`가 목적지가 된다. done 경로가 아니라는 `:311` 판단 뒤 상태 조회에 진입하지 않는다. 단일 명령/세미콜론 경로는 `:319` 상태 조회 후 `:330`의 block으로 도달한다.
- 영향: 지원하는 일반 Bash mv의 여러 줄 요청이 완료 승인 경고·차단을 우회한다. 기존 승인·해시 의미 보존과 Bash mv 회귀 확인이라는 A 계약에 관련된다. 악의적 shell 전체 해석이나 명령 치환 지원을 새로 요구하는 지적이 아니다.
- 권고: 지원하는 단순 명령에서 따옴표 밖 개행을 명령 경계로 보존하고, 기존 인용·공백 경로·세미콜론·warn/block/off를 유지한다. 개행 사례를 루트/하위 cwd와 생성 wrapper에 추가 확인한다. 이번 검토에서는 수정하지 않았다.

#### [P3 / W2] 현재 계획의 무결함 결론은 새 실패와 함께 갱신이 필요함

- 위치: `plan.md:187`의 `남은 제품 결함은 없으며`, `:177`–`179`의 현재 검증 요약. `changelog.md:56`의 과거 검증 당시 `남은 제품 결함은 없었다`와 구별한다.
- 재현·근거: 위 R2가 현재 코드에서 독립 재현됐지만 review2 발췌의 현재 상태는 무결함으로 남아 있다. `core/agent_rules_detail.md:100` 이하의 계획·변경 이력 관리 기준은 현재 실패·위험을 현재 plan에 남기도록 한다.
- 실제/기대: 현재 무결함 표현 / 새 R2 미해결과 필요한 재검증을 현재 상태로 표시. 과거 291건 성공 이력과 R1 해결 증거를 삭제하거나 실패였다고 바꾸지는 않는다.
- 영향·권고: 현재 완료 판단에 새 실패가 빠질 수 있다. 메인 담당자가 새 검토 결론을 plan/changelog에 반영할 때 현재 상태를 바로잡는다. 검토자 쓰기 권한 밖이므로 해당 파일은 편집하지 않았다. R2와 별도 제품 결함으로 중복 계산하지 않는다.

### 🚨 즉시 수정 필요

- P0/P1로 확정한 항목 없음. R2는 재현된 P2 수정 대상이며 W2는 그 결과를 반영할 기록 보완이다.

### 📝 조용한 결정 목록

- source 위치로 소유 루트를 결정하고 wrapper가 cwd를 보존하는 선택, 명시적 hook 설정 갱신 경로, 알 수 없는 사용자 명령 보존은 승인된 A 설계와 대응한다.
- 마스킹 방식·새 자동 검사 도입을 프로젝트에 맡기고 C/D를 조건부 문서 규칙으로 처리한 선택도 승인 기준과 대응한다. 추가 사용자 결정이 필요한 명세 밖 조용한 결정은 확정하지 않았다(메타 개수 0).

### 🔍 에이전트 가정 검증

- 설치 Runtime 위치로 소유 루트 식별 가능: 유효. 물리 스크립트 경로·core marker가 근거이며 불일치는 진단한다.
- hook cwd가 하위 폴더일 수 있음: 유효. cwd와 소유 상태 루트를 분리하고 현재 통합 테스트에서 확인한다. R2는 이 가정이 틀린 것이 아니라 명령 경계 처리 누락이다.
- agent별 호스트 입력 차이 가능 및 단위 테스트만으로 호스트 실행 보장 불가: 유효한 제한. 실제 자동 호출은 미확인으로 유지한다.
- 틀린 가정 확정 0건.

### 1차·changelog·실제 source 대조

- 새 1차 `independent_review_phase1.md`의 P2를 설명으로 수용하지 않고 현재 source와 실제 생성 명령으로 재현했다. 판정 유지다.
- `changelog.md:48`–`53`의 R1은 Runtime/스크립트 누락 시 wrapper의 과거 잘못된 exit 2다. 현재 `install.py:58`–`74`와 이번 `test_hook_project_root.py`의 missing Runtime·missing script 회귀 실행은 모드별 exit를 확인하므로 과거 R1 해결 주장은 지지된다. R2를 그 해결의 번복으로 취급하지 않는다.
- `changelog.md:39`의 일반 mv 보완은 단일 명령·세미콜론에 대해 확인되지만 개행까지 충족한다고 확대할 수 없다. 새 R2는 기존 변경 이력에 없는 실패이며 현재 미해결이다.
- `changelog.md:44`의 통합 13건과 `:52`·`:56`의 전체 291건은 시간상 이전 실행 기록이다. 이번에는 지정 5개 파일 129건을 실행했고 모두 통과했다. 전체 291건은 이번 검토에서 다시 실행하지 않았으며 과거 전체 성공을 현재 결함 부재 증거로 사용하지 않는다.
- 승인 기준은 현재 `reqspec-v1:b4ebda0685c88ace`이고 review2 helper가 정상 발췌했다. A/B/C/D 및 사용자 결정·변경 불가 제약은 유지되어 있다. 초기 3건·D 추가·4건 구현 승인·과거 R1/W1 경위는 changelog로 구별되며 완료 기준을 낮춘 변경은 확인하지 못했다. 별도 선택 문서가 없는 것을 누락으로 취급하지 않았다.

### 이번 실행 증빙과 한계

```text
python3 -m unittest discover -s tests -p test_hook_project_root.py
Ran 15 tests in 3.605s / OK
python3 -m unittest discover -s tests -p test_install.py
Ran 26 tests in 1.014s / OK
python3 -m unittest discover -s tests -p test_plan_hash.py
Ran 53 tests in 0.137s / OK
python3 -m unittest discover -s tests -p test_policy_consistency.py
Ran 16 tests in 0.448s / OK
python3 -m unittest discover -s tests -p test_structure_loading.py
Ran 19 tests in 1.643s / OK
```

- 위 검증과 별도로 36회 R2 대조 실행. `test_structure_loading.py`는 source/dist 전체 Runtime parity를 확인한다. 테스트를 위해 사용된 임시 fixture는 정리했다.
- 정상 경로(기존 mv의 warn/block/off)와 실패 경로(개행 우회 및 누락 Runtime의 모드별 진단)를 직접 추적했다.
- 실제 Claude/Codex 호스트의 자동 hook 호출은 여전히 미확인이다. 생성 wrapper에 Bash JSON을 직접 전달한 성공/실패는 호스트의 matcher 선택·자동 연결을 증명하지 않는다. `install.py:102`–`111`의 생성 matcher도 편집 도구 목록이므로 Bash 감시가 자동 연결됐다고 주장하지 않는다. 새 호스트 통합 요구나 사용자 설정 자동 변경을 이번 권고에 추가하지 않는다.
- 실제 설치 프로젝트 배포·릴리즈 생성·실서비스 마스킹·Layer 2 점검 보고서는 실행/생성하지 않았다. 무관한 전체 shell parser·동시 writer 완전 직렬화·전원 손실 원자성도 검증 완료로 주장하지 않는다.
