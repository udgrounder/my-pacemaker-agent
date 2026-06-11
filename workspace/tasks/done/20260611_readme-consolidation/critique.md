# 비평 결과

비평 대상: `workspace/tasks/active/20260611_readme-consolidation/plan.md` (상태: 설계 완료)
검증 근거: install.py 실제 코드, 루트 README.md, grep 전수 결과

---

### 🚨 실패 시나리오

- **시나리오 1 — install.py에 "삭제 전파" 로직이 *애초에 없음* (Step 6의 전제 붕괴):**
  plan은 "workspace는 merge 복사라 삭제 전파를 위해 install.py 수정 필수"라 하고, Step 6에서 "삭제 전파 로직 추가"를 한 줄로 위임한다. 그러나 실제 install.py(`_merge_dir`, L193~217)는 **추가(add)와 덮어쓰기(overwrite)만 한다. 삭제 경로가 단 하나도 없다.** dist에서 파일을 지워도 기존 설치본에는 그대로 남는다. 즉 Step 6은 "한 줄 수정"이 아니라 **install.py에 신규 삭제 메커니즘을 설계·구현하는 별도 하위 태스크**다. plan은 이 규모를 "(결정1=B인 경우만)"이라는 괄호 한 줄로 숨겼다. → 구현 단계에서 예상 범위 초과로 minor/major 경계가 흔들리고, 삭제 로직 설계(어느 디렉터리를 스캔할지, dist에 없는데 설치본에 있는 README를 어떻게 식별할지)가 비가시적 위임으로 남는다.

- **시나리오 2 — `_is_harness_managed`가 *모든* README.md를 harness 관리로 간주함 → 화이트리스트가 이미 무의미:**
  plan Step 6은 "harness 관리 README 화이트리스트 한정, 사용자 파일 불가침"을 안전장치로 제시한다. 그러나 install.py L188~190 `_is_harness_managed`는 `name == "README.md"`만 본다 — **경로·폴더 구분이 전혀 없다.** 사용자가 자기 `workspace/memory/내도메인/README.md`를 만들어도 harness 관리로 분류된다. 삭제 로직을 "README.md 이름이면 지운다"로 짜면 **사용자 생성 README까지 삭제**된다. plan이 말한 "화이트리스트"는 구체적 식별 규칙(dist 소스에 동일 경로가 있는 README만 삭제 등)을 정의하지 않았다 → 데이터 손실 시나리오 2가 그대로 살아있다. plan의 "해결책"(시나리오 2 대응)은 실제 코드 구조를 보면 미해결이다.

- **시나리오 3 — 루트 README.md L185~187이 삭제 대상 README를 *명시적으로 기술*하는데, 갱신이 조건부로 묶임:**
  루트 `README.md:185~187`은 디렉터리 트리에서 `memory/ (README + ...)`, `tasks/ (README, INDEX.md ...)`, `docs/ (README, INDEX.md)`로 **삭제될 README의 존재를 사실로 적고 있다.** README가 사라지면 이 세 줄은 거짓이 된다. 그런데 plan은 루트 README 갱신을 "완료 시 문서 업데이트 대상 — (결정 1=B인 경우)"로 **조건부·사후 항목**으로 배치했다. 결정 1은 이미 "완전 삭제"로 확정됐으므로 이 줄은 무조건 거짓이 되는데, 갱신은 사후 누락되기 쉬운 위치에 있다. → Step 4(흡수)와 별개로 L185~187 트리 수정이 **명시적 구현 항목으로 승격되지 않음.**

- **시나리오 4 — 설치본(루트 외) 기존 사용자의 깨진 링크:**
  Step 8은 "install.md:173 외 추가 참조 grep"을 말하지만, grep 결과 `agent-specs/claude/spec.md:42`도 `.mpa-workspace/hooks/README.md`를 참조한다(plan 미인지). hooks/README는 삭제 대상이 아니므로 깨지진 않으나, **plan의 참조 전수조사가 불완전했다는 증거**다. 같은 누락이 삭제 대상(`knowledge/README` 등)에 대해 없다고 단정할 근거가 약하다 — Step 8을 구현 후가 아니라 삭제 *전*에 수행해야 안전하다.

---

### ⚠️ 숨은 가정 (파급효과 높은 순)

- **가정 1 — "install.py 수정 필수"가 곧 "삭제 전파 로직 추가"라는 것 / 틀렸을 때:**
  전제는 "그 로직을 끼워 넣으면 된다"지만, 실제로는 추가/덮어쓰기 전용 머지 함수에 **삭제라는 반대 의미론을 도입**하는 것이다. 업그레이드 시 dist에 없는 모든 설치본 파일을 삭제하는 일반 로직으로 잘못 일반화하면, upgrade-candidates·사용자 도메인 파일까지 휩쓴다. 영향: 기존 사용자 데이터 손실(비가역, 실패비용 major 정당).

