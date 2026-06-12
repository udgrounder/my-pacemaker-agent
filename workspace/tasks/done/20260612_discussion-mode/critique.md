# 독립 비평: discussion-mode

> 설계 과정을 모르고 plan.md 결과물만 보고 약점을 찾았다. 모든 주장은 실제 파일(grep/read)로 검증했다.

## 비평 결과

### 🚨 실패 시나리오

- **시나리오 1 (라우팅 우선순위 충돌 — 미설계):** §2 "판단 우선순위"는 순서가 고정돼 있다 — `1.명시적 유형 선언 → 2.동작 서술 vs 추가 요청 → 3.키워드 힌트`. "이거 개선 논의하자"는 **2단계에서 "~하자"(추가 요청) = 리팩터링**으로 먼저 잡힌다. 키워드 테이블(3단계)은 그 뒤다. plan Step 6은 "토론 키워드 우선 판정 메모"를 키워드 테이블에 붙이겠다는 것인데, 메모는 **3단계 위치**에 있고 충돌은 **2단계**에서 일어난다. plan의 반례 1 "완화"는 메커니즘이 없다. → 토론 발화가 여전히 리팩터링/새 기능으로 오라우팅된다. **이것이 바로 이 태스크를 낳은 그 사고(미스라우팅)의 재발이다.**

- **시나리오 2 (신규 설치본에서 §4 면제 룰이 가리키는 폴더 부재):** Step 7은 `.mpa-workspace/core/agent_rules.md §4`를 "think-more/ → workspace/exploration/ 폴더 기반 면제"로 재작성한다. 이 파일은 **dist로 미러되어 모든 신규 프로젝트에 배포된다**(확인: `dist/.mpa-workspace/core/agent_rules.md`). 그러나 `dist/workspace/`는 스켈레톤이며 `exploration/` 폴더가 없다(확인: `dist/workspace`엔 .gitkeep·README·INDEX뿐). → 신규 설치 프로젝트에서 "workspace/exploration/ 내 작업은 Task 면제"라는 룰이 **존재하지 않는 폴더**를 가리킨다. plan Step 5는 discussion 흐름에 한해 "폴더 없으면 생성"을 명시하지만, §4 면제 룰 자체의 폴더 부재 처리는 어디에도 없다.

- **시나리오 3 (README 아키텍처 서술 붕괴):** README.md는 think-more/를 **경로가 아니라 정체성**으로 서술한다 — L160 표에서 think-more/를 `.mpa-workspace/`·`workspace/`와 **나란히 놓인 독립 레이어**로, L192에서 "설계 사고·탐구 공간 **(설치되지 않음)**"으로 규정한다. plan은 이를 "think-more/ → workspace/exploration/ 단순 참조 갱신"(Step 3)으로 처리한다. 그러나 think-more를 workspace/ **안으로** 넣으면 "설치되지 않는 별도 레이어"라는 문서화된 구분이 **사실과 모순**된다(workspace/는 설치 대상 영역). → 경로만 바꾸면 README L160 표·L192 트리가 거짓이 된다. 이건 sed 치환이 아니라 아키텍처 서술 재작성이 필요한데 plan은 분량을 "참조 갱신"으로 과소평가했다.

- **시나리오 4 (재진입 누락):** §"세션 시작 루틴"은 진행 중 작업의 primary source를 `workspace/tasks/active/`로만 본다(확인: agent_rules L37). 토론은 active 미등록이므로, 다음 세션 시작 시 진행 중 토론이 **상태 보고에 전혀 안 잡힌다**. plan 반례 4는 "사용자가 '이어서 논의하자' 발화"에 전적으로 의존 — 사용자가 잊으면 토론은 영구히 보이지 않는다. plan은 이를 "범위 외"로 처리했으나, 개발 태스크는 active 폴더가 망각을 막아주는 반면 토론은 그 안전망이 통째로 빠진다는 비대칭을 인정만 하고 보완하지 않는다.

### ⚠️ 숨은 가정 (파급효과 높은 순)

- **가정 1 (dist 동기화 = .mpa-workspace 미러뿐):** Step 10은 "dist 동기화 = .mpa-workspace 미러". 그러나 `dist/.mpa-workspace/upgrade-candidates/`가 **독립적으로 존재**하며 `archive/` 하위폴더까지 갖는다(확인). Step 8(upgrade 후보 archive)이 source의 `upgrade-candidates/`만 건드리고 dist 미러를 빠뜨리면 dist에 stale 상태가 남는다. 단, `discussion-mode-routing.md`는 dist에 없으므로(확인: dist엔 `minor-task-essential-questions.md`만) 이번 archive 자체는 안전 — 그러나 plan의 "dist = 미러" 단순화가 upgrade-candidates 디렉터리의 독립성을 인지하지 못한 것은 다음 작업에서 사고를 부른다.

- **가정 2 (settings.local.json think-more 참조 = 의미 있는 참조):** plan은 `.claude/settings.local.json`을 "참조 갱신" 대상으로 넣는다. 실제 확인하니 그 think-more 언급은 **grep 명령 permission allow-rule 안의 리터럴 절대경로**(L10)다 — 코드가 따르는 참조가 아니라 한 번 쓰고 만 권한 캐시 항목이다. 갱신해도 무해하지만, plan이 이를 "깨지는 참조"로 분류한 건 오진이다. 진짜 위험은 다른 데 있는데(README 아키텍처) 노이즈 항목에 주의가 분산된다.

