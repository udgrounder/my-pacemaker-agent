---
태스크: classification-bias-warning
생성일: 2026-06-11
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: cd845f1e8c3ff058
---

# 작업 계획서: classification-bias-warning

**파생 출처:** upgrade-candidates 처리 — `critique-target-layer-classification`(실행 vs 설명 층위 분류)과 `consistent-classification-no-label-shortcut`(분류 기준 일관 적용·라벨 금지) 두 후보가 같은 뿌리("대상을 라벨로 단정 말고 분류 기준을 실제 적용")여서 통합 채택.

---

## 에이전트 보고

### 사용자 결정 필요
- 없음 (통합 채택 방향 사용자 승인, 2026-06-11)

### 암묵적 결정
- 두 후보를 `mpa_system_designer.md`의 단일 항목으로 통합 — 별개 항목 2개보다 응집적.

### 에이전트 가정
| 가정 | 근거 | 틀렸다면 |
|-----|------|---------|
| 두 후보가 동일 패턴의 두 측면 | 둘 다 mpa_system_designer "편향 경고" 타겟 + "분류를 표면으로 건너뜀" 공통 | 별개면 항목 분리 |

### minor 판단 근거
- 단일 관심사: "분류 편향 경고" 추가
- 방법 자명: 기존 경고 목록에 항목 추가 + layer2 착수 노트
- git 가역 / 외부연동·취향 결정 없음

---

## 요청 원문
"제안한 방향으로 진행 — 두 후보 통합 채택 후 업그레이드."

---

## 목적
두 upgrade-candidate를 통합해 "비평·감사·수정 착수 전 대상을 분류 기준으로 먼저 분류하고, 라벨로 단정하지 말 것" 경고를 방법론에 반영한다.

---

## 구현 단계
- [ ] Step 1 — `mpa_system_designer.md` "LLM 행동 편향 경고"에 통합 항목 추가: ① 대상을 실행 레이어(core/inject/hooks — 매 세션 로드) vs 설명 레이어(guidebook 등 — 미로드)로 진입점 grep으로 먼저 분류, "실행 비용·준수 지속가능성" 비판은 실행 레이어에만 유효 ② 예외·행선지를 라벨로 단정 말고 세운 분류 기준을 모든 항목에 동일 적용
- [ ] Step 2 — `layer2_checkpoint.md` 점검 착수 전 "대상 층위 분류" 노트 추가
- [ ] Step 3 — dist ↔ 이 레포 설치본 동기화 (2파일 양쪽)
- [ ] Step 4 — 두 후보 파일에 처리 결과 한 줄 기록 후 `upgrade-candidates/archive/`로 이동

---

## 수정 대상 파일
| 파일 경로 | 변경 |
|---------|------|
| `dist/.mpa-workspace/personas/mpa_system_designer.md` | 편향 경고에 통합 항목 |
| `dist/.mpa-workspace/inject/layer2_checkpoint.md` | 착수 전 분류 노트 |
| 이 레포 설치본 사본 2개 | 동기화 |
| `.mpa-workspace/upgrade-candidates/{critique-target-layer,consistent-classification}.md` | archive 이동 |
