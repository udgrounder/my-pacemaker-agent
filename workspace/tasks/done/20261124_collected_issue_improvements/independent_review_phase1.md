## 검토 결과

- 대상: 승인된 A/B/C/D 요구사항과 `install.py`, Runtime의 `project_root.py`·`code_gate.py`·`session_start.py`·`turn_end.py`, 관련 core/inject 규칙, `install.md`, `docs/mpa-internal-structure.md`, 지정된 5개 테스트 파일.
- 기준: `python3 .mpa/runtime/hooks/task_documents.py inputs workspace/tasks/active/20261124_collected_issue_improvements/plan.md --stage review1`의 승인·설계·검증 발췌. plan 전체, 구현 진행·검증 결과, changelog, 이전 critique/review, 전체 diff는 읽지 않았다. `workspace/memory/shared/architecture.md`를 대조했으며 contracts.md는 없었다.
- 판정: **일반 mv 명령의 개행 경계 처리에 P2 결함 1건. 해당 부분 수정 및 재검증 권장.** 지정 회귀 테스트 129개는 통과했으나 아래 독립 반례는 포함하지 않았다. 실제 Claude·Codex 호스트의 자동 hook 호출은 미확인이다.

### ✅ 정합성 확인

- A의 Runtime 소유 루트와 실행 cwd 분리, 하위/외부 cwd 및 환경변수와 소유 상태 구분, 실제 Runtime symlink 소유권, 경계 밖 파일의 일반 소스 취급을 코드와 임시 Runtime 실행으로 확인했다. warn/block/off와 선택 critical 미승인·해시 불일치, 정상 승인 회귀도 지정 테스트에서 확인했다.
- 설정 갱신은 정확히 식별한 기존 명령만 교체하며 사용자 명령·matcher·추가 필드를 보존한다. JSON 임시 저장, fsync·권한 보존, 원본 바이트 대조 후 replace의 실패 경로와 훼손 JSON·symlink 보존을 설치 테스트에서 확인했다. 별도 hook 갱신 명령의 대상/권한은 승인된 A3 범위와 대응한다.
- B: core와 구현·검토 지침이 로그/외부 호출 변경을 조건으로 정상·실패 경로, 헤더·URL·본문·예외·오류 응답을 포함한다. HTTP·비 HTTP 개발 스크립트에는 적용되고, 로그와 무관한 코드·일반 문서에는 일괄 점검을 요구하지 않는 규칙으로 해석된다. 실제 마스킹 기능은 이번 구현 대상이 아니므로 구현됐다고 판정하지 않는다.
- C: 공용화/이동 시 새 소비자의 도입·운영 준비를 완료 기준과 검토 항목에 연결한다. 준비 절차 누락 문서는 보완 대상이고 유효한 공통 운영 문서 연결은 허용되며, 외부 인프라가 없는 모듈에는 무관한 인프라 절차를 강제하지 않는다. 실제 서비스 식별과 혼동 가능할 때만 대안 비교라는 경계도 대응한다.
- D: core 상세 규칙과 Layer 2 지침 모두 상세 결과·미해결 상태를 결과 문서에 두며 INDEX에는 날짜 한 줄만 남긴다. 프로젝트 지정 경로/같은 점검 기존 문서 우선, 같은 날 별도 점검 덮어쓰기 방지, 방법론 개선만 issue 연결, 저장 실패 시 새 마커 금지가 대응한다. 제안·중단·미완료에는 마커를 남기지 않으며 기존 완료 기준·주기를 바꾸지 않는다. 실제 점검 결과 문서나 INDEX를 생성·편집하지 않았다.
- source/dist 동일성은 `test_structure_loading.py`의 전체 Runtime 파일 parity 검사 통과로 확인했다. 외부 프로젝트 배포·릴리즈 생성·사용자 자산 자동 변경은 수행하지 않았다.

### ⚠️ 주의 필요

#### [P2] 개행 뒤의 명령 인수가 mv 목적지로 합쳐져 완료 승인 검사가 생략됨

- 위치: `.mpa/runtime/hooks/code_gate.py:294`–`310`, 특히 `lexer.whitespace_split = True`와 `tokens[index + 1:]`의 명령 경계 처리. 동기화된 dist에도 동일하게 적용된다.
- 재현 전제: 실제 Runtime을 임시 프로젝트의 `.mpa/runtime/`에 복사한다. `workspace/tasks/active/example/plan.md`는 `상태: 설계 완료`, CURRENT_TASK는 example이다. 프로세스와 입력 cwd는 해당 프로젝트의 `workspace/tasks`이고 `MPA_GATE=block`이다.
- 입력:

```json
{"tool_name":"Bash","cwd":"<임시 프로젝트>/workspace/tasks","tool_input":{"command":"mv active/example done/\nprintf finished"}}
```

