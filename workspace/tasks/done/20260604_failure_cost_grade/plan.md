---
태스크: failure_cost_grade
생성일: 2026-06-04
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: ""
---
# 태스크: 실패 비용 등급 (major/normal/minor) 도입
**상태:** 구현 완료  
**목적:** 실패 비용 레벨(1/2/3)을 major/normal/minor로 명명하고, plan.md에 저장 필드 추가, 구현 세션에서 등급별 행동 차별화

---

## 에이전트 보고

**사용자 결정 필요:** 없음

**에이전트 가정:**
| 가정 | 근거 | 틀렸을 때 영향 |
|------|------|--------------|
| 기존 Level 1=major, Level 2=normal, Level 3=minor 매핑 | 위험도 순서 동일 | 영향 없음 |

---

## 수정 대상 파일

| 파일 | 변경 내용 |
|------|---------|
| `layer1_design.md` | 자율성 레벨 테이블 명칭 변경 + plan.md 템플릿에 `실패 비용 등급:` 필드 추가 |
| `layer1_implement.md` | 구현 전 체크에 등급 확인 + 등급별 행동 명시 |
| `agent_rules.md` | "작업 진행" 섹션 Level 1/2/3 → major/normal/minor |
| `dist/` 3개 | 동기화 |

---

## 구현 단계

- [ ] 1. `layer1_design.md` — 자율성 레벨 테이블 + plan.md 템플릿 수정
- [ ] 2. `layer1_implement.md` — 등급 확인 + 등급별 행동 추가
- [ ] 3. `agent_rules.md` — Level 1/2/3 참조 전부 교체
- [ ] 4. `dist/` 동기화
