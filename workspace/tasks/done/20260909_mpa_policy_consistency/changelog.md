# 태스크 내역서: mpa_policy_consistency

**작업일:** 2026-09-09
**계획서:** [plan.md](plan.md)

## 변경 파일 목록

| 파일 경로 | 변경 유형 | 설명 |
|---|---|---|
| `.mpa/runtime/core/agent_rules.md`, `agent_rules_detail.md`, `session_protocol.md` | 수정 | 사용자 부담 원칙·minor 정본·실제 단계 진입 |
| `.mpa/runtime/inject/_agent_execution_priority.md`, `layer1_critique.md`, `layer1_design.md`, `layer1_implement.md`, `layer1_review.md`, `layer1_discovery.md` | 수정 | 독립 실행/폴백·최소 확인·검증 지적 자동 처리·발견 후 완료 승인 보존 |
| `.mpa/runtime/personas/implementer.md`, `mpa_system_designer.md`, `templates/plan_template.md` | 수정 | 실행 판단 위임·정본 참조·minor 확인 기록 |
| `.mpa/runtime/workflows/*.md` | 수정 | 실제 작업 진입점에서 원본 도달, 불필요한 새 작업·인간 추정 제거 |
| `guidebook/guidebook.md`, `agent-specs/*/spec.md` | 수정 | 사용자 흐름·승인/hook 보장 범위·호스트 미확인 |
| `workspace/memory/shared/architecture.md`, `direction.md` | 수정 | 현재 정책 원본 연결·오래된 폴백 제거 |
| `tests/test_policy_consistency.py` | 추가 | 정본 참조·알려진 충돌·gate 경계·배포/minor 직접 진입 회귀 11개 |
| `.mpa/runtime/skills/analysis/discovery_classification.md` | 수정 | 분류 판단을 에이전트가 수행하며 실제 의도 공백만 질문 |
| `dist/.mpa/runtime/` | 동기화 | source Runtime의 배포 후보 mirror |
| 작업 폴더 `policy-audit.md`, `verification.md`, review 파일 | 추가 | 정책 지도·사례·검증 근거 |

## 상세 변경 내역

### 사용자 개입

core의 "사용자 부담 최소화"를 정본으로 정의했다. 유효한 의도·승인 재사용, 기술 판단·내부 기록은 에이전트가 수행, 실제 명세·권한·중요 위험 변화만 질문한다. 기존 major 구현·완료 승인과 selected critical gate 코드는 유지한다.

### minor

detail의 경량 절차가 실행 요청/계획만 요청을 구분한다. 최소 확인은 내용·설정·동작에 맞추고 미확인은 명시한다. implement fast-path에서 이 정본을 직접 읽도록 연결했다. 외부 동작 변경은 위험을 재판정하고 범위가 유지되면 응답 대기 없이 계속한다.

### 독립 비평·구현 검증

priority 파일이 입력 격리·유효 결과·1회 재시도·미완료 처리 정본이다. 비평은 생략 여부 확인, 검증은 한계 고지와 자가 검증으로 구분한다. 검증자가 판단한 뒤에는 메인 에이전트가 상세 결과를 읽고 승인 범위의 수정·재검증을 수행할 수 있다. 검토 전용 요청을 수정 승인으로 취급하지 않는다.

### 보장 범위

설정 생성·스크립트 실행과 실제 호스트 동작을 분리했다. gate는 알려진 도구/입력/경로에 의존하며 범용 접근 통제가 아니다. 승인해시는 명세 일치만 확인한다. 실제 호스트 통합·모델 준수율은 미확인이다. hook·plan_hash·install·release_manager 구현은 수정하지 않았다.

### 1차 독립 검토 후 보완

검토자가 발견한 discovery의 `검토 완료`→done 직접 이동을 제거했다. 신규 작업 등록만으로 완료하지 않고 실제 결과 확인·완료 승인을 거친다. 분류·방향 기록을 위한 중복 질문도 정리했다. 승인 기록 누락은 당시 명시적 승인과 명세·위험의 동일성이 입증될 때만 근거를 남겨 정상 approve로 복구하며, 근거 부족·명세 변경은 기존 재승인 경로를 유지한다. 실제 기존 plan의 마이그레이션은 하지 않았다. core의 완료 승인 뒤 추가 이동 확인 예시도 제거했다.

### 최종 독립 검토 후 보완

MPA 수정 뒤 자동 동기화는 source Runtime에서 `dist/.mpa/runtime/`으로만 한정하고, 설치 대상 갱신은 사용자의 명시적 릴리즈·배포 요청에서 immutable bundle 절차로만 수행하게 명확히 했다. 또한 minor 구현 fast-path는 `구현 중` 상태와 유효한 승인해시가 없으면 최소 확인조차 시작하지 않고 경량 절차로 돌아가 계획 요청인지 실행 요청인지 재판정한다. 두 경계의 회귀 검사 2개를 추가했고 독립 검증자가 수정 후 해결을 재확인했다.

## 요구사항 명세 대비 변경 사항

| 변경 | 이유 | 명세 영향 | 보고 |
|---|---|---|---|
| implementer·검증 결과 처리·workflow 참조 추가 | 실제 실행에서 중복 질문/수동 기록 요구가 남음 | 승인 범위의 활성 호출자 보완 | 진행 안내 및 policy-audit |
| core minor 자동 승인 조건 명시 | 계획 요청도 approve할 수 있는 중복 문구 제거 | 없음 | 검증 기록 |
| discovery 종료·분류 및 승인 기록 복구 문구 보완 | 1차 독립 검토의 잔존 충돌 2건 및 관련 활성 호출자 | 없음 | 사용자 진행 안내·검증 기록 |
| team_collaboration의 새 스레드 지시 제거 | 2차 검토에서 남은 단계 전환 중복 지시 발견 | 없음 | 사용자 진행 안내·2차 검토 재확인 |
| Runtime 배포 경계·minor 직접 진입 보완 | 최종 독립 검증 P4/P5 | 없음 | independent_verification 재검증 |

## 검증 포인트

- [x] 새 회귀 검사 11개 포함 최종 전체 단위 테스트 153개 통과.
- [x] 전체 단위 테스트 150개 통과 (독립 검토 반영 전 1차 실행), 최종 153개 재검증 통과.
- [x] 독립 1·2차 검증 및 F1~F3 수정·재검증. 남은 즉시 수정·주의 0건.
- [x] 최종 source/dist 58개 asset parity·승인해시 일치·diff 검사 통과.

정적 문구 검사는 알려진 누락과 충돌만 검출한다. 자연어 의미 정합성은 독립 검토와 사례표로 보완하며 실제 환경 준수까지 입증하지 않는다.
