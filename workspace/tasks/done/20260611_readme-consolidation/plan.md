---
태스크: readme-consolidation
생성일: 2026-06-11
타입: major
실패비용: major
상태: 완료 승인
승인해시: cfeb518cb44792e5
---

# 작업 계획서: readme-consolidation

**파생 출처:** README 검토 요청 → 일부 내용이 정본 중복이고 일부(memory 기억판단 로직)는 정본에 없이 고립된 "죽은 규칙"임을 발견. 독립 비평(critique.md, 2026-06-11)으로 설계 약점 7건 교정. 사용자 논의로 흡수처 재설계.

---

## 에이전트 보고

### 사용자 결정 (2026-06-11 확정)

- [x] **결정 1 — `workspace/{tasks,memory,docs}/README.md` 3개 삭제 + `workspace/README.md` 단일 통합본 신규**
  - 분산은 없애되, 설치된 프로젝트 사용자가 in-place로 읽을 통합 안내를 workspace 최상위에 둔다.
  - `dist/workspace/README.md`로 만들면 설치/업그레이드 시 `_merge_dir`이 복사한다.
- [x] **결정 2 — `.mpa-workspace/README.md`, `knowledge/README.md` → 완전 삭제** (.mpa-workspace는 "직접 수정 안 하는 방법론"이라 사용자 README 불필요)
- [x] **결정 3 — `hooks/README.md`도 완전 삭제**, 고유 운영정보는 루트 README로 (아래 흡수처 표)

### 흡수처 — "사람이 읽는 건 README, agent가 적용하는 건 정본"

| 콘텐츠 | 성격 | 행선지 |
|--------|------|--------|
| memory "기억 판단 로직"(L55~71) | agent 행동규칙 | → `agent_rules_detail.md` (런타임 적용) |
| `.mpa-workspace` 직접수정금지 경고 | agent 행동규칙 | → `agent_rules_detail.md` |
| `workspace/{tasks,memory,docs}` 폴더 사용 안내 | 설치본 사용자용 | → **신규 `workspace/README.md`** |
| `.mpa-workspace/` 폴더 소개 + 직접수정금지(사람용 안내) | 설치본 사용자용 | → **신규 `workspace/README.md`** (agent 행동규칙은 별도로 agent_rules_detail) |
| hook 운영정보(MPA_GATE 설정·한계·이벤트명칭) | 사람용 매뉴얼 | → 루트 `README.md` hook 운영 섹션 |
| memory 문서작성원칙·Tier·주입매핑 | 정본 중복 | 삭제 (principles/shared_template/session_protocol에 존재) |
| GATE1/2·복구절차 (hooks/README) | 정본 중복 | 삭제 (agent_rules+detail에 존재) |

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|-----|------|---------|
| memory "기억 판단 로직"은 정본 어디에도 없는 유일 콘텐츠 | grep 0건 | 단순 중복 → 이전 불필요 |
| 삭제 대상 README를 가리키는 외부 참조 없음(hooks/README만 install.md·spec.md가 참조) | grep 전수조사 | 깨진 링크 → Step 0에서 재확인 |
| `.mpa-workspace` 직접수정금지 경고에 대응하는 정본 규칙 부재 | agent_rules_detail:234는 "수정 절차"이지 "금지"가 아님 | 이미 있으면 이전 생략 |

---

## 요청 원문

"프로젝트 내부 README 검토·개선" → "런타임 미참조 분산 문서 통합 + 고립 규칙은 주입 경로로" → "단 설치본 workspace 아래엔 사용자용 README 유지".

---

## 목적

분산 README를 (1) 정본 중복은 삭제, (2) 고립된 행동규칙은 정본 이전, (3) 설치본 사용자 안내는 `workspace/README.md` 단일본으로, (4) hook 운영 매뉴얼은 루트 README로 통합한다.

---

## 구현 단계

