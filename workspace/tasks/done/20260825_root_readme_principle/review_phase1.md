## 검토 결과

### ✅ 정합성 확인

- `.mpa/runtime/core/agent_rules.md`와 `dist/.mpa/runtime/core/agent_rules.md`는 파일 및 Runtime 트리 전체가 일치한다 (`cmp -s`, `diff -qr` 성공). Root README 원칙은 목적·적합한 사용 상황·시작 방법·계획서의 역할과 위치·기본 구조·이슈 흐름을 README 단독 이해 항목으로 명시한다.
- Root `README.md`는 설치 대상 경로를 포함한 시작 예시, `workspace/tasks/active/[작업명]/plan.md` 생성과 `done/` 보관, 재개 방법, 루트 `docs/`의 역할, 관찰→이슈 기록→사용자 요청 수집·검토→채택 항목 반영의 흐름을 실제로 설명한다. `install.md`와 `workspace/issues/README.md`의 사용자 확인·채택/기각 처리 원칙에도 모순되지 않는다.

### ⚠️ 주의 필요

- **[중간] guidebook의 설치본 구조가 현재 원칙과 모순된다.** `guidebook/guidebook.md:498-527`은 `docs/`를 `workspace/` 하위(`workspace/docs/`)로 그리지만, Root README (`README.md:108-122`), `workspace/README.md:29`, 설치 가이드(`install.md:222`)는 프로젝트 루트의 `docs/`로 일관되게 정의한다. 같은 guidebook의 용어집(`guidebook/guidebook.md:1714`)도 `workspace` 구성에 `docs/`를 넣는다. 상세 문서 독자는 문서 보관 위치와 소유 범위를 잘못 이해할 수 있다.

- **[중간] 설치된 프로젝트의 `workspace/README.md`가 존재하지 않는 상대 경로의 가이드북을 안내한다.** `workspace/README.md:70`은 마스터 레포의 가이드북을 ``guidebook/guidebook.md``로 제시하지만, 설치 골격 `dist/workspace/`에는 `guidebook/`이 포함되지 않는다. 설치본에서 이 경로를 그대로 해석하면 `<project>/workspace/guidebook/guidebook.md`가 되어 접근할 수 없다. 가이드북의 위치·접근 방법을 명시하거나 설치본에서 유효한 안내로 바꿔야 한다.

### 🚨 즉시 수정 필요

- **[높음] 설치 골격의 `dist/workspace/README.md`가 `docs/` 역할을 이전 정의로 유지해 source 문서와 배포본이 동기화되지 않았다.** source `workspace/README.md:29`는 루트 `docs/`를 “개발에 필요한 문서와 진행 과정에서 생성된 문서”의 보관소로 설명하지만, 설치에 복사되는 `dist/workspace/README.md:29`는 `docs/`를 “만든 것이 어떻게 동작하나(구현 후)”로 한정한다. 이는 작업 진행 중 생성되는 문서와 개발 참고 문서도 보관한다는 Root README·Runtime 원칙에 어긋나며, 신규 설치 사용자가 잘못된 구조 설명을 받는다. `cmp -s workspace/README.md dist/workspace/README.md`도 불일치했다.

### 📝 조용한 결정 목록

- 없음. Root README 원칙을 root README에만 적용하고 guidebook·설치 안내에는 상세도를 유지한다는 범위는 Runtime 규칙에 명시되어 있어, 검토 대상 문서에서 새로 숨겨진 범위 결정은 확인하지 못했다.

### 🔍 에이전트 가정 검증

- **검증됨:** “root README는 사람이 처음 읽는 설명 레이어”라는 가정은 `workspace/memory/shared/architecture.md:19`와 Runtime 규칙(`.mpa/runtime/core/agent_rules.md:207-215`)에 현재 원칙으로 명시되어 있다.
- **보완 필요:** 설치된 프로젝트의 구조 설명도 Root README 원칙의 대상 효과(README만으로 설치본 구조와 정보 위치를 이해)를 충족한다고 볼 수 있다는 가정은 성립하지 않는다. 배포되는 `dist/workspace/README.md`의 `docs/` 설명이 source와 다르고, guidebook도 `workspace/docs/`라는 상충된 구조를 제공한다.
