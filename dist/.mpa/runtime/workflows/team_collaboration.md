# 워크플로우: 팀 협업

> 여러 사람이 같은 프로젝트에서 AI agent와 함께 작업할 때의 흐름  
> 핵심 문제: 각자 다른 스레드에서 작업하면 memory가 diverge된다

---

## 혼자 작업 vs 팀 작업의 차이

| 구분 | 혼자 | 팀 |
|------|------|----|
| memory 관리 | 한 사람이 관리 | 공유 저장소(Git)에서 관리 |
| 태스크 배분 | 순서대로 | 의존성 기준으로 병렬 배분 |
| Layer 2 체크포인트 | 혼자 실행 | 팀 전체 동기화 포인트 |

---

## 사용 자원

| 구분 | 파일 |
|------|------|
| 세션 패키지 | `inject/layer0_init.md` (팀 공동) |
| 세션 패키지 | `inject/layer2_checkpoint.md` (팀 공동) |
| 개인 워크플로우 | `workflows/new_feature.md` 또는 `workflows/bug_fix.md` |
| 페르소나 | `personas/architect.md` (팀 레이어 0) |
| 페르소나 | `personas/integration_auditor.md` (팀 체크포인트) |
| 분석 스킬 | `skills/analysis/dependency_mapping.md` (태스크 배분) |

---

## 전체 흐름

```
[팀 Layer 0 — 함께]
스레드: 🆕 새 스레드 (팀 대표 1명)
inject:  inject/layer0_init.md
         └─ 페르소나: architect
         └─ 스킬: dependency_mapping

공동 작업:
1. memory/ 초안 작성 (특히 shared/architecture.md)
2. 팀 전원 검토 및 합의
3. 공유 저장소(Git)에 저장
4. dependency_mapping으로 전체 태스크 목록 + 의존성 도출 → 태스크 배분
        ↓
[개인 Layer 1 — 각자]
각자 담당 워크플로우 실행:
→ workflows/new_feature.md 또는 workflows/bug_fix.md

⚠️ 각 세션 시작 전 반드시:
- 최신 memory/ pull 확인 (다른 사람이 업데이트했을 수 있음)
        ↓
[팀 Layer 2 — 함께]
N개 태스크마다 팀 전체 체크포인트
스레드: 🆕 새 스레드
inject:  inject/layer2_checkpoint.md
         └─ 페르소나: integration_auditor
→ 개인 작업들이 전체 아키텍처와 정합한지 확인
```

---

## memory 공유 관리 규칙

```
1. memory/는 공유 저장소(Git)에서 관리
2. 변경 시 PR/MR로 팀 리뷰
3. 개인 작업 중 규칙 추가가 필요하면:
   a. 팀에 먼저 공유/합의
   b. 합의 후 공유 파일 업데이트
   c. 이후 작업에 반영
4. 규칙 변경이 기존 태스크에 영향을 주면 → Layer 2 체크포인트 즉시 실행
```

---

## 태스크 배분 원칙

```
병렬 가능:
- 의존성 맵에서 같은 레벨에 있는 태스크들
- 서로 다른 도메인을 담당하는 태스크들
- shared/contracts.md가 확정된 후의 각 구현 태스크들

순서대로 진행:
- contracts.md 정의 → 각 도메인 구현
- 데이터 모델 확정 → 데이터 의존 모듈 구현
```

---

## 핵심 체크포인트

- [ ] 팀 Layer 0에서 memory를 공동으로 합의했는가
- [ ] 태스크 배분이 의존성 맵 기준으로 이루어졌는가
- [ ] 각자 태스크 전에 최신 memory를 확인하는가
- [ ] 규칙 변경은 팀 합의를 거치는가
- [ ] Layer 2 체크포인트를 주기적으로 실행하는가
