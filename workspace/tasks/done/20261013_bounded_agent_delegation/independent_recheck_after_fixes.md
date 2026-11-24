# 선택적 위임 보완 독립 재검증

지정된 세 기준은 최신 source와 dist에서 모두 충족했다. 최초 확인에서 발견한 minor 단계 도식의 순서 불일치와 단일형 계획서의 실행 결과 유입 두 경로는 수정 후 같은 기준으로 다시 확인했다.

## 입력과 범위

`python3 .mpa/runtime/hooks/task_documents.py inputs workspace/tasks/active/20261013_bounded_agent_delegation/plan.md --stage review1`이 제공한 승인·설계 기준에서 시작했다. 승인 식별자는 `reqspec-v1:3e7fcc16cac22f14`였다. 지정된 훅·Runtime 지침·테스트와 대응 dist 파일을 대조했다. 실제 작업의 `review2`는 CLI 출력에서 제목 존재 여부만 기계적으로 계산했다.

## 1. 일반 위임과 완료 승인

**통과.** 위임 결과는 판단·검증 근거로 쓰고, 완료 확인은 사용자가 하며 메인이 기록하고 처리한다. 공통 완료 절차는 유효한 사용자 확인과 대상 충돌 확인을 거쳐 `상태: 완료 승인`을 기록한 뒤 정합성 확인, 해당 INDEX 행 제거, done 이동 순서로 진행한다. major 검증 지침과 minor fast-path가 이 순서를 따른다. 세션 지침과 용어집도 사용자 확인을 요구한다.

최초 확인에서 minor 도식은 완료 승인 확인을 `완료 승인` 상태 뒤에 표시했다. 최신 도식은 `작성 중 [자동 승인] → 구현 중 ⛔사용자 완료 승인 → 완료 승인 → done`이며 본문과 일치한다. 현재 작업 경로를 확인한 결과는 `active=True done=False`였다.

- 근거 위치는 `.mpa/runtime/inject/agent_delegation.md:24`, `.mpa/runtime/core/agent_rules.md:107`–`125` 및 `:348`–`350`, `.mpa/runtime/core/agent_rules_detail.md:166`–`177` 및 `:487`–`495`다.
- 경로별 근거 위치는 `.mpa/runtime/inject/layer1_implement.md:125`–`136`, `.mpa/runtime/inject/layer1_review.md:340`, `.mpa/runtime/core/session_protocol.md:79` 및 `:93`, `.mpa/runtime/core/glossary.md:14` 및 `:97`–`104`다.
- 승인과 이동은 Runtime 지침을 대조해 판정했다. 사용자 승인 발화를 모의해 실제 작업의 상태·INDEX·경로를 변경하는 검사는 수행하지 않았다.

## 2. 모델 확인 실패와 슬롯 부족의 우선순위

**통과.** `agent_policy.py resolve`의 표준 입력으로 기존 모델 정책 테스트 요청을 변형해 `free_slots=0`에서 각 역할별로 다섯 가지 경우를 실행했다.

| 조건 | `read` | `critique` | `review` | `reason` |
| --- | --- | --- | --- | --- |
| 모델 확인 유효 | `wait` | `wait` | `wait` | `no_slot` |
| 현재 모델 증거 누락 | `direct` | `critique_incomplete` | `review_self_check` | `evidence_missing_or_stale` |
| 호스트가 요청 모델을 덮어씀 | `direct` | `critique_incomplete` | `review_self_check` | `host_override` |
| 설정 지원 미확인 | `direct` | `critique_incomplete` | `review_self_check` | `settings_unconfirmed` |
| 정책상 미허용 모델 | `direct` | `critique_incomplete` | `review_self_check` | `model_not_allowed_or_available` |

슬롯 대기는 모델 증거, 요청 해석, 허용 목록, 설정 확인을 모두 통과해야 나온다. 독립 비평은 미완료 경로에서 기존 생략 확인 절차를 따르고, 독립 검증은 한계를 명시한 자가 검증 경로로 간다. 근거 위치는 `.mpa/runtime/hooks/agent_policy.py:197`–`200` 및 `:230`–`251`, `.mpa/runtime/inject/agent_delegation.md:5`–`9`, `.mpa/runtime/inject/_agent_execution_priority.md:26`–`35`다. 이 결과의 검증 범위는 정책 CLI와 연결 지침이며 실제 호스트가 선택한 모델은 별도 증거가 필요하다.

## 3. 1차 검증에서 실행 결과 격리

**통과.** 승인된 임시 계획서에 기준과 실행 결과 표식을 넣고 `task_documents.py inputs`의 두 단계에서 표식 존재 여부만 비교했다. 최초에는 `## 설계 기준` 아래 `### 실행 결과`와 구형 단일형의 `### 사전 조사` 아래 `#### 실행 결과`가 모두 `review1`에 남았다. 최신 소스는 plan 공통 발췌와 구형 설계 기준 발췌에 모두 `review_basis()`를 적용한다.

| 최신 CLI 입력 표식 | `review1` | `review2` |
| --- | --- | --- |
| 명시 설계 기준 아래 `DESIGN_NESTED_RUN` | `False` | `True` |
| 구형 사전 조사 아래 `LEGACY_NESTED_RUN` | `False` | `True` |
| 구형 실행 계획의 `LEGACY_STEP_RUN` | `False` | `True` |
| 최상위 `TOP_RUN`과 검증 기준 아래 `CHECK_NESTED_RUN` | `False` | `True` |
| `DESIGN_BASIS`, `LEGACY_BASIS`, `CHECK_BASIS` | `True` | `True` |
| 실제 작업의 `검증 결과`·`실행 TODO` 제목 | `False` | `True` |

관련 테스트에서도 역할 문서의 검증 기준·UI 설계 기준이 1차에 남고, 검증 실행·렌더링 결과는 2차에 보존됐다. 근거 위치는 `.mpa/runtime/hooks/task_documents.py:82`–`106`, `:239`–`292`, `:308`–`314` 및 `.mpa/runtime/inject/task_documents.md:55`–`62`다. 2차 검증에서 1차 결과 파일을 추가하는 책임은 호출자에게 있으며 `.mpa/runtime/inject/layer1_review.md:143`–`144`에 유지된다. 실제 2차 결과의 내용과 타당성은 검토 범위 밖이다.

## 실행 결과

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_agent_policy.py` → `Ran 13 tests`, `OK`.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_task_documents.py` → `Ran 21 tests`, `OK`.
- 지정 Runtime 10개 파일을 각각 dist의 대응 파일과 바이트 단위로 비교했다. `source/dist matches: 10/10`.
