# 독립 최종 검증

## 범위와 방법

- 구현 대화, `changelog.md`, 기존 `review_phase1.md`/`review_phase2.md`, `verification.md`는 읽지 않았다.
- `workspace/memory/shared/project_identity.md`, `workspace/memory/shared/architecture.md`, 이 작업의 `plan.md`를 먼저 읽고, `git diff --name-only` 및 실제 변경 파일을 대조했다.
- 대조 범위: 사용자 부담, minor 실행/계획 구분과 최소 확인, 독립 비평·구현 검증 실패 분기, 완료 승인·승인 기록 복구, workflow/inject 진입 경로, hook·승인해시의 보장 범위, source/dist Runtime 일치, `tests/test_policy_consistency.py`.

## 발견 사항

### P1 — MPA Runtime 수정 뒤 설치본을 즉시 동기화하라는 상충 지침

- 근거: `.mpa/runtime/core/agent_rules_detail.md:275`은 MPA 시스템 파일 수정 후 ``dist/`와 설치본 양쪽 동기화 필수`라고 지시한다. 바로 아래 `:277`, 그리고 `workspace/memory/shared/architecture.md:103`은 설치 대상 배포·릴리즈를 사용자 명시 요청 때만 하도록 한다.
- 영향: Runtime 규칙을 수정한 에이전트가 설치 대상까지 자동 갱신해야 한다고 해석하면, 명시 요청 없는 배포 금지와 대상 사용자 자산 보존 경계를 위반할 수 있다.
- 권장 수정: `:275`을 source Runtime의 `dist/` 동기화만 필수로 표현하고, 설치 대상 갱신은 별도 릴리즈/배포 요청과 immutable bundle 절차에 한정한다고 명시한다.

### P1 — minor 구현 직접 진입 시 계획만 요청한 작업을 막는 확인이 없다

- 근거: `.mpa/runtime/core/agent_rules_detail.md:291,295`는 계획만 요청하면 `approve`·구현을 하지 말라고 한다. 그러나 `.mpa/runtime/inject/layer1_implement.md:44-68`은 plan의 실패비용·체크리스트만 읽고 상태와 승인해시를 확인하지 않으며, `:122-126`은 `실패비용: minor`만으로 fast-path와 최소 확인을 시작한다.
- 영향: `layer1_implement.md`를 직접 시작한 워커가 `설계 중`인 minor plan(계획만 요청된 경우)을 실행 요청으로 오인해 구현할 수 있다. 이는 자동 approve를 명확한 실행 요청에 한정한 정책을 우회한다.
- 권장 수정: 구현 전 체크에 minor의 `상태: 구현 중`과 유효한 `reqspec-v1` 승인해시를 확인하는 분기를 추가한다. 둘 중 하나라도 없으면 detail의 minor 절차로 돌아가 실행 요청 여부를 판별하고 구현을 멈추도록 한다. 이 경계를 재현하는 회귀 테스트도 추가한다.

## 확인된 경로

- `core/agent_rules.md`와 detail은 명확한 minor 실행 요청만 자동 approve하고, 계획만 요청은 구현하지 않으며, 완료 확인 뒤에만 done 처리한다고 설명한다.
- `_agent_execution_priority.md`는 독립 비평 실패 시 사용자에게 생략 여부를 확인하고, 구현 검증 실패 시 한계를 밝힌 자가 검증으로 진행하며 미확인 항목을 남기도록 구분한다. critique/review/workflow 문서가 이 정본을 참조한다.
- 완료 승인은 `core/agent_rules.md:331-358`과 `layer1_discovery.md:89-92`에서 보존된다. 승인 기록 누락 복구도 detail `:46-58`에서 기존 승인과 현재 명세·위험이 동일한 경우에만 재사용하도록 제한한다.
- guidebook과 agent spec은 승인해시·hook의 제한된 범위, warn/block/off 차이, 실제 호스트 이벤트 호출·차단·자동 로딩이 미확인임을 명시한다.
- `diff -qr .mpa/runtime dist/.mpa/runtime` 및 `git diff --check`는 성공했다. `python3 -m unittest discover -s tests -q`는 151개 테스트가 통과했고, 새 정책 테스트는 source와 dist의 참조·문구 회귀 및 gate 경계를 검사한다.

## 한계

이 검증은 저장소의 실제 파일과 로컬 단위 테스트·Runtime parity만 대조했다. 호스트가 hook 종료 코드와 컨텍스트 주입을 실제로 수용하는지, 모델이 자연어 정책을 실제 세션에서 준수하는지는 검증하지 않았다.

## 재검증

앞서 기록한 두 P1은 현재 파일 대조 기준으로 해결됐다.

- `.mpa/runtime/core/agent_rules_detail.md:275`은 자동 동기화를 source Runtime → `dist/.mpa/runtime/`로 한정하고, 설치 대상 갱신을 사용자 명시 릴리즈·배포 요청 및 immutable bundle 절차로 제한한다. `personas/mpa_system_designer.md:32`도 동일한 경계를 사용한다.
- `.mpa/runtime/inject/layer1_implement.md:124`은 minor fast-path 시작 전에 `상태: 구현 중`과 유효한 `reqspec-v1:` 승인해시를 모두 확인하게 한다. 하나라도 없으면 구현·최소 확인을 시작하지 않고 minor 경량 절차로 되돌아가 계획 요청인지 명확한 실행 요청인지 판별한다.
- `tests/test_policy_consistency.py:97-109`에 두 경계를 확인하는 회귀 검사가 추가됐다. `/tmp/mpa-independent-final.log`의 전체 단위 테스트 결과는 153개 `OK`다. 재대조한 `diff -qr .mpa/runtime dist/.mpa/runtime`과 `git diff --check`도 성공했다.

이 재검증도 로컬 파일·테스트·parity 범위에 한정한다. 실제 호스트의 hook 통합과 자연어 지침에 대한 모델 준수는 미확인이다.
