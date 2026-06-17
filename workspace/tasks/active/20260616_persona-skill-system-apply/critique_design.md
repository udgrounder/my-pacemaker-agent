# 독립 비평 — persona-skill-system-apply plan (설계 완료 단계)

> 실행: 서브에이전트(plan_critic 역할), 설계 맥락 격리, 실제 파일 검증 포함. 2026-06-16.
> 메인 에이전트 검증: F1·F2 grep으로 확인 — 둘 다 사실. F2는 비평보다 참조처가 더 많음(layer1_implement·layer0_init·layer2_checkpoint).

## 사실 오류 (검증됨)

- **[high] F1 — M7 "tech 구현 전용 묶임"은 사실 오류.** `inject/layer1_review.md:159`가 이미 `skills/tech/`를 참조. tech는 구현+검토 양쪽에 바인딩돼 있음. 진짜 갭은 *설계 단계 미바인딩*뿐. → M7·Step 11 정정 필요.
- **[high] F2 — D1=B "memory/domains 흡수"의 대상이 빈 폴더 + 참조 고아화.** `workspace/memory/domains/`는 비어 있고, 이를 읽는 inject가 다수: `layer1_implement.md:24,25,157`, `layer0_init.md:60,120,167`, `layer2_checkpoint.md:22,124,145,166`. D1=B로 `workspace/skills/` 신설 시 이 참조들이 옛 빈 폴더를 계속 읽음 → 도메인 로드 침묵 실패. 수정 대상 표에 layer0_init·layer2_checkpoint 누락.
- **[med] F3 — M8 "삼중 흩어짐" 과장.** 라우팅 표(`agent_rules.md`)는 페르소나만 선언, 스킬 미선언. 스킬은 workflows+inject 이중. → "페르소나=삼중, 스킬=이중"으로 정밀화.

## 숨은 가정

- **[high] A1 — plan_interview 참조 3곳(layer1_design:36/59/171).** Step 3이 단수("참조처 갱신")라 누락 위험(특히 minor 분기 line 59).
- **[med] A2 — 분석 스킬을 inject가 직접 참조(layer2_checkpoint:31-34).** Phase 4 "페르소나 요구 도메인 선언"이 가산인지 이관인지 미정 → 이중화 위험.
- **[med] A3 — programming 도메인이 두 폴더로 분할(템플릿=MPA / 값=프로젝트).** 같은 도메인 두 파일의 로드 우선순위·머지 규칙 없음.

## 비가시적 위임

- **[high] V1 — tech→programming 개명의 dist 처리 미정.** 설치본+dist 양쪽 mv + 참조 갱신, dist 직접편집 금지와 얽힘. 동기화가 폴더 rename 처리하는지 불명.
- **[med] V2 — architecture.md 5층을 "추가"하나 기존 평면 표와 공존 시 모순.** 대체/병기 미정.
- **[low] V3 — Step 7 "면 1개면 태그 생략"의 판정 기준·주체 없음.**

## 내부 비일관

- **[high] S1 — D2=B 확정인데 Phase 5(Step 10·11)가 본문에 죽은 단계로 잔존.** 구현자가 Step 11(설계 단계 도메인 합성)을 건너뛰면 F1의 진짜 갭이 영영 미수정.
- **[med] S2 — 목적·요구사항·자기점검이 "M1~M7" 토대로 명시하나 실제 모델은 M11까지.** → "M1~M11"로 통일.
- **[low] S3 — Step 13 grep 검증의 패턴 목록 없음.** 최소 skills/tech·memory/domains·plan_interview·discovery_classification 4패턴.

## 가장 치명적 3가지
1. F1 — tech 구현 전용 묶임 사실 오류 (변경 근거가 틀림).
2. F2+S1 — D1=B 흡수 대상 빈 폴더 + 참조 고아화, layer2_checkpoint 수정 누락.
3. V1 — tech→programming 개명의 dist 처리 미정.

## 메인 에이전트 판단
- F1·F2 검증 완료(사실). F2는 비평보다 광범위.
- **D1 재고 권고:** 시스템이 이미 `memory/domains/`를 다수 참조 → D1=B(신설)는 광범위 재배선 비용. D1=A(기존 memory/domains 사용)가 저위험이고 "저장≠소유" 원칙과도 합치(어휘 비대칭은 감수). → D1=B→A 역전 검토.
