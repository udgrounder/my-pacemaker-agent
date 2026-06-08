## 검토 결과

> 검토 기준일: 2026-06-08  
> 검토 대상: plan.md 3개 요구사항 구현 결과  
> 검토 파일: agent_rules.md, agent_rules_detail.md, layer1_design.md, architecture.md

---

### 🚨 즉시 수정 필요

- **항목 10 (트리거 표 중복 위험)**: agent_rules.md 트리거 표 14줄에 "작업 완료 처리 직후 (Layer 2 현황 표시 시점) → Layer 2 현황 표시 (단, agent_rules.md에 인라인으로 있음 — detail 불필요)"가 있고, 신규 추가된 22줄 "실패 비용 추정 결과 minor로 판단된 직후 → minor 경량 처리 절차"가 있다. 그런데 이 트리거 조건 "minor로 판단된 직후"는 실제로는 **layer1_design.md를 읽고 있는 설계 세션 내부**에서 발생한다. layer1_design.md 56-59줄에도 동일 분기 설명이 있어, 에이전트가 설계 세션 중 minor로 판단할 때 트리거를 두 번 보게 된다 (layer1_design.md에서 한 번, 트리거 표에서 한 번). 이 자체는 오류가 아니나 — 실제 문제는 **트리거 표의 "minor 경량 처리 절차" 항목이 layer1_design.md의 분기 설명(56-59줄)과 다른 경로를 안내한다**는 점이다. layer1_design.md는 "agent_rules.md 'minor 태스크 경량 처리' 절차에 따라"를 지시하고, 트리거 표는 "agent_rules_detail.md 'minor 경량 처리 절차'"를 지시한다. 에이전트가 layer1_design.md를 읽으면 → agent_rules.md로, 트리거 표를 보면 → detail.md로 이동하는 **이중 경로**가 존재한다. 어느 쪽이 진입점인지 불명확하므로 수정 필요. / 이유: 에이전트가 minor 판단 직후 어느 파일을 읽어야 하는지 모호함 발생.

- **항목 12 (라우팅 포인터 실질 불일치)**: agent_rules.md 라우팅 테이블 140줄 `→ "MPA 시스템 파일 수정 규칙" 섹션` 포인터는 섹션 헤더(190줄)가 유지되어 있어 이동 자체는 성공했다. 그러나 섹션 내용이 `"세부 절차: core/agent_rules_detail.md 'MPA 파일 수정 세부' 섹션 참조."` 한 줄로 축약되었는데, **이 참조 경로가 파일명만 있고 실제 Read 경로가 없다**. agent_rules.md의 다른 참조들은 "core/agent_rules_detail.md [섹션명] 섹션 참조" 형식인데, 이 섹션은 동일하게 작성되어 있어 일관성은 있다. 그러나 에이전트가 "규칙 바꿔줘" 발화 시 라우팅 테이블에서 "MPA 시스템 파일 수정 규칙" 섹션으로 이동하면, 그 섹션은 **트리거 표의 "MPA 파일 수정 세부" 항목을 먼저 보지 않은 상태에서** 도달할 수 있다. 트리거 표(23줄)와 라우팅 테이블(140줄)이 동일 상황에서 서로 다른 진입점을 제공하므로, 에이전트가 어떤 경로로 진입하든 결국 detail.md를 읽어야 한다. 중복 진입 경로는 제거하거나 명확히 통합해야 한다. / 이유: 두 경로(트리거 표 → detail / 라우팅 테이블 → agent_rules.md 섹션 → detail)가 중간 단계를 하나 더 추가하므로 비효율.

---

### ⚠️ 주의 필요

- **항목 3 (layer1_design.md 참조 문구 명확성)**: layer1_design.md 66-68줄 참조 문구는 "agent_rules.md 'minor 태스크 경량 처리' 섹션의 **실패 비용 추정 절차**를 적용한다"라고 명시한다. agent_rules.md에서 해당 섹션 제목은 "minor 태스크 경량 처리 (GATE 1 생략 / GATE 2 경량 확인):"(216줄)이다. 섹션 제목이 길고 괄호가 포함되어 있어, 에이전트가 참조 문구의 인용명으로 해당 섹션을 찾을 때 불일치가 발생할 수 있다. agent_rules.md는 항상 로드되므로 별도 Read는 불필요하지만, 섹션명 불일치로 인한 탐색 오류 위험 존재. / 권장: layer1_design.md 참조 문구의 섹션명을 실제 헤더 텍스트와 정확히 일치시키거나, agent_rules.md 섹션 헤더를 단순화한다.

