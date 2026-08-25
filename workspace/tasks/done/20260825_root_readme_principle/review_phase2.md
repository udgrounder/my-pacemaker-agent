## 2차 독립 검증 결과

### 검증 범위와 방법

- 대조 기준: `workspace/memory/shared/architecture.md`, 이 작업의 `plan.md`, `review_phase1.md`, 실제 변경 파일 5개를 읽었다.
- 보조 확인: `git diff --check`는 성공했고, `cmp -s .mpa/runtime/core/agent_rules.md dist/.mpa/runtime/core/agent_rules.md`는 성공했다. `plan_hash.py check`도 현재 요구사항 명세 체크섬과 일치했다.
- `changelog.md`는 이 작업 항목에 존재하지 않는다. 이 작업에서는 이를 결함으로 단정하지 않았으며, `plan.md`의 명세 변경 이력·실행 중 변경 기록·검증 결과와 실제 diff, 1차 검토 결과를 대조했다.

### 🚨 즉시 수정 필요

1. **[높음] 신규 설치 골격의 `dist/workspace/README.md`가 `docs/`의 이전 정의를 계속 배포한다.**
   - 근거: `README.md:121,124`, `workspace/README.md:29`, `guidebook/guidebook.md:525`는 루트 `docs/`를 개발 참고 문서와 진행 과정 산출물의 보관소로 설명한다. 그러나 설치 시 복사되는 `dist/workspace/README.md:29`는 이를 “만든 것이 어떻게 동작하나(구현 후)”로 한정한다.
   - 영향: 새 설치 사용자는 진행 중 생성되는 문서·개발 참고 문서의 보관 위치를 잘못 이해한다. 이는 architecture의 root README 원칙(`architecture.md:19`) 및 이번 명세의 `docs/` 보완 결정과도 맞지 않는다.
   - 1차 검토도 발견했으며, 2차 확인에서 여전히 미해결이다.

### ⚠️ 주의 필요

1. **[중간] guidebook의 구조 트리가 루트 `docs/` 대신 `workspace/docs/`를 제시한다.**
   - 근거: `guidebook/guidebook.md:502-527`의 코드 블록은 `workspace/` 아래에 `docs/`를 배치한다. 반면 현재 architecture(`:13,19`), root README(`:108-124`), 설치 가이드(`install.md:220-223`)는 프로젝트 루트 `docs/`를 일관되게 사용한다.
   - 영향: 상세 안내 문서가 README의 기본 구조 설명을 상쇄해 문서의 실제 위치·소유 경계를 혼동하게 한다.
   - 1차 검토도 발견했으며, 2차 확인에서 여전히 미해결이다.

2. **[중간] 설치본 `workspace/README.md`의 가이드북 안내는 설치본에서 해석 가능한 경로가 아니다.**
   - 근거: source와 설치 골격 모두의 `workspace/README.md`는 “마스터 레포의 가이드북(`guidebook/guidebook.md`)”을 안내하지만, 설치 골격 `dist/workspace/`에는 `guidebook/`이 포함되지 않는다.
   - 영향: 설치된 프로젝트의 독자는 상대 경로를 따라갈 수 없다. 마스터 저장소에서 봐야 한다는 접근 방법을 명시하거나 설치본에서 유효한 안내로 바꿔야 한다.
   - 1차 검토도 발견했으며, 2차 확인에서 여전히 미해결이다.

3. **[중간] 실제 문서 변경 범위가 계획의 수정 대상 표와 실행 중 변경 기록에 완결적으로 남아 있지 않다.**
   - 근거: 실제 diff에는 `workspace/README.md`, `guidebook/guidebook.md`, `workspace/memory/shared/architecture.md`가 포함된다. 그러나 `plan.md:93-100`의 수정 대상 표에는 Runtime 규칙, root README, `dist/.mpa/runtime/`만 있고, `plan.md:130-137`의 실행 중 변경 기록에는 Runtime 규칙과 root README만 기록되어 있다. `architecture.md`는 완료 시 문서 업데이트 대상(`plan.md:126-129`)으로만 나타난다.
   - 영향: `changelog.md` 없이 plan의 실행 기록을 검토 근거로 삼을 때, 어떤 부수 문서가 왜 함께 바뀌었는지 재구성할 수 없다. 특히 guidebook·workspace README 변경은 “root README에만 적용”이라는 예상 조용한 결정(`plan.md:90`)과 겉보기에는 충돌한다.
   - 권장: 변경을 되돌릴 문제가 아니라, 실제 변경 파일별 목적·명세 영향과 source/dist 설치 골격 동기화 판단을 실행 기록에 보완한다.

### 📝 조용한 결정

1. **root README 원칙 자체는 root README에 한정하면서, `docs/` 정의 정합성을 위해 workspace README·guidebook·architecture도 함께 갱신했다.**
   - 이 판단은 내용상 합리적일 수 있으나, 수정 대상 표와 실행 중 변경 기록에 명시되지 않아 독자가 “상세 문서의 상세도는 유지”와 “상세 문서의 사실 오류 수정”의 경계를 확인할 수 없다.
   - 이것은 범위 확장 자체의 결함 판정이 아니라 기록이 필요한 결정이다.

### 🔍 에이전트 가정 검증

1. **틀림 — source `workspace/README.md`의 문구를 바로잡으면 설치본 사용자 설명도 함께 정합해진다는 암묵적 가정.**
   - `architecture.md:11`은 `dist/workspace/`가 신규 설치 골격임을 명시한다. 실제 `dist/workspace/README.md:29`는 갱신되지 않았으므로 source 문서 수정만으로 설치 사용자에게 변경이 전달되지 않는다.

2. **검증됨 — root README는 단독으로 기본 이해를 제공해야 한다는 핵심 요구.**
   - `README.md`는 목적·적합한 상황·시작 예시·작업 계획서의 역할 및 생성/보관 위치·승인/복구·사용자 자산 보존·설치 구조·이슈 수집 흐름을 자체적으로 설명한다. 링크는 상세 안내로만 사용한다.

### 1차 검토 대비 결론

- 1차의 세 가지 문서 정합성 지적은 모두 재현됐다.
- 1차가 별도로 적지 않은 사항은 실제 변경 범위와 `plan.md`의 수정 대상·실행 기록 간의 불일치다. `changelog.md` 부재는 이 작업의 결함이 아니라, 현재 작업 방식에서 plan 기록이 더 완전해야 한다는 이유로만 관련된다.
- Runtime source/dist 동기화와 root README의 단독 기본 이해 요구는 충족한다. 다만 신규 설치 골격의 README는 별도 배포 자산이므로 즉시 동기화가 필요하다.
