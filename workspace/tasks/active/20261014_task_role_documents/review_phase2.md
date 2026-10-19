# 독립 구현 검증 — 2차

판정: 승인된 재사용 가이드·템플릿·Runtime 및 현재 작업 최초 적용 범위에서 통과. 남은 즉시 수정 0건, 주의 0건. 테스트 진행 가능. 사용자 완료 승인이나 외부 설치·배포 완료를 대신하지 않는다.

## 입력·수행 경계

구현 대화를 상속하지 않은 독립 담당으로 수행했다. 첫 입력은 task_documents.py inputs plan.md --stage review2 출력이며 이후 현재 plan/implementation/verification/changelog, review_phase1.md, 실제 helper·hook diff·테스트, architecture.md를 읽었다. 공유 contracts.md는 해당 경로에 없으며 layer1_review의 존재 시 입력 조건에 따라 누락 계약으로 처리하지 않았다. engineering:code-review, 코드 검토자 역할 및 경로 추적·반례 탐색 기준을 적용했다.

소스·명세·선택 문서 기준은 수정하지 않았다. 두 review 산출물만 Write 도구로 저장했다. 추가 에이전트·상위 모델 호출, 실제 release/deploy/sync는 하지 않았다. 전체 테스트의 임시 프로젝트 deploy 로그는 실제 프로젝트 배포 증거가 아니다.

## 1차 발견과 실행 주장 대조

| 발견 | 실제 보완·회귀 근거 | 판정 |
|---|---|---|
| R1 단일형 review2 실행 기록 누락 | inputs review2에서 plan 전체를 base로 제공. minimal single 및 legacy 회귀는 실행/현재 상태/TODO가 2차에 남음을 검사 | 보완 확인 |
| R2 승인/복구 확인 누락 | READY_STATES 뒤 approval_hash_issue(check_documents=False)를 먼저 수행. 미승인/명세 불일치/복구 잔존 회귀는 implement/review1/review2 거부 | 보완 확인 |
| R3 무관한 조사 누락 차단 | implement/review1은 implementation/verification/ui_design만 inspect. 전체 audit·critique/review2는 전체 검사. 관련 없는 research 누락 회귀 통과 | 보완 확인 |
| R4 legacy 설계 기준 누락 | 기존 실행 계획의 사전 조사·예상 결정·반례만 발췌하고 section은 상위 heading에서 종료. legacy 설계/검증 sentinel 유지, 실행/TODO/완료 sentinel 배제 | 보완 확인 |

changelog는 네 발견과 보완을 모두 기록하며 review_phase1의 수정 후 재검증과 일치한다. 구현자 설명만으로 1차 판정을 바꾸지 않았다. 추가 비정상 등록 role=list/dict 보완은 helper의 isinstance(str) 선행 검사와 bad registry 두 입력을 실제 확인했다. 최종 changelog도 이 보완을 기록하며 전체 테스트에 포함된다. 승인된 형식 검사 범위의 경계 보완이고 새 명세나 실행 권한이 아니다.

정상 경로는 승인된 현재 plan → 승인/복구 확인 → 등록/기준 checksum 검사 → 역할 입력 추출까지 실제 실행했다. 실패 경로는 미승인/명세 불일치/복구 잔존 및 잘못된 role JSON → 정상 ValueError 진단을 코드와 회귀로 추적했다. approve/check/audit/gate/session 변경은 문서 오류를 승인 오류와 구분하며 기존 승인 거래·일반/critical 강도를 확장하지 않는다.

## 현재 계획·승인·이력·문서 소유

- plan은 검증 중, reqspec-v1:379e670bdd19a370이다. plan_hash check가 exit0으로 같은 명세를 확인했다. 두 선택 문서는 동일 spec 및 실제 basis checksum과 일치하고 inspect issues=[]이다.
- implementation은 설계/실행/진행 정본, verification은 판정 방법 정본이다. verification에 현재 구현 성공 주장·결과를 넣지 않았다. plan은 선택 이유·담당·링크·전체 요약을 유지한다. 화면 요구가 없어 ui_design 미선택은 정상이다.
- changelog는 work 지시서 기본 강제 폐기, 화면/소프트웨어 명칭 조정, implementation 통합, major 3종 강제 폐기, 최초 적용, 큰 작업/조사 예외 허용을 보존한다. 현재 기준과 폐기 방향이 충돌하지 않는다.
- Runtime 실행 요청과 정상 approve 기록은 changelog 및 plan 승인 체크에 있다. 실제 명세 해시는 직접 검증했으며 사용자 발화의 외부 원본 로그를 재감사한 것은 아니다. 문서 존재를 실행 승인으로 추정하지 않았다.
- tracked 기존 task 및 공개 Runtime contracts 경로의 git diff --name-only 출력은 비어 있었다. 다른 untracked task는 시작 전 snapshot이 없으므로 전체 무변경까지 증명하지 않는다. 현재 작업 외 일괄 전환 증거는 발견하지 않았다.
- 구현 계획 1~6은 실제 변경 파일·새 템플릿/helper/지침/사용 문서 및 회귀로 뒷받침된다. 7의 독립 검증은 1차 결과와 이번 2차로 수행했다. 최종 사용자 완료 승인 항목은 계속 대기하며 검증자가 대신 처리하지 않는다.

