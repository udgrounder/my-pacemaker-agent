# 태스크 내역서: plan_approval_flow_clarification

**작업일:** 2026-08-26
**계획서:** `plan.md`

---

## 변경 파일 목록

| 파일 경로 | 변경 유형 | 설명 |
|---------|---------|------|
| `.mpa/runtime/inject/layer1_design.md` | 수정 | 의도 확인 중심의 조건부 질문, 결정 해소 후 즉시 계획서 작성, 의도 결함 고지·보완, 구현 승인 전 독립 비평, 최종 구현 승인 요청 절차 정비 |
| `.mpa/runtime/inject/plan_interview.md` | 수정 | 인터뷰에서 사용자 의도를 바꾸는 항목만 질문하고, 나머지 조용한 결정·반례는 Agent가 근거와 위험을 기록하도록 정비 |
| `.mpa/runtime/core/agent_rules.md` | 수정 | 설계 상태 재개, 사용자 의도와 Agent 판단의 경계, 구현 승인 및 질문 규칙 동기화 |
| `.mpa/runtime/core/agent_rules_detail.md`, `.mpa/runtime/core/glossary.md` | 수정 | 세부 규칙과 용어를 사용자 결정·구현 승인 절차에 맞게 동기화 |
| `.mpa/runtime/core/session_protocol.md` | 수정 | 설계 완료 작업의 재개 경로를 계획 검토·구현 승인 요청으로 정정 |
| `.mpa/runtime/hooks/code_gate.py`, `.mpa/runtime/hooks/plan_hash.py` | 수정 | 승인 안내 문구와 명세 변경 이력의 하위 섹션 경계를 보완 |
| `.mpa/runtime/inject/discussion_mode.md`, `.mpa/runtime/templates/plan_template.md` | 수정 | 대화·계획서 템플릿의 질문과 승인 표현을 절차에 맞게 동기화 |
| `tests/test_plan_hash.py` | 수정 | 명세 변경 이력이 뒤따르는 하위 섹션을 침범하지 않는 회귀 검증 추가 |
| `.mpa/runtime/.mpa-version`, `dist/.mpa/runtime/.mpa-version` | 수정 | 생성된 불변 릴리즈 ID `20260826114136-81246cfd` 기록 |
| `workspace/releases/20260826114136-81246cfd/` | 추가 | Runtime 패키지, manifest, receipt, release note를 포함한 불변 릴리즈 번들 |
| `guidebook/guidebook.md` | 수정 | 사용자용 의도 확인·즉시 계획서 작성·독립 비평·최종 구현 승인·재개 흐름 설명 동기화 |
| `dist/.mpa/runtime/` | 동기화 | source Runtime의 변경을 배포 Runtime에 반영 |

---

## 상세 변경 내역

### `.mpa/runtime/inject/layer1_design.md`

- **대상:** major 설계 절차
- **위치:** `작업`, `major 설계 절차`
- **변경 유형:** 수정
- **내역:** 사용자 의도를 명확히해야 하는 항목만 사전 질문하고, 질문은 원하는 결과·우선순위·범위·완료 기준·위험 제약을 확인한다. 의도의 공백·모순·실현 불가 제약은 영향·권장 보완안과 함께 고지·보완한다. 계획서 작성 중 의도를 바꾸는 새 사항만 `사용자 결정`과 해시 갱신 대상으로 승격하며, 그 밖의 실행·기술 판단은 Agent가 수행한다. 위험 기준 충족 시 독립 비평을 `설계 완료` 전에 수행·반영하고, 최종 구현 승인은 보완된 계획서 검토를 요청하는 문구로 통일했다.

### 상태 재개·사용자 가이드

- **대상:** `agent_rules.md`, `session_protocol.md`, `guidebook.md`
- **위치:** 상태 표, 세션 재개, 계획 수립 안내
- **변경 유형:** 수정
- **내역:** `설계 중`은 조건부 질문 뒤 즉시 계획서를 작성하는 과정으로, `설계 완료`은 계획 검토·구현 승인 요청으로 일치시켰다.

---

## 요구사항 명세 대비 변경 사항

| 변경 | 이유 | 명세 영향 | 보고 |
|---|---|---|---|
| 없음 | 승인된 요구사항 명세의 절차와 범위 안에서 구현 | 없음 | 구현 완료 시 누적 보고 |

---

## 검증 포인트

- [x] 정상 경로 확인: 사용자 결정이 없을 때 질문을 생략하고 즉시 계획서를 작성한다.
- [x] 실패 경로 확인: 작성 중 새 사용자 결정은 질문·`사용자 결정` 반영 전에는 구현 승인을 요청하지 않는다.
- [x] plan.md 완료 기준 충족 여부: source–dist 동기화와 전체 단위 테스트로 확인했다.

## 추가 보완

- 사용자 지시에 따라 계획서 작성 자체를 별도 승인 관문으로 두지 않도록 정정했다. 사용자 결정 질문을 해소했거나 질문이 없으면 즉시 계획서를 작성하고, 명시적 승인은 완성된 계획서의 구현 승인에만 요구한다.
- 독립 평가 권고에 따라 위험 기준 충족 시 독립 비평을 구현 승인 전에 수행·반영하도록 가이드 흐름을 맞추고, 작성 중 질문과 최종 검토 항목을 우선순위별로 구분했다.
- 요구사항 명세는 사용자 의도 계약으로, 실행 계획·기술 선택·테스트·조용한 결정은 명세를 바꾸지 않는 한 Agent 수행 영역으로 명확히 구분했다.
- 질문의 목적을 구현 방법 선택이 아닌 사용자 의도 확인으로 정하고, 의도 결함을 발견했을 때의 고지·보완 형식을 추가했다.
- 독립 결과 검증에서 확인된 인터뷰 질문 경계와 명세 변경 이력의 하위 섹션 침범 문제를 보완했다.

## 검증 실행 기록

| 명령 | 결과 |
|---|---|
| `python3 release_manager.py sync-runtime` | source Runtime과 `dist/.mpa/runtime/` 동기화 성공 |
| `python3 -m unittest discover -s tests -v` | 121개 테스트 통과 |
| `python3 .mpa/runtime/hooks/plan_hash.py check workspace/tasks/active/20260825_plan_approval_flow_clarification/plan.md` | `reqspec-v1:564913155c6ae1fb` 일치 |
| `git diff --check` | 공백·형식 오류 없음 |
| `python3 release_manager.py prepare-release …` | 릴리즈 `20260826114136-81246cfd` 생성, 전체 테스트 121개 통과 |
| `python3 release_manager.py release-audit` | 릴리즈 번들 12개 감사 통과 |

## 완료 처리

- 사용자 명시 승인에 따라 2026-08-26에 완료 처리하고 `tasks/done/`으로 보관한다.
