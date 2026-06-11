# 작업 내역서: readme-consolidation

**작업일:** 2026-06-11
**계획서:** `plan.md`

---

## 변경 파일 목록

| 파일 경로 | 변경 유형 | 설명 |
|---------|---------|------|
| `dist/.mpa-workspace/core/agent_rules_detail.md` | 수정 | "기억 여부 판단" 섹션 신설(memory/README 고립 규칙 이전) + "MPA 파일 수정 세부"에 직접수정금지 원칙 보강 |
| `dist/.mpa-workspace/core/agent_rules.md` | 수정 | detail 로드 트리거 표에 "기억 여부 판단" 행 추가 |
| `dist/.mpa-workspace/inject/layer1_implement.md` | 수정 | "세션 종료 시" 머리에 기억판단 질문 + detail 참조 |
| `dist/.mpa-workspace/inject/layer1_review.md` | 수정 | 〃 |
| `dist/workspace/README.md` | 추가(신규) | 설치본 사용자용 통합 안내 — workspace/ + .mpa-workspace/ 소개·직접수정금지(사람용) |
| `README.md` (루트) | 수정 | "Hook (가드레일)" 섹션 신설(hooks/README 운영정보 흡수) + dist/설치본 디렉터리 트리 갱신 |
| `install.md` | 수정 | hook 박스의 "자세한 내용은 hooks/README" 참조 꼬리 제거 |
| `agent-specs/claude/spec.md` | 수정 | 〃 참조 꼬리 제거 |
| `install.py` | 수정 | `remove_obsolete_readmes()` 추가 — 업그레이드 시 폐기된 폴더별 README를 고정 경로 3개만 삭제(사용자 파일 불가침) |
| `dist/workspace/{tasks,memory,docs}/README.md` | 삭제 | workspace/README.md로 통합 |
| `dist/.mpa-workspace/README.md`, `knowledge/README.md`, `hooks/README.md` | 삭제 | 정본 중복 제거 / 운영정보는 루트 README로 흡수 |
| 위 전부의 이 레포 설치본 사본 (`.mpa-workspace/`, `workspace/`) | 동기화 | dist→설치본 복사·삭제 일치 |

---

## 상세 변경 내역

### `agent_rules_detail.md` — "기억 여부 판단" 섹션
- memory/README의 유일 콘텐츠("다음 AI 세션이 모르면 다른 결정?" 판단 질문 + 기록 위치 분기)를 이전. 정본 중복(문서작성 원칙·Tier)은 principles/shared_template 참조로 대체.
- agent가 런타임에 읽지 않던 "죽은 규칙"을 주입 경로(detail + inject 트리거)에 연결해 복원.

### `install.py` — `remove_obsolete_readmes()`
- `_OBSOLETE_WORKSPACE_README` 고정 상수(3개)에 한해 업그레이드 시 삭제. `_merge_dir`은 추가/교체만 하므로 삭제는 화이트리스트로만.
- 단위 테스트: 폐기 3개 삭제 + 사용자 생성 README 2개 보존 PASS.

---

## 계획서 대비 변경 사항

- 없음 (Step 0~10 계획대로, 비평 7건 모두 반영해 진행)

---

## 검증 포인트

- [x] 정상 경로: 삭제된 README 활성 참조 0건 / dist↔설치본 5파일 동일 / workspace/README.md 신규 존재
- [x] 실패 경로: install.py 삭제 로직이 고정 3개만 삭제, 사용자 README 보존 (단위 테스트 PASS)
- [x] plan.md 완료 기준: install.py 문법 OK, guidebook 정합(삭제 README 미참조)