### C1 요약 수치 불일치 — 보완 확인

최초 읽은 plan은 233개, implementation/changelog는 236개였다. 독립 실행은 236개다. 메인이 plan 현재 상태를 236개와 미확인 경계 표시로 갱신하고 changelog에 불일치 보완을 기록했다. 저장 직전 두 실제 파일을 다시 읽어 반영을 확인했다. 승인 명세·역할 기준 변경이 아니며 남은 주의 항목은 없다. plan의 일부 상위 실행 TODO는 결과 정리 과정의 요약 표시이며 역할별 상세 체크를 복제하도록 요구하지 않는다.

## 완료 기준 9 — 입력 충분성과 실수행 구분

이번 독립 담당은 역할 문서·승인 기준·실제 소스로 구현 대화 없이 판정 및 결과 저장을 수행했다. 1차도 기준 발췌로 실제 결함 네 건을 발견·재검증했다. verification의 미상속 검증 인계→review 산출물이라는 실제 활용 조건은 두 호출과 결과로 확인된다.

별도 구현 담당의 source 수정 실수행은 없었다. 승인 범위는 implementation을 메인 또는 단일 담당이 수행하도록 허용하며 모든 구현을 추가 에이전트에 넘기는 것을 요구하지 않는다. 요구9의 핵심인 fixture 실행 순서·허용 범위 이해는 다음 읽기 전용 인계 실험으로 확인했다.

- /tmp/mpa-review2-memory-fixture 경로의 plan/implementation을 문자열로 구성했다. Path.read_text/is_file/is_symlink, open 및 복구 존재 판단을 mock했다. 디스크 fixture·실제 파일은 생성/수정하지 않았다. 가상 reqspec 해시 e9dfbf04f63a3885와 basis checksum으로 정상 승인/입력 경로를 사용했다.
- 완료 기준1은 읽기 전용 helper 승인 경계 보존이다. 단일 구현자·승인 변경은 메인, helper 내부만 허용, dist 직접 수정/다른 작업/명세 변경 금지, 승인 경계 확인→누락/불일치 회귀→source/dist 동치의 순서, implementation 진행 기록에 결과 저장 조건을 입력에 담았다.
- implement 출력은 plan+implementation 두 입력만 제공하며 IMPLEMENTER_HISTORY_NOT_NEEDED 이력은 제외됐다. 독립 소비자인 이 담당은 과거 완료 설명이나 추가 질문 없이 위 실행 순서·금지 범위·산출물 위치를 파악할 수 있었다. 현재 작업의 실제 implement 출력도 plan/implementation/verification으로 한정되며 1~7단계·수정 대상·제외 범위·상위 제약을 보존했다.
- 이 실험은 구현 수행 준비와 최소 입력 충분성 확인이다. 별도 구현 담당의 실제 제품 수정·완성이나 토큰/시간 절감 증거가 아니다. implement는 진행 기록을 제거하므로 실제 재개 시 중단 지점 자동 전달까지 보장하지 않는다. 필요한 재개 진행 섹션은 명시 전달해야 한다.

fixture의 순서·범위 이해와 실제 독립 검증 인계는 승인된 문서·Runtime 도입의 완료 증거로 충분하다. 별도 구현 담당의 실제 source 수정 호출을 추가 필수 조건으로 만들 근거는 없다. 큰 조사도 현재 필요가 없어 실생성을 요구하지 않는다. nested research fixture, 상대 경로/누락/기준 검사 및 상위 등록 지침으로 선택적 분리 관리 계약을 확인했다. 실제 큰 조사 담당 수행은 미확인이다.

## 완료 기준별 최종 대조

| 기준 | 근거 | 판정 |
|---|---|---|
| 1~3 최소 plan/선택/정본 | 현재 작업 선택 이유·역할 소유·major/minor 조합·단일형 호환 | 통과 |
| 4 역할 인계/큰 작업 선택 분리 | 실제 검증 인계·역할 입력·nested research fixture·지침 | 범위 내 통과; 큰 조사 실수행 미확인 |
| 5 승인·복구 | 현재 승인해시 check·승인/갱신/복구 회귀·거래 diff | 통과 |
| 6 1차 격리/2차 대조 | 1차 제한 읽기 기록·split/legacy sentinel·이번 주장 대조 | 통과; 파일 접근 권한 봉쇄를 뜻하지 않음 |
| 7 이력/기준 연결 | 현재 changelog·checksum/spec 검사·중단/재개·legacy 회귀 | 통과; 전환 전 전체 원본 snapshot 동일성은 미확인 |
| 8 fixture/Runtime 동치 | 독립 전체236 테스트·source/dist diff exit0 | 통과 |
| 9 입력 충분성 | 읽기 mock 구현 인계 이해·실제 미상속 검증 담당 수행 | 범위 내 통과; 실제 별도 구현 수정/정량 효율은 미입증 |

