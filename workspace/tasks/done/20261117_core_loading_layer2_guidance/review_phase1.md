# 1차 독립 구현 검증

## 대상·입력·판정

- 기준은 `python3 .mpa/runtime/hooks/task_documents.py inputs workspace/tasks/active/20261117_core_loading_layer2_guidance/plan.md --stage review1` 출력의 승인·요구사항·설계·검증 기준이다. 승인해시는 `reqspec-v1:2b9391f0a3bc3b21`이다.
- 실제 source/dist의 core/agent_rules.md·agent_rules_detail.md·session_protocol.md, inject/layer1_design.md·layer1_implement.md·layer1_review.md·layer1_discovery.md·layer2_checkpoint.md, templates/plan_template.md·plan_minimal_template.md·changelog_template.md, tests/test_structure_loading.py·test_todo_policy.py와 docs/mpa-internal-structure.md·guidebook/guidebook.md 및 architecture.md의 관련 내용을 검토했다.
- 구현 대화·changelog·baseline snapshot·plan 전체 진행/실행 기록·2차 결과·전체 git diff는 읽지 않았다. task_documents.md·_agent_execution_priority.md·personas/code_reviewer.md와 반례/경로 추적 계약을 적용했다.
- 판정: **수정 필요**. 아래 내용과 줄번호는 발견 시점의 소스 기준이다. 메인에 전달 후의 수정은 이 보고서에서 재평가하지 않으며 2차 검증에서 대조한다.

## 🚨 즉시 수정 필요

### R1. 존재하는 다른 정본을 가리키는 트리거 오지정을 검사하지 못함 (P2, C6)

- 대상: `tests/test_structure_loading.py:95`~115 및 `:196`~204.
- helper `loading_route_issues`는 표에서 추출한 대상 heading의 존재만 검사하며 트리거별로 기대하는 정본을 대조하지 않는다. `core/agent_rules.md:36`의 `"Layer 2 현황 표시"`를 이미 존재하는 `"계획서와 변경 이력 관리"`로 바꾼 메모리 fixture에서도 반환값은 `[]`였다.
- 현재 wrong-file fixture는 glossary에 해당 heading이 없어서 실패한다. 유효하지만 다른 정본으로 향하는 출발 참조 오지정은 검증하지 못한다.
- 추가 경계: core `:35`의 `계획 문서 생성·편집 전, 검증 입력 준비 전·재개 시`를 `계획 문서 생성·편집 전`으로 바꿔도 `[]`였다. 검증 입력 준비·재개 조건 자체가 사라져도 기존 부분문자열 검사를 통과한다.
- 영향: 실제 표의 출발 참조가 잘못된 정본으로 향하거나 보호 이벤트가 빠져도 회귀 검사가 성공할 수 있다. C6의 트리거→정본 연결 단절 탐지 범위가 불완전하다.
- 권장: 실제 표 파싱을 유지하며 주요 트리거별 기대 파일·정확한 heading 대응과 필수 검증 입력/재개 조건을 확인한다. 존재하는 다른 heading/파일 오지정 및 조건 일부 삭제를 동일 helper의 음성 fixture로 추가한다.

### R2. guidebook에 자동 Layer 2 실행 조건이 잔존함 (P2, C4/C7)

- 대상: `guidebook/guidebook.md:1353`.
- 팀 memory 변경 원칙에 `규칙 변경이 기존 작업에 영향을 주면 → Layer 2 체크포인트 즉시 실행`이 남아 있다. 같은 문서 `:935`~938과 Runtime detail `:137`~140은 안내·제안과 사용자 요청을 구별하고 자동 실행 조건을 두지 않는다.
- 영향: 사용자 요청 없이 규칙 변경만으로 전체 점검을 즉시 실행하라는 별도 조건으로 읽힌다. C7의 문서 정합성과 상충한다.
- 권장: 필요성을 제안하고 사용자 요청에 따라 수행하도록 Runtime의 동일 정본과 연결한다.

## ✅ 정합성 확인

| 기준 | 실제 근거·판정 |
|---|---|
| C1 | source/dist core 모두 33,556바이트. 기존 `CORE_BASELINE_BYTES = 34_731` 유지, 1,175바이트 여유. 설계 입력의 변경 전 36,783바이트와 비교하면 3,227바이트 감소다. 변경 전 수치는 독립 snapshot으로 재확인하지 않았다. |
| C2 | core `:35`, `:309`~315에 정본 구분·승인/실패 증거·선행 로드가 남고 detail `:100`~114에 단일 갱신자·복구 우선·현재 실패 노출·이력 선저장·TODO/운영 안내 분리가 있다. 단순 질문 자동 로드는 추가하지 않았다. |
| C3 | detail `:132`~145가 실제 Layer 2 정본이다. core `:36`, major 완료 detail `:126`, checkpoint `:182`에서 직접 도달한다. 설치 Runtime은 source memory 없이 기준을 찾을 수 있다. |
| C4 | detail `:137`~140의 major 1개/minor만 5개·minor 기본 생략·명시 요청 우선·집계 미확인·생성일 대체 금지·동일일 순서 불명은 기준과 맞는다. R2는 수정 필요다. |
| C5 | detail `:142`~145는 점검 완료 기준 충족·결과 기록 뒤에만 기존 마커를 쓰며 제안·중단·미완료에는 쓰지 않는다. 다른 행·정렬·과거 마커 보존, 저장 실패 보고, 동일일 중복 금지가 있다. done 재등록·전체 분석은 금지한다. 과거 INDEX 변경 자체의 이력 대조는 하지 않았다. |
| C6 | 실제 source/dist와 메모리 fixture가 같은 helper를 쓴다. exact_section은 정확한 heading과 fence 제외를 처리한다. 대상 삭제/rename·소비 참조 삭제/오지정 fixture는 원본을 수정하지 않는다. 기존 승인/복구·minor 직접 경로·계약 앵커·parity와 전체 테스트가 성공했다. R1은 남는다. |
| C7 | docs 내부 구조 `:15`~16, architecture `:71`, `:95`~100, guidebook `:935`~938의 정본은 Runtime과 맞으며 전체 source/dist 파일 parity가 통과했다. R2 때문에 문서 전체 정합성은 미충족이다. 구현 이력 주장·독립 검증 기록의 최종 대조는 2차 범위다. |

