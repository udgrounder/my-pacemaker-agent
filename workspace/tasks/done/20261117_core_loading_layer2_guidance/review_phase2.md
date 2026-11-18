# 2차 독립 구현 검증

## 대상·입력·판정

- 구현 대화 미상속으로 task_documents.md·_agent_execution_priority.md·layer1_review.md·code_reviewer 및 반례/경로 추적 기준을 확인했다. task_documents.py inputs plan.md --stage review2 출력과 review_phase1.md·changelog.md를 실제 파일에 대조했다. 전체 git diff는 읽지 않았다.
- 대상은 source/dist의 core/agent_rules.md·agent_rules_detail.md·session_protocol.md, inject/layer1_design.md·layer1_implement.md·layer1_review.md·layer1_discovery.md·layer2_checkpoint.md, plan_template.md·plan_minimal_template.md·changelog_template.md, tests/test_structure_loading.py·test_todo_policy.py, docs/mpa-internal-structure.md·guidebook/guidebook.md·architecture.md·architecture_history.md다. runtime_before.json은 이동 원문 대조에 사용했다.
- 판정: **1차 R1/R2 해소, 추가 즉시 수정 결함 없음. 사용자 테스트 진행 가능.** INDEX 전후 원문 보존의 증거 한계는 유지한다. 구현자 설명만으로 1차 판정을 번복하지 않았다.

## 1차 발견의 실제 재검증

### R1 — 해소

- loading_route_issues는 실제 트리거 표를 파싱하고 계획 생성·편집, 검증 입력 준비, 재개, Layer 2 표시, 기존 이어가기 요청 각각의 필수 조건과 정확한 detail 파일/heading 대응을 검사한다. 일반 대상 heading 존재 검사도 유지된다.
- 실제 source 문서를 메모리 dict로 읽고 Layer 2 표의 대상을 존재하는 “계획서와 변경 이력 관리”로 바꿨다. 현재 반환은 wrong trigger target: Layer 2 현황 표시 시점: core/agent_rules_detail.md: Layer 2 현황 표시다.
- 원문에서 검증 입력 준비 전· 및 ·재개 시를 각각 제거하면 해당 조건의 missing trigger condition을 반환한다. 1차에서 통과한 세 반례가 현재 검출된다.
- test_detects_valid_but_wrong_trigger_heading 및 test_detects_missing_management_load_events가 동일 helper를 사용한다. 기존 삭제/rename·잘못된 파일·소비 경로 단절·fenced 예시 위장 fixture도 유지된다. 메모리 fixture 실행 전후 source Runtime 전체 checksum 동일을 확인했다. 원본 Runtime에 실패 주입·원복을 하지 않았다.

### R2 — 해소

- guidebook.md:1353은 규칙 변경 영향이 있으면 필요성을 검토해 제안하고 사용자 명시 요청에 따라 실행하며 자동 실행하지 않는다고 한다.
- 같은 문서 :935~938과 Runtime detail의 “Layer 2 현황 표시”가 안내·사용자 요청·실제 점검을 구별한다. 1차의 즉시 실행 잔존 문구는 현재 없다.

## C1~C7 및 구현 주장 대조

| 기준 | 실제 근거·판정 |
|---|---|
| C1 | snapshot core_before 36,783바이트, 현 source/dist core 33,556바이트. 3,227바이트 감소, 기존 CORE_BASELINE_BYTES=34,731 대비 1,175바이트 여유. 기준 상향 없음. |
| C2 | snapshot moved_management 3,625바이트의 비어 있지 않은 각 문단은 core_before에 있고 합본 전체는 현 detail에 정확히 포함된다. 원래 두 위치의 합본이므로 옛 core에 연속 포함된다고 주장하지 않는다. core 요약·필수 선행 로드와 단계/템플릿/재개 연결을 확인했다. 옛 detail의 verbatim 변경 문단은 완료 후속·재개 두 곳이며 새 정본 연결로 대응한다. 나머지 원문 문단과 기존 heading은 보존된다. |
| C3 | detail의 실제 “Layer 2 현황 표시”에 core 표·major 완료 후속·checkpoint 종료에서 도달한다. 설치 Runtime만으로 찾으며 프로젝트 memory에 의존하지 않는다. |
| C4 | 마지막 유효 점검 이후 major 1개/minor만 5개, minor 기본 생략, 명시 요청 우선, 자동 실행 금지가 있다. 마커 없음·날짜 오류·종류/완료 근거 누락·동일일 순서 모호는 집계 미확인이다. 생성일/폴더명 대체와 done 전수 재분석을 금지한다. |
| C5 | checkpoint 완료 기준과 결과/미해결 항목 기록 뒤에만 기존 마커를 기록한다. 제안·중단·미완료에는 쓰지 않는다. 다른 행/과거 마커 보존·동일일 중복 금지·저장 실패 노출이 있다. 현 INDEX는 실제 active/hold 6개 폴더와 대응하고 done 행이 없다. 과거 마커 10개와 직전 점검 신규 1개를 확인했다. 구현 시작 원문 증거 한계는 아래 주의에 명시한다. |
| C6 | 실제 source/dist와 메모리 fixture는 같은 helper를 사용한다. 새 두 테스트로 1차 공백 해소. 전체 248개 테스트 종료코드 0이며 parity·기존 승인/복구·minor 직접 경로·계약 앵커·TODO 검사를 포함한다. source/dist 전체 파일 목록/내용 동일 검사 통과. |
| C7 | docs 내부 구조·guidebook·architecture의 현재 정본은 detail과 일치한다. architecture_history에 이전 계획/이력·주기 설명과 사용자 승인 근거가 보존되고 현재 문서는 새 배치를 가리킨다. 1차 실패 증거 및 최초 246개 통과와 추가 반례/보완을 구별한다. |