- **항목 9 (minor 경량 처리 절차 내용 일부 차이)**: agent_rules_detail.md 266줄의 step 4 표현이 "보고 + 사용자 확인 대기 → 확인 후 done 처리 (agent_rules.md '작업 완료' 섹션 참조)"이다. 원본 agent_rules.md에 있던 동일 내용(원본에서 이동 전)과 비교 시, 원본에는 별도 done 처리 절차가 인라인으로 있었으나 현재는 "agent_rules.md 섹션 참조"로 대체되어 있다. 이 자체는 설계 의도(중복 제거)에 맞지만 — detail.md를 읽은 에이전트가 agent_rules.md까지 다시 참조해야 하므로, minor 태스크 완료 시 필요한 읽기 수가 늘어난다. / 권장: 완료 처리가 minor 흐름에서 빈번히 발생하는 경우 인라인으로 유지하는 것을 검토한다.

- **항목 13 (이동된 내용 완전성)**: plan.md Step 5에서 "upgrade-candidates 형식 섹션에 archive 처리 방법 병합"이 명시됐다. 현재 agent_rules.md 90줄에 archive 절차가 detail.md 참조로 대체되어 있고, detail.md 216-226줄에 "처리 후 archive 절차"가 있다. 원본과 비교 시 — 원본 agent_rules.md에는 "처리 완료 후 — 삭제 대신 archive로 이동:" 이후 3가지 처리 결과 코드 블록이 있었고, detail.md에도 동일 내용이 있다. 내용 자체는 일치하나, agent_rules_detail.md 226줄 "세션 시작 시 upgrade-candidates/(루트)에 있는 파일만 처리 대상으로 안내한다. archive/는 이력 참조용이므로 사용자에게 알리지 않는다." 문장이 원본 agent_rules.md에는 없던 신규 추가 내용이다. 이 추가가 의도된 것인지 확인이 필요하다. / 권장: plan.md에 "archive/ 디렉토리 운영 원칙 추가"가 명시적으로 언급되지 않았으므로, 이 추가가 범위 내인지 확인한다.

---

### ✅ 확인됨

- **항목 1**: agent_rules.md 218-240줄에 ①②③ 순서 판단 절차 + 등급 테이블이 통합됨.
- **항목 2**: layer1_design.md에서 ①②③ + 테이블이 제거되고 "agent_rules.md 실패 비용 추정 절차 적용" 참조로 대체됨.
- **항목 4**: minor/critical/major 판단 기준이 agent_rules.md 단일 위치에만 존재함. layer1_design.md에 독립 기준 없음.
- **항목 5**: architecture.md 47-50줄 — "즉시" 제거됨. "마커 이후 done 태스크 중 major가 1개 이상 포함된 완료 작업이 있을 때" 표현으로 명확화됨.
- **항목 6**: agent_rules.md 335줄 — 트리거 조건이 architecture.md 기준으로 업데이트됨.
- **항목 7**: 두 파일의 트리거 표현이 동기화됨. "minor만 5개 이상" 조건도 양쪽 모두에 존재함.
- **항목 8**: agent_rules_detail.md 230-243줄에 "MPA 파일 수정 세부" 섹션 추가됨. 트리거 조건 명시.
- **항목 11**: agent_rules.md "MPA 시스템 파일 수정 규칙" 섹션이 detail 참조 1줄로 대체됨.
- **항목 14**: agent_rules.md 전체 흐름이 섹션 축약 후에도 자연스럽게 이어짐. 헤더 구조 유지됨.
- **항목 15**: plan.md 3개 요구사항(실패 비용 단일 소스화, Layer 2 트리거 명확화, detail 이동) 모두 구현됨.
