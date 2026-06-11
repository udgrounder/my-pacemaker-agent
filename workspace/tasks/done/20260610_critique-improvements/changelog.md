# 작업 내역서: critique-improvements

**작업일:** 2026-06-10
**계획서:** `plan.md`

---

## 변경 파일 목록

| 파일 경로 | 변경 유형 | 설명 |
|---------|---------|------|
| .mpa-workspace/core/session_protocol.md | 수정 | 실패비용 참조를 중간파일(layer1_design)→정본(agent_rules) 직접 참조로 |
| .mpa-workspace/workflows/new_feature.md | 수정 | 동일 — 정본 직접 참조 |
| .mpa-workspace/workflows/bug_fix.md | 수정 | 인라인 3축 표현 제거, new_feature와 동일한 정본 참조 패턴으로 통일 |
| README.md | 수정 | hooks 설명 "강제 메커니즘"→"가드레일(하드 차단은 게이트뿐)" |
| .mpa-workspace/hooks/README.md | 수정 | "강제하는 메커니즘"→"가드레일", 하드 차단은 code_gate뿐임 명시 |
| guidebook/guidebook.md | 수정 | 14.2 삭제역설 완화책 보강 + 첫머리 "실행 경로 미로드" 한 줄 |
| dist/.mpa-workspace/** | 동기화 | PostToolUse hook 자동 복사 (4개 파일 확인) |

---

## 상세 변경 내역

### SSOT (Step 1·2)
- session_protocol.md:83, new_feature.md:34 — 실패비용 추정 참조를 `core/agent_rules.md` "minor 태스크 경량 처리" 절차(①②③)로 통일. 기존엔 중간파일 layer1_design.md를 가리켜 깨지기 쉬웠음.
- bug_fix.md:37-39 — "심각도/발견가능성/가역성" 인라인 표현 제거. 폐기 표현이라서가 아니라 new_feature와 참조 방식이 불일치했기 때문. 같은 정본 참조 패턴으로 통일. "수정 전 커밋" 줄은 bug_fix 고유라 유지.

### 톤 (Step 3) — 결정 A: 차단은 강제 유지
- README:178, hooks/README.md:3 — 세션시작 주입·종료 리마인드까지 "강제"로 묶던 표현을 "가드레일"로 정밀화. code_gate의 하드 차단은 "강제"로 명시 유지.

### 삭제역설 (Step 4) — 메커니즘 미도입, 설명 보강
- guidebook 14.2 — 기존 "빈도 신호"를 (1)위반 탐지 우선(특히 금지 규칙) (2)기원 추적 (3)빈도 신호는 주의(자동 계측 불가)로 재구성 + 비대화 시 리팩토링 + 조용한 위반 한계. 사용자 통찰 반영.

### guidebook 보완 (Step 5)
- 첫머리 — "이 문서는 매 세션 자동 로드되지 않으며, 실행 규칙은 .mpa-workspace/가 담당" 한 줄 추가.

---

## 계획서 대비 변경 사항

- 항목 3(효용 미검증 명시): 사용자 결정으로 철회 — 구현 안 함.
- 항목 4: "layer2_checkpoint 메커니즘 추가"에서 "guidebook 14.2 설명 보강"으로 전환(사용자 통찰 반영).
- Step 2 처리 근거 수정: "구버전이라 틀림"이 아니라 "워크플로우 간 참조 방식 불일치"로 재해석(mpa_system_designer 경고 반영).

---

## 검증 포인트

- [x] 정상 경로 확인: grep — 실패비용 참조가 중간파일을 더 이상 가리키지 않음
- [x] 실패 경로 확인: grep — 워크플로우에 인라인 3축 표현 잔존 없음
- [x] plan.md 완료 기준 충족: dist 4개 파일 동기화 일치 확인
