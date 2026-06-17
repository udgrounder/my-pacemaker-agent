---
태스크: persona-skill-guidebook
생성일: 2026-06-16
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: e506acd89ddc3766
---
**목적:** 페르소나·스킬 관계/주입/관리 토론(R1~14) 결론을 guidebook 폴더에 새 원칙 문서로 정리

**요청:** "이 내용을 정리해서 우선 가이드북 폴더에 새로운 문서로 정리해서 작성하자"

**출처:** `workspace/exploration/discussion/persona_skill_relationship.md` (R1~14)
**스타일 참조:** `guidebook/multi_agent_principles.md` (한 문장 → 원칙 + 근거 라운드 추적 → 부록)

### 핵심 기능
- `guidebook/persona_skill_principles.md` 신규 작성
- 결론 문서 성격 — 라운드 기록은 과정, 이 문서는 "쓸 수 있는 결론". 각 원칙에 근거 라운드(R##) 추적
- 담을 결론:
  1. 경계 기준 = **역할 종속성** (사실/스타일 아님, 역할 범위)
  2. 관계 모델 = **합성** (페르소나 적용 ⊗ 스킬 도메인사실, R+D not R×D), 사람 프레임 vs 에이전트 프레임
  3. 스킬 내부 = 도메인 + **역할-면(面)** 구조, 가용집합/활성부분집합
  4. **개념적 소유 ≠ 물리적 저장** (소유=활성시점 기준, 저장=응집/DRY)
  5. 주입 타이밍 = 단계 진입 시 선언된 것 (PM/서브스레드는 multi_agent_principles 교차참조)
  6. 관리 함의 = analysis→페르소나 소유, skills→도메인·역할면, 저장/소유 분리

### 구현
1. `guidebook/persona_skill_principles.md` 작성 (multi_agent_principles.md 형식 차용)
2. multi_agent_principles.md와 교차참조 명시 (중복 영역: PM/서브스레드·입도)

### 완료 시 문서 업데이트 대상
- 없음 (가이드북 문서 자체가 산출물). 토론 문서는 별도 마커 정리.