- 실행 계획 1~4의 배치·연결·검사 결과는 실제 산출물과 대응한다. 5의 독립 1차 결과와 별도 2차 산출물은 이 문서로 연결한다. 과거 도구 실행 순서와 snapshot 채집 시점 자체는 파일만으로 재구성하지 않는다.
- 승인해시 reqspec-v1:2b9391f0a3bc3b21은 현재 check와 일치한다. review2 입력 생성 성공, 태스크 .plan-renewal.json 없음. 1차 보완은 승인 범위의 연결 검출·문구 정합성 보완이며 명세/승인 완화가 아니다. 사용자 완료 확인은 미완료이고 작업은 active다.

## 정상·실패·경계 경로

- 정상 major 완료: 완료 인정/사용자 확인 → 목적지 충돌 검사 → 상태/INDEX 정리·done 이동 → detail 안내 정본. 마커 뒤 현재 major 완료가 입증되면 최소 1개 근거로 제안하며 자동 점검·마커 기록으로 건너뛰지 않는다.
- 편집/재개/검증 입력 준비는 관리 정본을 먼저 읽는다. 갱신 담당자 한 명, .plan-renewal.json 잔존 시 다른 편집 중단·복구 우선, 확보 파일/JSON·실패 증거 보존, 현재 미확인/실패 노출 규칙이 이동 전 원문과 함께 유지된다. review1 입력 격리와 review2 이력 대조는 별개다.
- minor는 detail 직접 템플릿 경로·계획만 요청 시 구현 금지·자동 승인 조건·최소 확인·완료 확인·Layer 2 기본 생략을 유지한다.
- 명시적 주기 확인의 minor 4개/5개는 미도래/제안 가능을 구별한다. 근거 없는 같은 날 완료·오래된 미완료 생성일은 횟수로 추정하지 않는다. 사용자 전체 점검 요청은 횟수와 무관하다.
- 실제 점검은 checkpoint 9개 완료 기준과 결과 기록 뒤 종료 경로에서 마커 처리한다. 미해결 개선 이슈와 점검 미완료를 구별하고 제안·중단은 기록하지 않는다.

## 현재 실행 증거

- python3 -m unittest discover -s tests: 종료코드 0. 현재 suite 248개를 별도 count로 확인했다. 구조 14개와 TODO/승인·복구/task_documents/contract_reference/task_index_policy 등 포함.
- plan_hash.py check: 현행 승인해시 일치. git diff --check: 종료코드 0, diff 본문 미열람.
- 1차 반례 세 가지의 현재 검출과 fixture 전후 Runtime checksum 일치를 직접 확인했다.
- snapshot은 저장된 비교 원문으로 사용했으며 최초 편집 전 캡처라는 설명의 시점 자체를 독립 증명하지 않았다.

## ⚠️ 주의 필요

1. **INDEX 전후 원문 보존 증거 한계.** 구현 시작 원문/checksum snapshot이 별도로 없다는 메인 답변을 받았다. 현 6개 active/hold 폴더와 행·정렬, HEAD 과거 마커 10개 보존 및 2026-11-17 한 줄을 직접 확인했다. 직전 점검 보고서의 5개 복구·과거 10마커 보존·신규 완료일 기록 및 현재 계획 등록과 대응한다. 이 관측과 “이번 구현에서 편집하지 않음” 설명으로 전후 모든 행 본문의 동일성을 독립 증명하지 않는다. 손상 증거는 발견하지 못했으며 기존 사용자 변경을 되돌리지 않는다.

## 조용한 결정·가정·미확인

- 추가 비가시적 조용한 결정 0개. 정확한 heading 검사·fenced 예시 제외·메모리 fixture·동일일 중복 금지·최소 major 근거 활용은 승인 설계 안에 있다.
- 틀린 계획 가정 0개. 이동/선행 로드 의미 보존은 정적 경로·원문 대조에서 유효하고 크기 축소는 수치로 충족한다. 완료 시각이 보장되지 않는다는 가정은 불확실성 경계와 일치한다.
- 실제 모델 준수·호스트 hook 실행·사용자 완료 처리·Layer 2 수행/마커 편집·토큰/속도 개선·설치 프로젝트 배포는 미관찰이다. 문서/정적 검사 통과로 해당 행동을 입증하지 않는다. 사용자 확인 전 완료 처리하지 않는다.