- 실제 결과: exit 0, stdout/stderr 모두 빈 문자열. 같은 입력을 설치 도구가 생성한 Claude·Codex wrapper로 실행해도 두 agent 모두 동일하다. hook은 입력 문자열만 검사했고 실제 mv를 실행하지 않았다.
- 기대 결과: 뒤의 `printf`와 무관하게 첫 줄의 단순 `mv active/example done/`에 대해 `완료 승인` 누락을 판정해 block 모드 exit 2를 반환해야 한다. 첫 줄만 전달하거나 `; printf finished`로 연결하면 현재도 exit 2다.
- 원인: shlex가 따옴표 밖 개행을 whitespace로 제거하므로 토큰이 `['mv', 'active/example', 'done/', 'printf', 'finished']`가 된다. operand 수집이 다음 명령까지 진행하고 `finished`를 목적지로 선택한다. done 경로가 아니라고 판단해 상태 조회를 생략한다.
- 영향: 승인된 일반 Bash mv 감시에서 흔한 여러 줄 명령이 동일한 이동 요청임에도 경고·차단을 우회한다. 루트/하위 cwd 차이 문제와 별개로 이번 수정된 토큰화 경로의 기능 누락이다. 실제 호스트가 Bash에 이 hook을 호출하는지는 이 재현으로 증명하지 않는다.
- 수정 방향: 지원하는 단순 명령의 따옴표 밖 개행을 명령 경계로 보존해 `mv` operand 수집을 끝낸다. 기존 따옴표/공백 경로 처리, `;` 경계, warn/block/off를 유지하며 루트·하위 cwd와 두 생성 wrapper에 개행 사례를 추가 확인한다. shell expansion·명령 치환·전체 shell 해석을 새 요구사항으로 부과하는 지적은 아니다.

독립 실행 원문 발췌:

```text
agent=claude suffix='' exit=2
agent=claude suffix='; printf finished' exit=2
agent=claude suffix='\nprintf finished' exit=0 stdout='' stderr=''
agent=codex suffix='' exit=2
agent=codex suffix='; printf finished' exit=2
agent=codex suffix='\nprintf finished' exit=0 stdout='' stderr=''
```

exit 2의 stderr 원문:

```text
완료 처리 차단: 'example' plan.md 상태가 '완료 승인'이 아닙니다 (현재: 설계 완료).
사용자의 명시적 완료 승인 후 plan.md 상태를 '완료 승인'으로 업데이트하세요.
mv 이외의 방법으로 이동해도 동일 규칙이 적용됩니다.
```

### 🚨 즉시 수정 필요

- P0/P1로 확정할 항목 없음. 위 P2는 실제 재현된 기능 결함으로 수정 대상이다.

### 📝 조용한 결정 목록

- 신규 wrapper가 두 agent 모두 현재 작업 폴더의 가장 가까운 Runtime을 찾고 환경변수 대신 물리 스크립트 소유 루트를 사용하는 결정: 승인 설계에 명시된 위임 범위다.
- 훼손·알 수 없는 사용자 설정을 보존하면서 수동 확인 실패를 반환하는 결정: 승인된 설정 보존/실패 보고 기준에 대응한다.
- 확인한 소스·지침에서 추가 사용자 결정이 필요한 명세 밖 변경은 확정하지 못했다.

### 🔍 에이전트 가정 검증

- 고정 Runtime 위치로 소유 루트를 식별 가능: 유효. 물리 경로·core marker를 확인하며 복사/불일치 경로는 미확인 진단으로 처리한다. 임시 Runtime과 symlink 실행 회귀가 대응한다.
- hook cwd가 하위 폴더일 수 있음: 유효. 생성 명령은 cwd를 바꾸지 않으며 상대 파일을 입력/프로세스 cwd에서 해석한다. 루트/하위 및 입력 cwd 누락 사례를 실제 실행했다.
- 호스트 입력은 agent별로 다를 수 있음: 유효한 제한. 생성 wrapper 및 모의 JSON 실행은 실제 호스트 호출 보장이 아니므로 별도로 구분했다.
- 확정된 틀린 가정은 없다. 위 mv 결함은 명령 경계 구현 누락이다.

### 실제 실행한 검증

다음 명령을 각각 직접 실행했다.

```text
python3 -m unittest discover -s tests -p 'test_hook_project_root.py'
Ran 15 tests in 3.602s / OK
python3 -m unittest discover -s tests -p 'test_install.py'
Ran 26 tests in 0.915s / OK
python3 -m unittest discover -s tests -p 'test_plan_hash.py'
Ran 53 tests in 0.127s / OK
python3 -m unittest discover -s tests -p 'test_policy_consistency.py'
Ran 16 tests in 0.402s / OK
python3 -m unittest discover -s tests -p 'test_structure_loading.py'
Ran 19 tests in 1.606s / OK
```

추가로 `tests/test_hook_project_root.py`의 `HookProjectRootTest` 임시 fixture를 읽어 재사용했다. `setUp()` → `active_plan()` → `run_hook(data=..., cwd=case.nested, mode='block', agent=..., generated=True)` 순서로 두 agent와 위 3개 command를 각각 실행하고 fixture를 정리했다. 제품·테스트 파일은 수정하지 않았다.

### 미확인 한계 및 추가 관찰

- 전체 test discover, 실제 호스트 자동 hook 연결, 외부 프로젝트 배포, 실서비스 로그 마스킹은 이번 검토에서 실행하지 않았다. 지정 테스트 통과를 이들의 성공으로 확장하지 않는다.
- malformed 입력도 별도로 실행했다. 정상 절대 `file_path`와 객체형 `cwd`를 보내면 warn 모드에서 `hook 실행 작업 폴더를 확인할 수 없습니다.`라는 additionalContext와 exit 0을 반환하며 선택 critical 검사는 실행하지 않는다. 같은 파일 요청에 정상 문자열 cwd이면 미승인 critical exit 2다. 다만 실제 호스트가 객체형 cwd를 제공한다는 근거는 없어 이를 정상 지원 입력의 확정 결함으로 세지 않았다. 입력 오류 처리 확장을 판단할 경우 이 재현 사실을 참고할 수 있다.
- 정상 경로와 실패 경로를 실제 추적했다. 설정 보존의 임의 비협조 writer 동시 변경·전원 손실에 대한 원자성을 증명하지 않으며, 승인 범위 밖의 전체 shell parser나 신규 보안 도구 도입을 요구하지 않는다.