## 정상·실패·경계 경로

- 정상 major 완료: core 완료 진입 → detail 완료 인정/작업 항목 완료 → 사용자 완료 확인 → INDEX 행 정리·done 이동 → detail `:126`의 현황 정본 → 마커 이후 완료 근거가 확인된 major 최소 1개일 때 한 줄 제안. 자동 점검이나 마커 작성으로 이어지지 않는다.
- 실패/보호: 계획 편집 전 core `:35` 또는 minor detail `:383`·설계/구현/발견 inject 선행 경로 → 관리 정본 `:111` → `.plan-renewal.json` 잔존 시 다른 에이전트 편집 중단·복구 정본. 과거 성공 효력 상실은 `:112`에서 현재 미확인/재검증 필요·현재 실패 노출을 요구한다.
- 독립 검증 입력: implement/review inject `:5`가 입력 생성 전에 관리 정본을 읽게 하고 review `:7`이 입력 격리를 우선 적용한다. 실제 review1 helper는 승인 이후 상태·현재 해시·복구 상태 확인 후 설계/기준만 반환한다(`hooks/task_documents.py:199`~220). 실행 결과 전체를 검증자에게 노출해 보호를 대신하지 않는다.
- minor: detail `:383` 관리 정본 선행 → `:388`의 공통 템플릿 직접 경로. 계획만 요청 시 구현하지 않음·자동 승인 조건·최소 확인·사용자 완료 확인·`:397`의 Layer 2 기본 생략이 유지된다.
- 집계: minor 4개/5개는 명시적 주기 확인에서 미도래/제안 가능을 구별한다. 마커 없음·잘못된 날짜·동일일 순서 모호·종류/완료 근거 없음·미완료 생성일은 집계 미확인이다. 사용자 전체 점검 요청은 횟수와 무관하다.
- 점검 완료: checkpoint 완료 기준 `:138`~148을 충족하고 결과/미해결 항목을 남긴 뒤 종료 `:182` → detail 실제 완료 기록. 제안·중단·미완료는 마커 미작성이다.
- 검사 실패 경로: 대상 heading 삭제/rename과 소비 참조 단절은 현행 fixture가 잡는다. 존재하는 다른 정본으로 향하는 표 오지정은 R1처럼 통과한다.

## 실행 증거·한계

- `python3 -m unittest discover -s tests`: 종료코드 0. 동일 discover 구성의 테스트 수는 246개다. 구조·TODO·plan_hash/task_documents·contract_reference·task_index_policy 및 배포 회귀를 포함한다.
- `git diff --check`: 종료코드 0. diff 본문은 읽지 않았다.
- 추가 반례: source를 메모리 dict로 읽어 R1의 두 문자열만 변경하고 공유 helper를 호출했다. 두 경우 모두 `[]`였다. 원본 파일 저장·실패 주입·원복은 수행하지 않았다.
- 정적 문서 연결·단위 테스트는 실제 모델의 규칙 준수, 호스트 hook 실행, 속도/토큰 개선을 입증하지 않는다. 사용자 완료 처리·Layer 2 수행·INDEX 편집을 실행하지 않았다.

## ⚠️ 주의 필요

별도 수정 항목 없음. 모델 행동·변경 전 크기 snapshot·과거 이력 대조 미실시는 위 한계로 남긴다.

## 📝 조용한 결정 목록

- exact_section/policy_text의 fenced 예시 제외와 메모리 fixture는 승인 설계에 있는 구현 결정이다. 추가 비가시적 위임은 발견하지 못했다.
- 동일일 마커 중복 금지·현재 major 최소 1개 근거 사용·done 전체 재분석 금지는 설계에 이미 있다. 새 집계 DB/hook·기준 상향은 발견하지 못했다.

## 🔍 에이전트 가정 검증

- 상세 정본 이동 뒤 선행 로드로 의미 보존: 정적 경로 기준 유효. 실제 모델 행동까지 증명하지 않는다. R1은 현재 Runtime 경로 자체보다 향후 단절 탐지의 공백이다.
- 기존 크기 기준 내 축소 가능: 유효. 현행 33,556바이트로 기준 미만이다. 원문 절차의 역사적 일대일 대조는 금지된 snapshot/changelog 없이 수행하지 않았다.
- 완료 시각이 모두 존재하지 않아 정확한 카운터를 전제할 수 없음: 유효. 근거 부족을 미확인으로 남기고 날짜/폴더 기반 추정을 금지한다.
- 실패비용 major 판단: 여러 정책 소비 경로와 검사기의 거짓 통과가 있는 작업이므로 모순되지 않는다. 등급을 바꿀 새로운 근거는 발견하지 못했다.