- **가정 2 — `.mpa-workspace`는 "통째 교체"라 dist에서 지우면 자동 전파 / 부분적으로만 참:**
  install.py L378 `shutil.rmtree(agents_workspace_dst)` 후 재복사가 맞다. 이 가정은 옳다. **그러나 이는 "업그레이드 모드"에서만 성립**한다 — `copy_agents_workspace`는 upgrade 분기에서 rmtree+copytree를 한다. 신규 설치는 문제없음. 단, 이 가정이 옳다는 사실이 가정 1(workspace 쪽)의 어려움을 가린다. 두 폴더의 동기화 의미론이 비대칭(.mpa=교체, workspace=머지)인데 plan은 이 비대칭을 정확히 짚었으나, 그 결과 workspace 삭제가 얼마나 어려운지는 과소평가했다.

- **가정 3 — codex 태스크가 이 파일들을 동시 수정 안 함(active 폴더에 없음) / 틀렸을 때:**
  근거가 "active/에 없고 INDEX에만 있음"이다. 그러나 INDEX에 있다는 건 진행 의도가 있다는 뜻이다. 이 태스크가 hooks/README를 손대지 않기로 한 것은 옳으나, **inject/layer1_implement.md·layer1_review.md 수정(Step 3)이 codex 런타임 hook 동작과 무관한지**는 검증되지 않았다. codex 태스크가 inject 파일 matcher를 건드리면 충돌 가능. 영향: 양 태스크 머지 충돌.

---

### ❓ 미해소 비가시적 위임

- **항목 1 — 삭제 대상 README 식별 규칙의 부재:**
  "harness 관리 README 화이트리스트"의 구체 정의가 없다. (a) dist 소스 트리에 동일 상대경로가 존재하면서 (b) dist에서 삭제된 README만 지울지, (c) 고정 경로 목록(`workspace/{tasks,memory,docs}/README.md`)을 하드코딩할지 결정되지 않음. 구현자가 임의 선택하게 됨 → 사용자 결정/설계 결정이 구현 중으로 새어 들어감(minor 불가, major 정당).

- **항목 2 — `.mpa-workspace/README`의 "직접 수정 금지" 경고 대체처 (plan이 ⚠️로 스스로 제기했으나 미확정):**
  plan L28이 "그 경고를 어디서 대체할지 확인 필요"라고 적었지만 어디로 옮기는지 결정이 없다. 루트 README 흡수(Step 4)에 "직접수정 금지 경고"가 들어간다고 했으나, **설치본 사용자는 루트 README를 받지 않는다**(루트 README는 harness 레포 문서이지 설치 대상이 아님 — install.py는 dist/만 복사). 즉 경고를 루트 README로 옮기면 **설치본 사용자에게는 경고가 영영 사라진다.** 이 위임은 실패한 대체처를 가리키고 있다.

- **항목 3 — 루트 README L185~187 트리 갱신의 책임 단계:**
  거짓이 될 것이 확정된 세 줄을 어느 Step이 고치는가? Step 4는 "흡수"만 말하고 트리 수정은 명시 안 함. 완료 시 문서 항목은 조건부. → 누락 위험.

---

### 🔧 구조적 문제

- **항목 1 — 단계 순서 오류: 참조 점검(Step 8)이 삭제(Step 5·6) 이후에 있음.**
  깨진 참조 확인은 삭제 *전* 영향 분석으로 해야 한다. 지금 순서는 "지우고 나서 깨졌는지 본다"로, 깨진 참조 발견 시 이미 삭제가 끝나 롤백 부담이 크다. Step 8 → Step 5 앞으로 이동 권장.

- **항목 2 — install.py 변경의 동기화/검증 누락:**
  Step 7은 "dist ↔ 설치본 동기화"인데 install.py는 dist에 있지 않다(레포 루트). install.py 수정은 동기화 대상이 아니라 **그 자체로 테스트가 필요한 코드 변경**이다. 그런데 검증 체크리스트는 "README 변경 반영" 위주이고, **install.py 삭제 로직의 단위 검증(사용자 파일 보존 + 대상 README만 삭제)이 검증 항목에 없다.** 데이터 손실 위험 대비 검증 공백.

- **항목 3 — 비대칭 동기화로 한쪽만 반영될 경로:**
  `.mpa-workspace/README`·`knowledge/README` 삭제는 dist에서 지우면 끝(업그레이드 시 rmtree). 그러나 **이 레포 자체의 설치본**(`/.mpa-workspace/README.md`, `/.mpa-workspace/knowledge/README.md` — 루트에 실재)은 dist 삭제로 자동으로 안 지워진다. 개발자가 수동 삭제해야 한다. plan의 "동기화"가 이 레포 루트 설치본의 수동 삭제를 포함하는지 불명확 → 한쪽(dist)만 지우고 루트 설치본이 잔존하면 grep·테스트가 오염된다.

- **항목 4 — minor GATE2 문구(불일치 B)의 정본 위치 미확정:**
  Step 6은 "B(tasks/README minor GATE2)도 삭제로 소멸 — 단 B 내용이 루트 README/정본에 정확한지 Step 4에서 확인"이라 한다. 그러나 minor 흐름 GATE2 규칙의 정본은 `agent_rules.md`/`session_protocol`이지 루트 README가 아니다. "루트 README에 정확한지 확인"은 정본을 잘못 지목할 위험. 삭제로 규칙이 소멸하는 게 아니라 **원래 정본에 이미 있는지**를 확인해야 한다.
