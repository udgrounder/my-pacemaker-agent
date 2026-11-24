## 검토 결과

- 대상: 사용자 요청의 일반 `mv` 개행 경계 수정·회귀와 1차 지적 R2-1의 후속 수정. 제품·테스트·plan·memory는 수정하지 않았다.
- 입력: `task_documents.py inputs workspace/tasks/active/20261124_collected_issue_improvements/plan.md --stage review2`의 승인·설계 기준 및 실행 기록, 같은 폴더 `r2_fix_review_phase1.md`, `changelog.md`, 현재 실제 소스. 승인해시는 `reqspec-v1:b4ebda0685c88ace`이며 `task_documents.py inspect`는 `roles-v1`, 선택 문서 없음, `issues: []`였다.
- 확인 소스: `.mpa/runtime/hooks/code_gate.py:288–385`, `project_root.py`, `tests/test_hook_project_root.py`, `install.py:54–75`, `docs/mpa-internal-structure.md:50–54`. 관련 승인·정책·설치·구조 테스트도 실행했다.
- 판정: **이번 수정 범위에서 현재 남은 actionable 결함은 발견하지 않았다.** 1차의 실패 원문은 당시 소스에 대한 유효한 증거로 그대로 유지한다. 구현자 설명이 아닌 현재 소스와 독립 실행 결과로 R2 및 R2-1의 종결을 판단했다.

### ✅ 정합성 확인

#### 원래 R2와 1차 R2-1의 종결 근거

- 원래 실패 입력 `mv active/example done/\nprintf finished`는 현재 `_shell_command_lines`가 따옴표 밖 개행에서 명령을 나누고(`code_gate.py:328–331`), 각 명령 뒤에 경계 토큰을 삽입하는 경로(`346–351`)를 탄다. 뒤 `printf` 인수가 mv 목적지가 되지 않는다.
- 1차 R2-1 입력은 다음과 같다. 아래 코드 블록의 마지막 `printf`는 별도 줄이다.

```sh
printf \ #; mv active/example done/
printf finished
```

- 현재 `305–314`는 이스케이프된 문자를 소비할 때 `word_start=False`를 설정한다. 따라서 이스케이프된 공백 뒤 `#`는 주석이 되지 않고, `324`의 주석 분기는 실제 단어 시작에서만 적용된다. 역슬래시 개행을 제거하는 `307–309`는 기존 단어 경계 상태를 유지한다.
- 위 두 입력을 root/nested, JSON cwd 포함/누락, 직접/생성 Claude/생성 Codex, warn/block/off, 설계 완료/완료 승인 상태에 교차 적용했다. 설계 완료에서는 block exit 2와 완료 처리 진단, warn exit 0과 완료 처리 경고, off 무출력 exit 0이었다. 완료 승인에서는 모두 무출력 exit 0이었다.
- R2-1이 실제 명령인지도 별도 임시 fixture에서 `bash -c`로 재확인했다. shell exit 0, stdout `' #finished'`, `done/example/plan.md` 존재, 원래 active plan 부재였다. 같은 입력의 현재 hook은 block exit 2와 완료 처리 진단을 냈다. 실제 사용자 작업을 이동한 결과가 아니다.

#### 독립 실행 행렬

기존 통합 fixture의 Runtime 복사·실행 helper만 사용하고 입력·기대값은 별도로 구성했다. 공백을 포함한 임시 프로젝트에 현재 Runtime을 복사하여 실제 subprocess를 실행했다.

- 상태 2개 × cwd 2개 × JSON cwd 유무 2개 × 모드 3개 × 실행 경로 3개 × 명령 9개 = **648회**, 실패 0.
- 명령 9개: 단일 mv, mv 뒤 개행·별도 명령, 세미콜론·별도 명령, 빈 줄과 닫히지 않은 따옴표를 포함한 주석, 역슬래시 줄 연속, 인용된 개행 인수 뒤 실제 mv, 이스케이프 공백 뒤 `#`와 실제 mv, 인용 공백 뒤 `#`와 실제 mv, 단어 내부 줄 연속 뒤 `#`와 실제 mv.
- root에서는 `workspace/tasks/active/example`·`workspace/tasks/done/`, nested에서는 `active/example`·`done/`로 같은 실제 경로를 가리켰다. JSON cwd 생략은 wrapper의 실제 프로세스 cwd 보존을 함께 확인한다.
- 음성 대조 **4회**도 모두 무출력 exit 0: 실제 주석 뒤 가짜 mv, 작은따옴표 여러 줄 인수 속 mv, 공백 뒤 역슬래시 줄 연속 다음 실제 주석, 큰따옴표 여러 줄 인수 속 mv.
- 총 **652회**, 기대값 불일치 0. 인용·주석·이스케이프·기본 경계만 검증했으며 변수 확장·명령 치환·shell 전체 실행 지원을 합격 요구로 추가하지 않았다.

