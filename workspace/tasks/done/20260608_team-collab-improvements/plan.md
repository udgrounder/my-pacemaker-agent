---
태스크: team-collab-improvements
생성일: 2026-06-08
타입: major
실패비용: major
상태: 완료 승인
승인해시: 84c65c57e694a297
---

# 태스크: 팀 협업 개선 3종

**목적:** 팀원이 Git으로 workspace/를 공유하고 어떤 에이전트로도 언제든 이어서 작업할 수 있도록 세 가지를 개선한다.

---

## 에이전트 보고

### 사용자 결정 필요
- ~~**[A] inject 파일 우선순위 구조 형식**~~ → **결정: 공통 섹션 파일 생성 후 두 inject 파일이 참조**
- ~~**[C] 가이드북 팀 협업 섹션 위치**~~ → **결정: 10장(세션 연속성) 뒤 11장으로 추가**

### 에이전트 가정
| 가정 | 근거 | 틀렸을 때 영향 |
|------|------|--------------|
| inject 우선순위가 필요한 파일은 서브에이전트를 쓰는 것들 — layer1_critique.md, layer1_review.md | 두 파일만 "Agent 도구" 의존 | 다른 파일도 해당되면 범위 확대 |
| .codex/hooks.json의 `--agent claude`는 install.py 버그 | spec.md는 `--agent codex`로 정의됨 | 의도적이었다면 수정 불필요 |
| 가이드북 팀 협업 섹션은 신규 추가 (기존 team_collaboration.md 내용을 가이드북으로 올림) | 현재 가이드북에 팀 협업 섹션 없음 | 없음 |

---

## 구현 단계

- [x] **A. inject 파일 우선순위 명확화**
  - 대상: `layer1_critique.md`, `layer1_review.md` (서브에이전트 의존 파일)
  - 현재: "서브에이전트 우선, fallback 자가 비평"이 본문에 묻혀 있음
  - 변경: 파일 상단에 실행 우선순위 블록을 명시
    ```
    실행 우선순위:
    1순위. 서브에이전트 (Agent 도구 지원 시)
    2순위. 자가 비평 (미지원 시 — 제약 명시 후 진행)
    ```
  - dist/ 동기화 포함

- [x] **B. .codex/hooks.json 버그 수정**
  - `--agent claude` → `--agent codex` (3개 스크립트 모두)
  - install.py의 codex hooks 생성 부분도 확인 후 수정

- [x] **C. 가이드북 팀 협업 섹션 추가**
  - 핵심 메시지: workspace/를 Git으로 공유하면 어떤 에이전트로도 언제든 이어서 작업 가능
  - 포함할 내용:
    - 팀 협업의 기본 구조 (Git 공유 + 에이전트 무관)
    - workspace/ vs 세션 메모리 역할 분리 (팀 공유 vs 개인)
    - memory/ 변경 시 PR 리뷰 원칙
    - Layer 0 공동 → 개인 Layer 1 → 팀 Layer 2 흐름

---

## 검증 체크리스트
- [ ] layer1_critique.md와 layer1_review.md에서 우선순위 블록이 맨 위에 위치하는가
- [ ] .codex/hooks.json에서 모든 스크립트가 `--agent codex`를 쓰는가
- [ ] install.py가 생성하는 codex hooks도 `--agent codex`인가
- [ ] 가이드북 팀 협업 섹션이 흐름상 자연스러운 위치에 있는가

## 반례
- inject 파일 상단에 우선순위 블록을 넣으면 파일이 길어 보일 수 있음 → 간결하게 3줄 이내로 유지
- 가이드북 팀 협업 섹션이 너무 길어지면 오히려 읽히지 않음 → 핵심만, team_collaboration.md 전체를 옮기지 않음

## 수정 대상 파일
- `.mpa-workspace/inject/layer1_critique.md`
- `.mpa-workspace/inject/layer1_review.md`
- `dist/.mpa-workspace/inject/layer1_critique.md`
- `dist/.mpa-workspace/inject/layer1_review.md`
- `.codex/hooks.json`
- `install.py` (codex hooks 생성 부분)
- `guidebook/guidebook.md`
