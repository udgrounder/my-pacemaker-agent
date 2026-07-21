## 일관성 점검 결과

### ✅ 확인됨 (문제 없음)

- **트리거 표 ↔ detail 섹션 이름 대조 (item 1)**: `agent_rules.md` "상세 파일 로드 트리거" 표에 나열된 13개 detail 섹션 이름을 `agent_rules_detail.md`의 실제 `## ` 헤딩과 하나씩 대조 — 전부 정확히 일치.
  - 프론트매터 누락 처리(8행) / 계획 승인 재확인(42행) / 태스크 재개(62행) / 코드 탐색(94행) / 기억 여부 판단(105행) / 기술·도메인 지식 기록 기준(137행) / 역할 메모리 업데이트(183행) / 다음 작업 예측(201행) / upgrade-candidates 형식(217행) / MPA 파일 수정 세부(266행) / minor 경량 처리 절차(286행) / 실패비용 추정 기준(318행) / 완료 인정 판별 기준(348행).
  - "Layer 2 현황 표시"는 트리거 표에 "detail 불필요 — agent_rules.md에 인라인"으로 명시돼 있고, 실제로 `agent_rules.md` "태스크 완료" 섹션 major 항목 5번(310~326행)에 해당 내용이 인라인으로 존재함을 확인.
  - `core/glossary.md` 행(27행)도 "disclosed reference — agent_rules_detail.md가 아니라 별도 파일"로 정확히 구분 표기됨.

- **code_gate.py/plan_hash.py 출력 메시지 ↔ 문서 인용 대조 (item 4)**: 실제 코드에서 `emit_block`/`emit_warn`으로 내보내는 문자열을 직접 확인.
  - `code_gate.py`의 `check_hash_integrity()`가 내보내는 `"⛔ 계획 승인 기록 복구 필요: ..."`, `"⛔ 계획 재승인 필요: ..."` 두 문자열이 `agent_rules.md:12`, `agent_rules_detail.md:13,44`가 인용하는 `"계획 승인 기록 복구 필요"` / `"계획 재승인 필요"`와 글자 단위로 정확히 일치(부분 문자열 포함 관계 확인).
  - 다른 emit 메시지(`⛔ 완료 처리 차단`, `⚠️ 완료 절차 확인`, `⛔ 구현 차단`)는 트리거 표에서 별도로 인용되지 않으며, 인용하지 않는 것이 맞음(해당 트리거가 없음).

- **`[작업명]` 잔존 플레이스홀더 (item 3)**: `.mpa-workspace/` 설치본 전체 `grep -rln '\[작업명\]'` 결과 0건. 전부 `[태스크명]`으로 교체 완료.

- **`core/glossary.md` 존재·참조 정확성 (item 6)**: 파일 존재 확인(`.mpa-workspace/core/glossary.md`, 73줄). `agent_rules.md:27`이 정확한 경로로 이 파일을 가리키며 disclosed reference로 구분. `workspace/memory/shared/architecture.md`의 "파일별 역할" 표(167행)에도 `core/glossary.md` 행이 추가돼 있고, 같은 파일에서 `grep -n "GATE"` 결과 0건 — GATE 문구가 "계획 승인"/"완료 승인 확인"으로 완전히 교체됨을 확인.

- **GATE 1/2 잔존 검사 — 훅 스크립트·session_start.py (item 2 일부)**: `code_gate.py`, `plan_hash.py` 내부에는 docstring·주석 형태로 "GATE 1"/"GATE 2"가 다수 남아있으나(예: `code_gate.py:7,11,140,178,226,258,311,316,321,347`), 이는 `glossary.md:51`이 명시한 예외("훅 스크립트 내부 주석·MPA_GATE 환경변수 이름")에 정확히 해당 — 문제 아님. `session_start.py`도 "코드 수정 게이트"(163행)라는 일반 명사만 사용하고 "GATE 1/2"라는 번호 지칭은 없음 — 알려진 예외와 일치.