- **가정 3 (think-more 참조 = 11개 파일):** plan 반례 3은 "이미 11개 파일 식별". 실제 grep 결과 source 영역 참조는 `README.md, .mpa-workspace/core/agent_rules.md, guidebook/guidebook.md, .claude/settings.local.json, think-more/README.md, dist/.mpa-workspace/core/agent_rules.md` + active task plan 4건. **plan 수정대상 표(L98)는 README·guidebook·settings 3개만 명시**하고 `dist/.mpa-workspace/core/agent_rules.md`의 think-more 면제 룰(L184), `think-more/README.md` 자체를 §"수정 대상"에 누락했다. dist agent_rules는 Step 7에서 source를 고치고 Step 10에서 미러로 따라온다 치더라도, plan 본문에 명시가 없어 구현자가 dist §4를 안 고칠 위험이 있다.

### ❓ 미해소 비가시적 위임

- **항목 1 (문서 "용도별 재분류" 기준 미정):** Step 1은 think-more 22개 문서를 "제목·내용 기준으로 discussion/research/use_cases에 재분류"하라 하고 "모호하면 사용자 확인"으로 위임한다. 그러나 think-more는 **이미 discussion/research/use_cases 3-폴더 구조**를 갖고 있다(확인). "단순 rename이 아니라 재분류"라는 지시는 기존 분류를 흔들겠다는 것인데, **무엇을 옮길지 기준이 없다**. 예시로 든 `principles.md`("확립된 원칙은 active discussion과 성격이 다를 수 있음")는 옮길 곳조차 모호하다(use_cases도 research도 아님). → 사실상 "구현 중 즉흥 판단"으로 위임됐다. minor 면제 영역이 아닌 이상 이건 설계 결정인데 plan은 "암묵적 결정으로 확정"이라 주장하면서 정작 기준을 안 줬다.

- **항목 2 (토론 진입/이탈 판정 임계 미정):** plan은 진입을 "논의하자/토론하자" 발화로, 이탈을 "사용자 종료 선언"으로 둔다. 그러나 토론 중 "이건 만들자"(개발 핸드오프, Step 5 출구)와 "이 부분 좀 더 논의하자"(토론 지속)의 경계, 토론 중 발생한 단순 질문이 토론을 이탈시키는지가 미정. inject/discussion_mode.md(Step 5)가 이를 정의할 책임을 지지만 plan 단계엔 판정 규칙이 없어 "구현 시 알아서"로 위임됐다.

- **항목 3 (엮인 multi-agent 토론 "재시작 가능"의 상태 모순):** Step 9는 `multi-agent-utility-discussion`을 "dev 의례 없이 정리 후 done 보관 + 토론 모드로 재시작 가능"이라 한다. done에 보관된 태스크의 회의록을 exploration/discussion/으로 옮긴 뒤 "재시작"하면, 그 토론의 새 라이브 문서와 done에 남은 과거 task plan이 **이중 진실원**이 된다. 재시작 시 과거 기록을 어떻게 연결할지(이어쓰기? 새 문서?) 미정.

### 🔧 구조적 문제

- **항목 1 (Step 순서 — 라우팅이 폴더보다 먼저면 안전하나, §4 룰이 dist에서 깨짐):** plan은 "폴더 생성/이관 → 룰"(Step 1→7) 순서를 지켰고 source 프로젝트에선 안전하다. 그러나 Step 7이 고치는 §4 면제 룰은 dist를 통해 **폴더가 없는 신규 프로젝트로 배포**된다(시나리오 2). 즉 순서 문제가 아니라 "이 룰은 source 폴더 구조를 전제하는데 배포 대상엔 그 구조가 없다"는 **배포 정합성 결함**이다. think-more 면제(현 §4)는 think-more/가 설치 안 되므로 "있으면 적용" 식으로 무해했지만, exploration은 workspace/ 하위라 "설치 영역인데 폴더는 없는" 어정쩡한 상태가 된다.

- **항목 2 (discussion_partner 페르소나와 기존 검증 페르소나 역할 중복 미정리):** Step 4 `discussion_partner.md`는 "동조 금지·steelman 후 반론·가정 표면화"를 핵심으로 한다. 이는 기존 `personas/code_reviewer.md`(비평)·독립 비평 세션의 역할 규칙과 상당 부분 겹친다. plan은 새 페르소나의 **차별점**(개발 반사 억제, 확립/열림 구분)만 나열하고 기존 비평 페르소나와의 관계(상속? 별개?)를 정의하지 않는다. 페르소나 증식 시 일관성 부채가 쌓인다.

- **항목 3 (guidebook은 "설명 레이어"인데 완료 후 업데이트로 미룸):** §"완료 시 문서 업데이트"에 guidebook을 넣었으나(L137), guidebook L5는 think-more/discussion/을 **직접 가리키는 깨지는 참조**다. 이건 "설명 보강"이 아니라 "깨진 경로"이므로 Step 3(참조 갱신, 구현 단계)에서 처리해야 할 항목인데 완료 후 단계로 분리돼 구현 중 grep=0 검증(검증 체크리스트 L128)과 모순된다 — 완료 전엔 guidebook에 think-more가 남아 있어 "grep think-more = 0" 검증이 실패한다.

---

## 발견 요약
- 🚨 실패 시나리오: 4건 (라우팅 우선순위 충돌, 신규설치 폴더 부재, README 아키텍처 붕괴, 재진입 누락)
- ⚠️ 숨은 가정: 3건 (dist=미러 단순화, settings 오진, 참조 11개 주장 vs 누락)
- ❓ 비가시적 위임: 3건 (재분류 기준, 진입/이탈 판정, 재시작 상태 모순)
- 🔧 구조적 문제: 3건 (배포 정합성, 페르소나 중복, guidebook 단계 모순)

**가장 치명적 2건:** ① 시나리오 1 — Step 6의 "메모"가 충돌 지점(§2 2단계)을 못 막아 미스라우팅 재발. ② 시나리오 2/구조1 — §4 룰이 dist 배포 시 존재하지 않는 폴더를 가리킴.
