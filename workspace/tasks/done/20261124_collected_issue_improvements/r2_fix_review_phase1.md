## 검토 결과

- 대상: R2 일반 mv의 개행 경계 수정과 A1의 완료 승인·모드 보호 회귀. `.mpa/runtime/hooks/code_gate.py`, `project_root.py`, `tests/test_hook_project_root.py`, `install.py`의 생성 명령, `docs/mpa-internal-structure.md:50–54`를 직접 확인했다.
- 기준: `task_documents.py inputs .../plan.md --stage review1`의 승인해시 `reqspec-v1:b4ebda0685c88ace`, A1/A3/X1 및 A 설계·검증 기준. plan 전체·실행 기록·changelog·이전 critique/review는 읽지 않았다. architecture의 Runtime 소유 루트·실행 cwd 분리 원칙도 대조했다. shared/contracts.md는 없다.
- 판정: **수정 필요.** 원래 개행 사례는 해결됐지만 새 주석 전처리에 기본 이스케이프 처리 결함이 있어 완료 승인 누락을 차단하지 못한다.

### 🚨 즉시 수정 필요

#### R2-1. 이스케이프된 공백 뒤의 `#`를 주석으로 오인하여 뒤의 실제 mv를 제거함

- 위치: `.mpa/runtime/hooks/code_gate.py:319–322` (`_shell_command_lines`), 호출 경로 339–344. 동기화된 dist에도 같은 코드가 있다.
- 원인: 주석 시작 여부를 `chars[-1].isspace()` 등 직전 원시 문자로 판단한다. `\ `의 공백은 shell 단어 내부의 문자지만 공백 뒤 `#`를 새 주석으로 판정해 그 줄의 `; mv ...`까지 버린다.
- 재현 전제: 임시 프로젝트에 실제 Runtime 복사, `workspace/tasks/active/example/plan.md` 상태 `설계 완료`, cwd `workspace/tasks`, `MPA_GATE=block`.

```json
{"tool_name":"Bash","tool_input":{"command":"printf \\ #; mv active/example done/\nprintf finished"}}
```

- JSON cwd는 생략해 프로세스 cwd를 사용했다. 명시적 nested cwd 입력도 같은 결과다.
- 실제: 직접 code_gate 실행, `install._hook_cmd('code_gate.py', 'claude')`, 같은 Codex 생성 명령 모두 **exit 0, stdout/stderr 빈 문자열**.
- 기대: block은 완료 승인 누락 진단과 exit 2, warn은 완료 절차 경고와 exit 0, off는 무검사 exit 0.
- root cwd에서는 `mv workspace/tasks/active/example workspace/tasks/done/`로 같은 실제 경로를 요청했다. root/nested × warn/block/off × 직접/생성 Claude/생성 Codex 총 18개 모두 무출력 exit 0이라 block 차단과 warn 경고가 누락됐다.
- 실제 실행 증거: 별도 임시 fixture에 done 디렉터리를 만들고 위 명령을 `bash -c`로 실행했다. exit 0, stdout ` #finished`, `done/example/plan.md` 존재, 원래 active plan 부재를 확인했다. 즉 문자열 속 가짜 mv가 아니라 실제로 미승인 작업이 이동하는 입력이다. 사용자 작업 폴더는 이동하지 않았다.
- 영향: 기본 인용·이스케이프·주석·세미콜론 범위에서 완료 승인 보호가 우회된다. 변수 확장·서브셸·shell 전체 실행 지원을 새 요구로 부과한 사례가 아니다.
- 권장: 주석 시작 여부를 이스케이프·인용이 반영된 실제 단어 경계로 판정하고 이 반례를 직접 및 양 agent 생성 명령에 회귀 사례로 추가한다.

### ✅ 정합성 확인

- 원래 실패 입력 `mv active/example done/\nprintf finished`를 포함하여 단일/세미콜론/개행, 주석 속 닫히지 않은 따옴표, 따옴표 안 개행·이스케이프 따옴표, 역슬래시 줄 연속을 독립 구성했다.
- 상태 설계 완료/완료 승인 × root/nested cwd × warn/block/off × 직접/생성 Claude/생성 Codex의 288개 실행은 기대 판정과 일치했다. 생성 명령에는 JSON cwd를 넣지 않아 cwd 보존도 확인했다. 공백이 포함된 임시 프로젝트 경로를 사용했다.
- 위 행렬의 설계 완료는 block exit 2, warn은 완료 절차 경고와 exit 0, off는 무출력 exit 0이었다. 완료 승인 상태에서는 같은 명령 모두 무출력 exit 0이었다.
- 인용된 여러 줄 문자열 속 mv, 주석 속 mv, 인용 문자열의 줄 연속 등 3개 음성 대조군은 무출력 exit 0이었다.
- 정상 경로: 소유 Runtime 루트 → 실행 cwd 상대화 → 개행 경계 토큰화 → active 작업 plan 상태 완료 승인 → 통과. 실패 경로: 같은 경로에서 설계 완료 → warn 경고/strict 차단. R2-1은 이 경로 앞의 주석 전처리에서 실제 mv가 제거되는 별도 실패 경로다.
- `project_root.py`는 Runtime 실제 위치와 실행 cwd를 분리한다. 이번 개행 처리는 승인해시 계산·선택 critical 검사 코드 자체를 변경하지 않는다. 관련 기존 테스트에서 critical 승인 누락·해시 불일치·정상 승인·off 동작을 재확인했다.
- source/dist의 `code_gate.py`, `project_root.py`는 각각 `cmp` exit 0으로 일치했다.

### 실행 근거

각 명령은 `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p '<파일명>'`으로 실행했다.

| 테스트 | 실행 수 | 결과 |
|---|---:|---|
| test_hook_project_root.py | 17 | OK |
| test_plan_hash.py | 53 | OK |
| test_policy_consistency.py | 16 | OK |
| test_install.py | 26 | OK |
| test_structure_loading.py | 19 | OK |

기존 131개 테스트가 통과해도 독립 반례 R2-1은 남는다. 독립 288개 기대 행렬·3개 음성 대조군·18개 반례 행렬은 임시 프로젝트를 만들고 실제 subprocess로 hook 또는 생성 명령 전체를 실행했다. 기존 fixture의 Runtime 준비·실행 helper만 재사용했고 입력과 기대값은 독립 구성했다.

### ⚠️ 주의 필요 및 한계

- 실제 Claude/Codex 호스트의 자동 hook 연결은 이 검토에서 실행하지 않았다. 복사 Runtime과 생성된 shell 명령의 실행 증거이며 호스트의 자동 호출 보장은 아니다.
- shell 전체 해석·확장은 검증 또는 합격 요구 범위로 추가하지 않았다.

### 📝 조용한 결정 목록

- 별도 제품 정책 변경은 발견하지 않았다. R2-1의 원시 문자 기반 주석 경계 추정은 허용 가능한 위임 정책이 아니라 명시된 인용·주석·이스케이프 처리의 구현 결함이다.

### 🔍 에이전트 가정 검증

- Runtime 위치로 소유 루트를 식별하고 cwd는 요청 경로 해석에 사용한다는 가정: 본 검토의 root/nested·공백 경로·생성 명령 fixture에서 유효.
- 호스트 입력이 다를 수 있다는 가정: JSON cwd 포함/누락을 구별해 실행했다. 자동 호스트 호출 자체는 미확인으로 남긴다.
- 일반 shell 주석·이스케이프 전처리로 정상 mv를 보존한다는 코드의 가정: R2-1에서 틀림. 완료 승인 보호의 실제 우회가 발생한다.
