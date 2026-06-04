# 워크플로우: 새 기능 개발

> 새로운 기능을 처음부터 구현할 때의 전체 세션 시퀀스  
> Layer 0(프로젝트 초기화)이 완료된 상태에서 시작

---

## 사용 자원

| 구분 | 파일 |
|------|------|
| 세션 패키지 | `inject/layer1_design.md` |
| 세션 패키지 | `inject/layer1_critique.md` |
| 세션 패키지 | `inject/layer1_implement.md` |
| 세션 패키지 | `inject/layer1_review.md` |
| 페르소나 | `personas/task_designer.md` |
| 페르소나 | `personas/plan_critic.md` |
| 페르소나 | `personas/implementer.md` |
| 페르소나 | `personas/code_reviewer.md` |
| 분석 스킬 | `skills/analysis/silent_decision_extraction.md` |
| 분석 스킬 | `skills/analysis/counterexample_finding.md` |
| 분석 스킬 | `skills/analysis/path_tracing.md` |
| 기술 스킬 | `skills/tech/[사용 기술].md` |

---

## 전체 흐름

```
[0단계] 실패 비용 추정 (세션 시작 전, 인간이 직접)
심각도 / 발견 가능성 / 가역성을 추정하여 자율성 레벨 결정
→ session_protocol.md 자율성 레벨 표 참조
        ↓
[1단계] 설계 세션
스레드: 🆕 새 스레드
inject:  inject/layer1_design.md
         └─ 페르소나: task_designer
         └─ 스킬: silent_decision_extraction + counterexample_finding
         └─ 컨텍스트: shared/ 전체
결과물: 태스크 계획 (사전 결정 사항 + 단계 + 조용한 결정 목록 + 반례)
        ↓
[1.5단계] 계획 독립 비평 (복잡도 높을 때 권장)
스레드: 🆕 새 스레드 (설계 세션 컨텍스트 이어받지 않음 — 컨텍스트 오염 방지)
inject:  inject/layer1_critique.md
         └─ 페르소나: plan_critic
         └─ 읽는 것: plan.md만 (설계 과정 컨텍스트 없음)
결과물: 실패 시나리오·숨은 가정·비가시적 위임 목록
        ↓
[2단계] 사전 결정 사항 해소 (인간이 직접)
설계 세션에서 나온 "사전 결정 필요 사항"과 비평 결과를 인간이 직접 결정
⚠️ 가치 결정이 포함된 경우 반드시 이 단계에서 해소 (AI에게 위임 불가)
결정 내용을 태스크 계획에 보완
        ↓
[2.5단계] 가역성 확보 (구현 전)
현재 작업 상태를 커밋하여 롤백 지점 확보
인터페이스 변경이 있다면 contracts.md 먼저 업데이트
        ↓
[3단계] 구현 세션
스레드: 🆕 새 스레드
inject:  inject/layer1_implement.md
         └─ 페르소나: implementer
         └─ 스킬: [사용 기술].md + silent_decision_extraction
         └─ 컨텍스트: shared/ + domains/ + [1단계 태스크 계획]
        ↓
[4단계] 검토 세션
스레드: 🆕 새 스레드
inject:  inject/layer1_review.md
         └─ 페르소나: code_reviewer
         └─ 스킬: path_tracing + counterexample_finding
         └─ 컨텍스트: shared/ + [1단계 태스크 계획]
        ↓
[5단계] memory 업데이트
검토 세션 보고에서 나온 결정/안티패턴을 memory에 반영
```

---

## 핵심 체크포인트

- [ ] 실패 비용을 추정하고 자율성 레벨을 결정했는가 (0단계)
- [ ] 설계 세션에서 조용한 결정 목록이 추출됐는가 (1단계)
- [ ] 계획 복잡도가 높다면 독립 비평을 **새 스레드**에서 진행했는가 (1.5단계)
- [ ] 가치 결정이 있었다면 인간이 직접 해소했는가 (AI 위임 아님)
- [ ] 구현 전 커밋으로 롤백 지점을 확보했는가 (2.5단계)
- [ ] 사전 결정 사항이 모두 해소된 후 구현 세션을 열었는가
- [ ] 구현 세션에 태스크 계획이 주입됐는가
- [ ] 검토 세션은 반드시 새 스레드에서 했는가 (컨텍스트 오염 방지)
- [ ] 정상 + 실패 경로를 모두 추적했는가
- [ ] memory 업데이트 완료했는가