- **옛 plan.md 구조 참조 검사 (item 5)**: `workflows/*.md`, `personas/*.md`(plan_critic.md 포함), `templates/*.md`(plan_template.md 제외) 전체에서 "## 에이전트 보고"/"## 요청 원문"/"## 목적"/"## 요구사항"/"## 구현 단계" 등이 plan.md의 최상위 구조로 언급되는 곳을 찾지 못함. `inject/layer1_design.md`는 `## PRD`/`## 구현 계획`/`## 완료 기준` 용어를 일관되게 사용하고, "PRD 확정 전 구현 단계 작성 금지" 규칙과 2단계 작성 절차(122행, 130~151행)가 실제로 반영돼 있음을 확인. `plan_critic.md`의 "구현 단계" 언급(26행)은 새 구조에서도 `## 구현 계획` 하위 `### 구현 단계`로 그대로 존재하는 용어라 불일치 아님.

### 🚨 불일치 발견

- **`inject/layer1_design.md:188`에 옛 "GATE1" 표현 잔존**: `- **명시적 승인 없이 구현을 시작하지 않는다** — "GATE1을 승인할까요" 같은 내부 용어를 사용자에게 그대로 노출하지 않는다.` 이 문구가 "GATE1"이라는 옛 절차 명칭을 그대로 담고 있음. `core/glossary.md:51`이 명시한 예외 목록은 "훅 스크립트(`code_gate.py`/`plan_hash.py`) 내부 주석·`MPA_GATE` 환경변수 이름·`session_start.py`의 일반 명사 사용"뿐이며, `layer1_design.md`는 이 셋 중 어디에도 해당하지 않는 실행 레이어 inject 파일(매 설계 세션 로드)이다. "절차 설명 레벨에서 GATE 1/2 잔존 여부"를 확인하는 이번 점검 기준상 이 자리가 걸린다.
  - 파일: `.mpa-workspace/inject/layer1_design.md:188`
  - 수정 제안: "GATE1을 승인할까요" → "계획 승인을 승인할까요" 또는 문맥에 맞는 평이한 예시로 교체(예: `"내부 게이트 이름을 그대로 노출하지 않는다"`처럼 특정 번호 없이 서술하거나, `"계획 승인"이라는 이름 자체도 그대로 노출은 괜찮으므로 예시 문구를 다른 내부 전용 표현으로 교체`). 핵심은 "GATE1"이라는 옛 번호 표기를 제거하는 것.

### 📋 동기화 대기 (문제 아님)

- `dist/.mpa-workspace/core/agent_rules_detail.md` — 설치본과 다름. dist 쪽이 구버전 상태(예: `## GATE 1 재진입 복구`, `[작업명]`, "작업 재개" 등 옛 표현 그대로, "실패비용 추정 기준"·"완료 인정 판별 기준" 섹션 자체가 없음). 이번 태스크(현재 상태: `구현 중`)가 아직 완료 처리되지 않아 `dist/` 동기화·`current_version` 갱신 단계 전이므로 예상된 상태.
- `dist/.mpa-workspace/upgrade-candidates/` — `.gitkeep`, `plan_checkbox_lag.md`, `reapply-dcAmountJson-dateRange.md`가 설치본에는 없고, 설치본의 `index_registration_omission.md`·`archive/discussion-mode-routing.md`·`archive/discussion_premature_dichotomy.md`는 dist에 없음. 이 태스크와 무관한 기존 드리프트로 보이나, dist 동기화 시 함께 반영 필요.
- 그 외 확인한 파일(`core/agent_rules.md`, `core/glossary.md`, `templates/plan_template.md`, `hooks/code_gate.py`, `hooks/plan_hash.py`, `.mpa-version`)은 이미 설치본과 dist가 동일함 — 별도 동기화 불필요.

### 참고 (불일치는 아니나 확인 시 발견한 경계 사례)

- `.mpa-workspace/templates/sub_template.md`가 "## 목적"·"## 구현 단계"를 최상위 헤딩으로 사용 중이나, 이는 `plan.md`가 아니라 서브태스크 전용 경량 포맷(`sub_[이름].md`)이며 이번 태스크 배경(item 6: plan_template.md만 재작성 대상)에 포함되지 않아 불일치로 분류하지 않았음. `templates/minor_plan_template.md`도 3영역(PRD/구현계획/완료기준) 구조를 따르지 않고 기존 플랫 구조를 유지 중이나, `agent_rules_detail.md` "minor 경량 처리 절차"(304행)가 동일하게 플랫 구조("핵심 기능"·"구현")를 서술하고 있어 서로 어긋나지 않음 — 다만 두 파일 모두 이번 재구조화의 의도적 제외 대상인지, 누락인지는 이번 태스크 설계자가 판단할 사안으로 남겨둠.
