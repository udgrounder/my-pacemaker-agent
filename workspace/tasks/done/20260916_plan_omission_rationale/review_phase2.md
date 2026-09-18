# 독립 구현 검토 — phase 2

## 발견 사항

### [P1] major 설계 자기 점검이 생략 사유와 실제 조건을 대조하지 않는다

- **근거:** 완료 기준은 major의 설계 자기 점검과 구현 후 검토가 생략 사유의 적용 조건·작업 사실을 대조해야 한다고 정한다([plan.md:37](plan.md#L37)). 그러나 `layer1_design.md`의 새 완료 기준은 표에 조건과 작업 사실을 **기록**하라고만 하며([layer1_design.md:115](../../../../../.mpa/runtime/inject/layer1_design.md#L115)), 작성 절차도 표를 채우라는 지시만 둔다([layer1_design.md:132](../../../../../.mpa/runtime/inject/layer1_design.md#L132)). 실제 조건과의 일치 검토는 구현 후 검토인 `layer1_review.md`에만 있다([layer1_review.md:192](../../../../../.mpa/runtime/inject/layer1_review.md#L192)). changelog의 “major 계획 작성과 자기 점검에 생략 사유 확인을 추가”라는 설명([changelog.md:13](changelog.md#L13))은 기록 의무와 대조 검토를 같은 것으로 취급한다.
- **영향:** 구현 승인 전에 major 계획의 표가 형식적으로 채워졌지만 해당 섹션을 실제로 생략해도 되는지 검증되지 않을 수 있다. 구현 후 발견되면 승인 전 검토에서 잡을 수 있었던 오류가 실행 중 변경 기록 또는 명세 변경으로 늦게 전파된다.
- **1차 검토와의 관계:** phase 1의 네 지적에는 없던 완료 기준 미충족이다. phase 1의 적용 목록·분류 근거·minor 후속 기록 보완과 별개로 남는다.
- **수정 필요 여부:** 필요. `layer1_design.md`의 설계 완료 자기 점검 또는 major 작성 절차에 표의 각 행을 실제 적용 조건·작업 사실과 대조하는 명시적 확인을 추가하고, 그 문구가 빠지면 실패하는 파일별 회귀 사례를 추가해야 한다.

### [P2] 형식적 생략 사유를 막는 회귀 검증이라는 changelog 주장이 실제 테스트에 없다

- **근거:** 템플릿은 개별 사유가 `없음`·`해당 없음`·`불필요`만으로 이루어지면 안 된다고 규정한다([plan_template.md:88](../../../../../.mpa/runtime/templates/plan_template.md#L88)). changelog는 “형식적 사유” 실패 경로를 정책 검사로 확인했다고 적었다([changelog.md:37](changelog.md#L37), [changelog.md:52](changelog.md#L52)). 하지만 `test_todo_policy.py`는 해당 금지 문구나 `[적용 조건] — [작업 사실]` 형식을 검사하지 않고([test_todo_policy.py:26-35](../../../../../tests/test_todo_policy.py#L26-L35)), `test_policy_consistency.py`의 파일별 요구 문구와 음성 사례도 생략 사유 금지 규칙을 포함하지 않는다([test_policy_consistency.py:68-93](../../../../../tests/test_policy_consistency.py#L68-L93), [test_policy_consistency.py:145-150](../../../../../tests/test_policy_consistency.py#L145-L150)).
- **영향:** 템플릿에서 형식적 사유 금지 또는 구체 사유 형식이 빠져도 추가된 정책 회귀는 통과한다. 이번 변경의 핵심 실패 경로가 changelog가 주장한 수준으로 보호되지 않는다.
- **1차 검토와의 관계:** phase 1의 네 번째 지적은 파일·절차별 검사와 음성 사례를 요구했다. 후속 변경 기록 열에 대해서는 보완됐지만, changelog가 함께 주장한 형식적 사유 실패 경로에는 같은 수준의 검증이 없다.
- **수정 필요 여부:** 필요. 금지된 단독 사유와 조건·작업 사실 형식이 없는 사유를 각각 제거·변형한 입력에서 정책 검사가 실패하도록 회귀 사례를 추가하거나, changelog의 실패 경로 확인 주장을 범위에 맞게 정정해야 한다.

### [P2] Runtime 현재 릴리즈 포인터 변경이 changelog와 계획의 변경 목록에서 빠졌다

- **근거:** 실제 변경에는 source와 dist의 `.mpa-version`이 모두 `20260908031548-d2e08dc8`에서 `20260916031907-05597730`으로 바뀐 내용이 있다([.mpa-version:1](../../../../../.mpa/runtime/.mpa-version#L1), [dist .mpa-version:1](../../../../../dist/.mpa/runtime/.mpa-version#L1)). changelog의 변경 파일 목록은 source `.mpa/runtime/.mpa-version`을 열거하지 않고([changelog.md:8-19](changelog.md#L8-L19)), 계획의 수정 대상 파일 목록에도 없다([plan.md:120-131](plan.md#L120-L131)).
- **영향:** Runtime 내용 변경과 별개인 현재 릴리즈 참조의 갱신 이유·범위가 작업 이력에서 추적되지 않는다. 특히 계획이 release 또는 deploy 생성을 제외한 상태이므로([plan.md:29-30](plan.md#L29-L30)), 검토자는 이 포인터 변경이 동기화의 부수 효과인지 별도 릴리즈 판단인지 알 수 없다.
- **수정 필요 여부:** 필요. changelog에 source·dist 버전 포인터 갱신과 발생 이유를 기록하고, 계획과 불일치하지 않는지 작업 기록에서 명확히 해야 한다.
