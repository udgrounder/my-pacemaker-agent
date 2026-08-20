## 2차 메타 검증

판정 기준: `plan.md`의 읽기 전용 감사 범위와 권위 모델에 따라, `audit_report.md` 및 `review_phase1.md`의 주장을 실제 실행·설명·배포 근거에 다시 대조했다. 이 태스크에는 changelog가 없으므로 변경 이력은 판정에 사용하지 않았다.

### 🚨 즉시 수정 필요

1. 완료 승인 규칙 충돌은 보고서가 적은 두 문서를 넘어 실행 inject까지 존재한다.
   - `.mpa-workspace/core/agent_rules.md`의 major/minor 상태 모델은 모두 `완료 승인`을 거쳐서만 `done`으로 이동하게 한다.
   - `.mpa-workspace/hooks/code_gate.py:11-18, 251-261`도 완료 이동의 상태 계약을 `완료 승인`으로 둔다. 단, 기본 `MPA_GATE=warn`에서는 경고이고 `block`일 때만 차단이다.
   - 이에 반해 `.mpa-workspace/inject/layer1_discovery.md:88,126`은 `검토 완료` 상태에서 `done/` 이동을 지시한다. `guidebook/guidebook.md:841,871,1074`도 같은 직접 이동을 반복한다.
   - 따라서 보고서 1·2번의 drift 판정은 맞지만, 권장은 `session_protocol.md`·`architecture.md`·guidebook만이 아니라 `layer1_discovery.md`와 동기화된 `dist/.mpa-workspace/inject/layer1_discovery.md`까지 포함해야 한다. source와 dist의 해당 inject는 현재 동일하다.

2. `.mpa-workspace` 직접 수정 금지는 절대 표현이라 허용된 MPA 수정 경로와 충돌한다.
   - `workspace/memory/shared/architecture.md:86`은 직접 수정을 금지한다.
   - 같은 Runtime의 `.mpa-workspace/core/agent_rules.md`는 “규칙 바꿔줘”를 MPA 파일 수정 절차로 라우팅하며, README도 `.mpa-workspace`를 `mpa_system_designer` 프로세스로 직접 수정 가능하다고 설명한다 (`README.md:208,220`).
   - 이 항목을 단순 표현 정리 후보로 둔 보고서 평가는 약하다. “설치 대상의 비승인 Runtime 직접 수정 금지, source의 승인된 MPA 수정 태스크는 허용”처럼 경계를 명시하는 수정이 필요하다.

### ⚠️ 주의 필요

1. 보고서가 `hooks/code_gate.py`라고 쓴 경로는 부정확하다. 실제 파일은 `.mpa-workspace/hooks/code_gate.py`다. 또한 hook은 상태 계약을 확인하지만 기본값이 `warn`이므로, “요구한다”는 문구는 기계적 강제와 절차상 의무를 구분해 써야 한다.

2. OpenAgent의 자동 wiring이 완결되지 않은 관찰은 사실이다. `install.py:32,36,448-450`은 config map·hook wiring을 보류하고 spec 질의 안내만 출력하며, `agent-specs/openagent/spec.md`의 감지·폴더·설치 처리는 미정/TBD다. 다만 README와 guidebook은 `openagent`를 지원 agent로 열거하는 동시에 `spec.md 질의로 결정`, `감지 불가 → 사용자 확인`이라고 명시한다 (`README.md:73-75`, `guidebook/guidebook.md:553,1174`). 그러므로 즉시 “자동 통합 결함”으로 확정하기보다, 정식 자동 지원인지 수동 설정 지원인지의 제품 약속을 먼저 결정해야 한다.

3. 외부 표준 용어 절차 부재를 다음 스프린트 필수 항목으로 승격한 근거는 부족하다. 계획은 이미 공식 출처를 확인하지 못하면 `외부 표준 미검증`으로 표기하고 내부 명확성만 판정하도록 정한다 (`plan.md:66,97-103`). 보고서는 이 계획상 라벨을 신규 요구처럼 제안하지 말고, 해당 라벨을 적용했는지 여부만 기록해야 한다.

4. 배포본 완결성 결론은 실체가 있으나 보고서의 증거 위치가 부족하다. 현재 release receipt와 manifest의 validation에는 66개 테스트 성공 및 dry-run·deploy·rollback 출력이 남아 있고, `tests/test_release_manager.py:86-122,149-197,254-293`은 사용자 소유 경로 보존·runtime config rollback·marker 검증·rollback 실패 복구를 직접 검사한다. 따라서 “근거가 전혀 없다”는 1차 검토의 강한 해석은 맞지 않는다. 다만 보고서는 manifest/receipt와 테스트 파일·명령을 명시해 재현 가능하게 보강해야 한다.

### 📝 조용한 결정

- 실행 규칙과 inject가 충돌할 때 `agent_rules.md`를 정본으로 삼는다는 보고서의 권위 모델은 계획과 부합한다. 다만 수정 대상과 재검증 범위를 명시하지 않은 채 결론만 낸 것은 부족하다.
- OpenAgent 지원 수준은 자동 통합/수동 설정 중 어느 제품 약속인지 사용자 결정이 필요하다.
- 외부 표준 용어는 이번 감사에서 내부 명확성만 판정하고, 공식 출처가 없으면 미검증으로 남기는 것이 계획에 맞는다.
- hook의 warn/block 집행 강도와 문서상 완료 승인 의무는 별개의 축으로 기록해야 한다.

### 🔍 틀린 에이전트 가정

- “minor 완료 승인 확인은 자동 생략된다”는 가정은 거짓이다. 계획 승인만 자동이고 완료 승인 확인은 남는다.
- “guidebook의 직접 done 이동만 문제다”는 가정은 불충분하다. 동일한 실행 지시가 `layer1_discovery.md`에 있다.
- “OpenAgent 선택지는 자동 연결 완료를 뜻한다”는 가정은 검증되지 않았다. 현재는 수동 질의 기반 경로다.
- “release-audit 통과만으로 종단 간 완결성이 증명된다”는 가정은 불충분하다. 이번 release에는 관련 검증 근거가 존재하지만, report에는 그 위치와 재현 절차가 빠져 있다.

### 최종 판정

보고서의 핵심 발견(완료 승인 drift, OpenAgent 자동 wiring 미완결)은 실제 근거와 대체로 일치한다. 다만 완료 승인 drift의 수정 범위가 실행 inject까지 확장되어야 하며, `.mpa-workspace` 수정 경계는 즉시 명확히 해야 한다. 배포 결론은 evidence-free가 아니라 evidence-unlinked 상태이므로, 근거 파일·명령을 보고서에 보강한 뒤 테스트 진행이 가능하다.