- [ ] **Step 0 (삭제 전 영향 분석)** — 삭제 대상 README 6개를 가리키는 참조를 dist·루트·agent-specs·guidebook 전체 grep 재확인. 깨질 링크 목록화.
- [ ] Step 1 — memory/README 층 2(L55~71) 정밀 추출: principles·shared_template·inject와 줄 단위 대조해 "유일 콘텐츠"만 확정
- [ ] Step 2 — `agent_rules_detail.md`에 "기억 여부 판단" 섹션 신설 + `.mpa-workspace` 직접수정금지 경고 통합. `agent_rules.md` 트리거 표에 로드 트리거 추가
- [ ] Step 3 — `inject/layer1_implement.md`·`layer1_review.md` "세션 종료 시" 머리에 판단 질문 1줄 + Step 2 섹션 참조
- [ ] Step 4 — **`dist/workspace/README.md` 신규 작성**: ① workspace/ 역할 + memory/tasks/docs 폴더 사용 안내(삭제될 3개 README의 사람용 핵심 통합), ② `.mpa-workspace/` 폴더 소개 + "직접 수정 말 것"(사람용), 설치본 사용자가 두 폴더를 한 곳에서 이해하도록
- [ ] Step 5 — 루트 `README.md`: hook 운영 섹션 신설(hooks/README 고유 운영정보 흡수) + L185~187 디렉터리 트리 갱신(폴더별 README → workspace/README.md 반영)
- [ ] Step 6 — minor GATE2(불일치 B) 정본 확인: `agent_rules.md`/`session_protocol.md`에 `완료 승인 ⛔G2` 흐름이 정확한지 확인
- [ ] Step 7 — install.md hook 박스 결과 요약만 유지 + install.md:173·`agent-specs/claude/spec.md:42`의 "자세한 내용은 hooks/README" 꼬리 제거
- [ ] Step 8 — install.py 삭제 전파 로직: **고정 경로 상수**(`workspace/tasks/README.md`, `workspace/memory/README.md`, `workspace/docs/README.md`)에 한해 업그레이드 시 설치본에서 삭제. workspace/README.md는 신규 추가 대상이므로 삭제 목록에서 제외. `_is_harness_managed` 이름기반 로직 미변경. 사용자 생성 README 불가침.
- [ ] Step 9 — README 삭제 실행 (dist 기준): `workspace/{tasks,memory,docs}/README.md`, `.mpa-workspace/README.md`, `.mpa-workspace/knowledge/README.md`, `.mpa-workspace/hooks/README.md`
- [ ] Step 10 — 동기화: dist ↔ 이 레포 설치본 양쪽. **이 레포 루트 설치본 README 6개 수동 삭제** + workspace/README.md 신규 반영(양쪽).

---

## 수정 대상 파일

| 파일 경로 | 변경 |
|---------|------|
| `dist/.mpa-workspace/core/agent_rules_detail.md` | "기억 여부 판단" 섹션 + 직접수정금지 경고 |
| `dist/.mpa-workspace/core/agent_rules.md` | 트리거 표 로드 트리거 |
| `dist/.mpa-workspace/inject/layer1_implement.md`·`layer1_review.md` | 세션 종료 판단 질문 + 참조 |
| `dist/workspace/README.md` | **신규** — 설치본 사용자용 통합 안내 |
| `README.md` (루트) | hook 운영 섹션 신설 + L185~187 트리 갱신 |
| `install.md` | hook 박스 요약화 + 참조 꼬리 제거 |
| `agent-specs/claude/spec.md` | hooks/README 참조 꼬리 제거 |
| `install.py` | 고정 경로 화이트리스트 README 삭제 전파 + 단위 검증 |
| 삭제: `dist/workspace/{tasks,memory,docs}/README.md`, `dist/.mpa-workspace/README.md`, `dist/.mpa-workspace/knowledge/README.md`, `dist/.mpa-workspace/hooks/README.md` | 통합 후 제거 |
| 이 레포 설치본 사본(`.mpa-workspace/`, `workspace/`) | 동기화·삭제·신규 |

## 참고 파일 (수정 없음)

- `core/principles.md`, `templates/shared_template.md`, `core/session_protocol.md` — 중복 콘텐츠 정본

---

## 반례 (비평 반영)

- 시나리오 1: install.py 삭제를 "dist에 없는 모든 파일 삭제"로 일반화 → 사용자 파일 손실. **해결: 고정 경로 상수 3개로만 한정.**
- 시나리오 2: 직접수정금지/기억판단을 루트로 옮겨 설치본 agent가 못 받음. **해결: 행동규칙은 정본(agent_rules_detail) 이전.**
- 시나리오 3: 루트 README L185~187이 거짓이 됨. **해결: Step 5에 트리 갱신 명시.**
- 시나리오 4: 레포 루트 설치본 README가 dist 삭제 후 잔존해 grep·테스트 오염. **해결: Step 10 수동 삭제.**
- 시나리오 5: workspace/README.md를 삭제 화이트리스트에 잘못 넣어 신규본이 지워짐. **해결: Step 8에서 명시적 제외.**
- 시나리오 6: memory 층2를 detail로 옮겼으나 agent가 트리거 도달 안 함. **해결: Step 3 inject 세션종료가 직접 가리킴.**

---

## 검증 체크리스트

- [ ] 정상: 새 세션 "기억 판단" 트리거 시 detail 섹션 로드 / 설치본 agent가 직접수정금지 경고 수신 / 설치본에 workspace/README.md 존재
- [ ] 실패: 삭제된 README를 가리키는 깨진 참조 0 (Step 0 대조)
- [ ] **install.py 단위 검증: 고정 경로 3개만 삭제, workspace/README.md·사용자 생성 README 보존**
- [ ] 엣지: 업그레이드 시 .mpa-workspace README(교체 전파) / workspace 폴더별 README(삭제 전파) / workspace/README.md(추가) 모두 의도대로
- [ ] dist ↔ 레포 설치본 양쪽 반영

---

## 완료 시 문서 업데이트 대상

- [ ] 루트 `README.md` — Step 5에서 구현 항목으로 처리됨
- [ ] `guidebook/guidebook.md` — memory 기억판단 서술과 정합 확인

---

## 구현 후 발견

| 항목 | 유형 | 발견 맥락 | 처리 경로 |
|------|------|-----------|-----------|
| (결과를 경험한 후 채워짐) | | | |
