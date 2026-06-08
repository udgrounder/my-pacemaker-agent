---
태스크: agent-rules-refinement
생성일: 2026-06-08
타입: major
실패비용: major
상태: 완료 승인
승인해시: 018b5473f1d23d9d
---

# 작업 계획서: agent-rules-refinement

**파생 출처:** 없음 — 시스템 전체 비평 분석에서 발견된 3개 개선 항목

---

## 에이전트 보고

### 사용자 결정 필요

- 없음

### 암묵적 결정

- agent_rules.md를 실패 비용 추정의 단일 소스로 결정 — layer1_design.md의 ①②③이 더 상세하므로 agent_rules.md를 layer1_design.md 기준으로 보완 후 통합 / 반대 방향(agent_rules.md 기준 유지)도 가능했으나 더 상세한 쪽이 단일 소스가 돼야 함
- detail 이동 3개 후보 모두 이동 결정 — 트리거 조건이 명확하고 agent_rules_detail.md 기존 패턴과 일관성이 있음

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|-----|------|---------|
| agent_rules.md는 CLAUDE.md @inject로 항상 로드됨 | CLAUDE.md 파일 확인 | layer1_design.md에서 "agent_rules.md 참조"가 추가 I/O를 유발할 수 있음 |
| dist/ 동기화는 .mpa-workspace/ 파일을 dist/.mpa-workspace/로 복사 | architecture.md "dist/가 단일 배포 소스" 원칙 | 동기화 방향이 반대라면 dist/ 내용을 먼저 수정해야 함 |

---

## 요청 원문

시스템 전체 비평 분석에서 도출된 3개 항목 개선:
- 3번: 단일 소스 원칙 위반 (minor 판단 기준 중복)
- 4번: Layer 2 트리거 조건 명확화
- 7번: agent_rules.md → detail 이동으로 경량화

---

## 목적

agent_rules.md의 규칙 밀도를 낮추고, 중복 정의를 단일 소스로 통합하며, Layer 2 트리거 기준을 명확히 한다.

---

## 요구사항

1. **실패 비용 추정 단일 소스화**: layer1_design.md의 ①②③ + 등급 테이블을 agent_rules.md에 통합 → layer1_design.md는 참조로 대체
2. **Layer 2 트리거 명확화**: "major 1개 이상 → 즉시" → "마커 이후 done 중 major 포함 시"로 변경 (architecture.md + agent_rules.md 동기화)
3. **agent_rules.md 경량화**: 세부 절차 3개를 agent_rules_detail.md로 이동 + 트리거 표에 항목 추가

---

## 구현 단계

- [x] Step 1 — agent_rules.md 실패 비용 추정 섹션 보완 / 이유: layer1_design.md의 ①②③ + 등급 테이블을 minor 판단 기준 앞에 통합 (single source)
- [x] Step 2 — layer1_design.md 실패 비용 추정 섹션 대체 / 이유: ①②③ + 테이블 제거 → "agent_rules.md 실패 비용 추정 절차 적용" 한 줄로 대체
- [x] Step 3 — architecture.md Layer 2 트리거 변경 / 이유: "즉시" 제거, "마커 이후 done 중 major 포함 시" 로 명확화
- [x] Step 4 — agent_rules.md 작업 완료 섹션 Layer 2 트리거 동기화 / 이유: architecture.md 변경 내용 반영
- [x] Step 5 — agent_rules_detail.md에 3개 섹션 추가 / 이유: 트리거 조건이 명확하고 이동 시 에이전트 행동에 영향 없는 것만 선별 이동
  - `MPA 파일 수정 세부` 섹션: 수정 규칙 전체 (195-206줄, ~12줄) — 라우팅 테이블에 이미 포인터 있음
  - `minor 경량 처리 절차` 섹션: 5단계 세부 (240-258줄, ~19줄) — minor 판단 후에만 진입
  - `upgrade-candidates 형식` 섹션에 archive 처리 방법 병합: (88-95줄, ~8줄) — 이미 동일 트리거 항목 존재
- [x] Step 6 — agent_rules.md에서 이동된 내용 제거 + 트리거 표 업데이트 / 이유: 제거 위치에 "agent_rules_detail.md [섹션명] 참조" 1줄로 대체, 트리거 표에 2개 항목 추가
  - 미이동 항목: 정정 회고(세션 종료 트리거 모호 + 강제 실행 요구), 작업 완료 절차(빈도 높아 매 Read 오버헤드)
- [x] Step 7 — dist/ 동기화 / 이유: 수정된 파일 4개를 dist/.mpa-workspace/에 반영

---

## 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---------|---------|
| `.mpa-workspace/core/agent_rules.md` | 실패 비용 추정 통합, Layer 2 트리거, 3개 섹션 이동(경량화), 트리거 표 2개 항목 추가 |
| `.mpa-workspace/core/agent_rules_detail.md` | 2개 섹션 신규 추가(MPA 파일 수정 세부, minor 경량 처리 절차) + upgrade-candidates 형식 섹션에 archive 처리 병합 |
| `.mpa-workspace/inject/layer1_design.md` | 실패 비용 추정 ①②③ → agent_rules.md 참조로 대체 |
| `workspace/memory/shared/architecture.md` | Layer 2 트리거 기준 변경 |
| `dist/.mpa-workspace/core/agent_rules.md` | 동기화 |
| `dist/.mpa-workspace/core/agent_rules_detail.md` | 동기화 |
| `dist/.mpa-workspace/inject/layer1_design.md` | 동기화 |

## 참고 파일 (수정 없음)

- `workspace/memory/shared/architecture.md` — Layer 2 트리거 현재 정의 참조

---

## 반례

- 시나리오 1: agent_rules.md에 실패 비용 추정이 통합된 후 길이가 더 늘어나 당초 목표(경량화)와 상충 → Step 6 경량화로 순증가 없도록 통합 분량 ≤ 이동 절감 분량 확인. 해결책: Step 5/6 순서로 이동 후 통합하여 순증가 최소화
- 시나리오 2: detail로 이동된 섹션의 트리거 조건이 불명확해 에이전트가 로드 시점을 놓침 → 트리거 표의 조건 문구를 기존 패턴(동사·명사 일치)에 맞춰 명확히 작성

---

## 검증 체크리스트

- [ ] 정상 경로: agent_rules.md의 실패 비용 추정 섹션을 읽고 minor/major/critical 판단이 가능한가
- [ ] 정상 경로: layer1_design.md의 참조 문구를 읽고 에이전트가 agent_rules.md를 찾아 적용할 수 있는가
- [ ] 실패 경로: minor 판단 기준이 agent_rules.md와 layer1_design.md 중 어느 한쪽에만 있는 상태가 없는가
- [ ] 엣지 케이스: 이동된 섹션의 트리거 표 항목이 기존 항목과 중복되지 않는가

---

## 완료 시 문서 업데이트 대상

- [ ] `workspace/memory/shared/architecture.md` — Layer 2 트리거 변경 반영 (Step 3에서 직접 수정)