## 직접 실행 증거·남은 경계

PYTHONDONTWRITEBYTECODE=1 전체 unittest discover를 독립 실행했다. 최초 실행은 exit0이었으나 출력 축약에서 최종 합계가 보이지 않아 메모리 로그 수집 방식으로 다시 실행했다. 직접 확인한 결과: Ran 236 tests in 4.450s, OK, failures=0, errors=0. 부모 보고나 1차의 104개 수치와 구분한다.

task_documents inspect: issues=[] 및 두 basis 일치. plan_hash check: 일치 reqspec-v1:379e670bdd19a370, exit0. diff -qr .mpa/runtime dist/.mpa/runtime: exit0, 차이 없음. 마지막 plan/changelog 요약 변경은 Runtime 변경이 아니므로 전체 테스트 반복 대신 실제 요약 파일 대조를 했다.

외부 설치 프로젝트·실제 호스트 hook, 자동 모델 선택, 실제 큰 조사, 별도 구현 담당 source 수정, 정량 효율은 확인하지 않았다. release/deploy는 명시 제외 범위이며 화면 구현이 없어 실제 UI 시각 검증은 비적용이다. 승인된 source/문서/fixture의 완료 증거와 외부 적용 검증을 구분한다.

승인 범위 밖 조용한 결정이나 틀린 에이전트 가정을 발견하지 않았다. checksum을 의미 인증으로 취급하지 않는 지침·검토 구조와 major 실패비용 분류는 유효하며 별도 보정 기록은 필요하지 않다. 메인은 근거 확인 뒤 사용자 테스트/결과 확인 단계로 진행할 수 있다.

## UI HTML 미리보기 추가 검증 — 2차

판정: 사용자 요청 “ui 의 경우 요청시 html 파일로 디자인을 보여 주는 부분도 추가해줘”의 지침 추가 범위 통과. 남은 즉시 수정 0건, 주의 0건. 이번 추가 판정은 기존 236개 테스트 범위와 구분한다.

review_phase1.md 끝의 추가 검증과 Runtime 정본의 HTML 단락, ui_design_template의 요청 시 HTML 섹션, docs/task-documents와 guidebook 관련 설명을 읽고 현재 plan 운영 안내·implementation 진행 기록·changelog의 추가 보완 주장을 대조했다. 모두 요청 시 HTML 작성→실제 렌더 확인→열어 보여주기/클릭 가능한 링크 제공을 동일하게 설명한다. 도구 부재 시 여는 방법과 렌더링 미확인 안내, 화면 상태·반응형·확인용 상호작용, 예시/가상 동작 표시, 실제 제품 구현·서버 연동과의 구분은 Runtime 정본에 명시되어 있다.

작은 작업은 plan에서 화면 기준/미리보기 경로/버전을 연결하고 별도 ui_design이나 고정 폴더를 강제하지 않는다. HTML은 디자인 자료이며 mpa-doc Markdown 역할 문서로 등록하지 않는다. 변경 시 연결 기준·버전/시점도 확인하며 checksum만으로 HTML 검증을 대신하지 않는다. 이 내용은 기존 선택 문서·명세 정본·승인/생명주기 권한을 유지하는 실행 방법 보완이고 새 문서 타입이나 승인 권한이 아니다.

현재 plan 운영 안내와 implementation 진행 기록은 이 절차의 지침 반영을 설명한다. changelog는 기존 승인 요구사항/해시를 변경하지 않는 보완임을 기록하고 이전 236개 테스트·독립 검증 증거와 이번 문구 검증을 구분한다. 실제 HTML을 제작하거나 화면을 확인했다고 주장하지 않으며 1차 추가 판정과 충돌하지 않는다.

직접 확인: source/dist의 inject/task_documents.md 및 templates/ui_design_template.md 각각 diff -q exit0, 차이 없음. 관련 구조5/정책15 검사, diff 검사·승인해시 check 통과 및 sync-runtime 수행은 전달된 메인 실행 기록이며 이번 2차가 재실행한 수치로 주장하지 않는다. 코드 변경 없는 지정 문구 보완이므로 테스트 확대·새 테스트·HTML 실생성은 수행하지 않았다.

실제 특정 UI HTML 작성·브라우저 렌더·열기 흐름은 이번 요청 범위가 아니며 미실행/미확인이다. 지침 추가 완료와 실제 디자인 산출물 완료를 구분한다. 발견한 주장 불일치·누락 변경·추가 조용한 결정은 없다.