#### 경로·승인 보호와 문서

- 정상 경로는 실제 Runtime 소유 루트 확인 → 입력 또는 프로세스 cwd로 상대 경로 해석 → 명령 경계 보존 → active plan의 완료 승인 상태 확인 → 허용이다. 실패 경로는 같은 경로에서 설계 완료 상태 → 모드에 따른 경고·차단이다.
- `project_root.py`의 소유 루트·실행 cwd 분리와 `install.py`의 cwd를 바꾸지 않는 Runtime 절대 경로 실행 계약이 유지된다. 이번 어휘 처리 수정은 선택 critical 승인·해시 검사 의미를 변경하지 않는다. 관련 회귀 테스트에서 승인 누락·해시 불일치·정상 승인·off, 루트 오류·외부 경로·symlink와 생성 wrapper 오류 모드도 재확인했다.
- `docs/mpa-internal-structure.md`는 개행 경계·인용·주석·줄 연속의 구분, 제한된 shell 검사, fixture와 호스트 연동의 차이를 현재 코드와 맞게 설명한다.
- source/dist Runtime **72개 파일**을 바이트 대조하여 불일치 0을 확인했다. 특히 `hooks/code_gate.py`, `hooks/project_root.py`가 동일하다.

### 실행 근거와 기록 대조

각 테스트는 `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p '<파일명>'`으로 실행했다.

| 테스트 | 실행 수 | 결과 |
|---|---:|---|
| test_hook_project_root.py | 18 | OK |
| test_plan_hash.py | 53 | OK |
| test_policy_consistency.py | 16 | OK |
| test_install.py | 26 | OK |
| test_structure_loading.py | 19 | OK |

- 합계 **132건**, 모두 exit 0. 이번 2차는 관련 범위 테스트를 실행했으며 changelog의 전체 294건 실행 수·시간을 독립 재실행한 것으로 주장하지 않는다.
- changelog의 R2 전처리 설명, R2-1의 `word_start` 수정, 회귀 추가는 현재 실제 코드·테스트와 일치한다. 회귀는 `test_mv_command_boundaries_in_direct_and_generated_hooks`, `test_mv_newlines_preserve_quoting_continuations_and_approved_move`, `test_hash_after_escaped_word_character_does_not_hide_next_mv`에 존재한다.
- changelog의 일시 NameError는 현재 테스트 실행에서 재발하지 않는다. 이는 제품 R2-1과 구별하며 과거 실패 기록을 제거할 사유가 아니다.
- 기존 R2 실패, 1차 R2-1 실패 및 수정 전 48개 subtest 실패 주장은 해당 원문·이력으로 보존돼 있다. 1차 원문을 최신 무결함 결론으로 덮어쓰지 않았다.
- 현재 plan의 A 구현·R2 재검증 미완료 표시와 `검증 중` 상태는 최종 2차 결과 반영 전의 진행 상태로 읽힌다. 이번 보고를 받은 메인이 현재 결과를 갱신할 대상이며 별도의 제품 결함으로 계산하지 않는다. 승인된 요구사항·해시·완료 조건을 축소한 변경이나 완료 승인·done 이동은 확인되지 않았다.

### 🚨 즉시 수정 필요

- 없음. 1차 R2-1은 현재 코드와 독립 실행으로 해결됨을 확인했다.

### ⚠️ 주의 필요 및 한계

- 추가 actionable 항목 없음.
- 실제 Claude·Codex 호스트의 자동 hook 호출은 이번 검토에서 실행하지 않았다. 복사 Runtime과 생성 shell 명령 전체의 실행 증거이며 호스트 자동 연결을 보장하지 않는다. 이 기존 미확인은 테스트 통과로 종결하지 않는다.

### 📝 조용한 결정 목록

- 새 제품 정책이나 승인 범위 밖 결정은 발견하지 않았다. 제한된 shell 어휘 처리는 승인된 일반 mv 경계 보존 범위로 유지된다.

### 🔍 에이전트 가정 검증

- Runtime 소유 루트와 실행 cwd를 분리하면 root/nested에서 같은 작업 상태를 판정한다: 이번 실제 실행 행렬에서 유효.
- JSON cwd가 없으면 wrapper가 보존한 프로세스 cwd를 사용할 수 있다: 직접·양 agent 생성 명령에서 유효.
- 이스케이프·인용 뒤 `#`의 경계와 역슬래시 개행의 단어 상태를 보존한다: 기존 1차 실패와 추가 독립 변형에서 유효. 과거 틀린 가정과 영향은 1차 파일에 유지한다.
- fixture 실행만으로 호스트 자동 호출을 확인할 수 있다: 채택하지 않은 가정이며 호스트 연동은 미확인으로 유지한다.
