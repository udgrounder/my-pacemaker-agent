# 독립 구현 검증 — 2차

## 대상·방법

- review_phase1.md를 먼저 읽고, changelog.md 및 `python3 .mpa/runtime/hooks/task_documents.py inputs workspace/tasks/active/20261104_architecture_current_snapshot/plan.md --stage review2`의 계획·진행 주장을 실제 파일과 대조했다. 구현 대화는 전달받지 않았다.
- Runtime 대상 10개: core/agent_rules.md, core/agent_rules_detail.md, templates/shared_template.md, templates/architecture_history_template.md, personas/memory_curator.md, inject/layer0_init.md, layer0_update.md, layer1_implement.md, layer1_review.md, layer2_checkpoint.md 및 dist 대응 파일. 해당 diff와 현재 본문·지침 연결을 확인했다.
- workspace/memory/shared/architecture.md와 architecture_history.md도 검토했다. `git show HEAD:workspace/memory/shared/architecture.md`를 원본으로 사용했으며 과거 Git 이력을 재구성하지 않았다. 독립 실행 정본·reviewer 및 반례 탐색/경로 추적 지침도 읽었다.
- 제품·계획·이력은 수정하지 않았다. 이 검토 결과 파일 두 개만 저장한다.

## 판정

수정 필요. 1차 P2 1건을 실제 실행과 변경 전 파일로 재확인하여 유지한다. 추가 독립 finding은 0건이다. 변경 목적 자체를 무효화하는 문서 유실·현재 계약 변경·이력 로드 강제는 확인하지 못했다.

## 유지한 finding

### [P2] 항상 로드되는 core 크기 기준 회귀

- 위치: `/Users/kjkim/Study/my-pacemaker-agent/.mpa/runtime/core/agent_rules.md:88`–95 및 같은 내용의 `/Users/kjkim/Study/my-pacemaker-agent/dist/.mpa/runtime/core/agent_rules.md:88`–95.
- 시나리오: 기존 구조 로딩 검사를 포함해 정책 검증을 수행하거나 전체 단위 테스트를 요구하는 release preflight로 진행한다.
- 실제 재현: `python3 -m unittest tests.test_task_index_policy tests.test_contract_reference tests.test_structure_loading tests.test_policy_consistency` → 35개 중 34개 통과, `test_core_is_smaller_than_the_recorded_pre_refactor_baseline` 실패. 출력은 `AssertionError: 35310 not less than 34731`이다.
- 변경 전 대조: `git show HEAD:.mpa/runtime/core/agent_rules.md`는 33,202 bytes로 `/Users/kjkim/Study/my-pacemaker-agent/tests/test_structure_loading.py:9`의 34,731-byte 기준 안이다. 현재 파일은 35,310 bytes다. 테스트 70–72행은 현재 core 크기를 직접 검사한다. 1차의 33개 실행과 이번 35개 실행은 포함 모듈 차이이며 동일 실패다.
- 영향: 기존 로딩 회귀 기준이 깨졌다. plan의 기존 정책 검증·source 검증 완료 판단에는 이 미충족 증거가 반영돼야 한다. 이 결과는 changelog의 구현 설명으로 재평가하지 않는다.
- 권장: core에 정본 구분과 필요한 로드 트리거·링크를 남기고 상세 이관/보존 절차를 on-demand detail로 이동하는 등 기존 기준 안에 맞춘 뒤 관련 참조·source/dist를 확인하고 같은 검사를 재실행한다. baseline 숫자만 높이는 방식은 근거가 되지 않는다.

## 명세·구현 주장 대조

| 주장/기준 | 실제 확인 결과 |
|---|---|
| changelog 14행 및 plan 66행: 이동 원문·링크 보존 | HEAD 원문과 현재/이력 diff를 대조했다. 이전 관리 원칙 전체, 선택형 작업 문서 계약 전체, 구성 층위 모델 설계 출처가 history에 보존돼 있다. 인용의 `> `와 줄 끝 공백만 제거한 문자열 비교에서도 각 블록 일치. |
| 현재 설계·호환 조건 보존 | 선택형 계약은 현재 architecture 74–76행에 원문 그대로 통합됐다. plan 내부 표/legacy 해시 지원, reqspec 승인 형식·renew-spec·복구 JSON 및 독립 1차/2차 분리는 70–72, 123행에 유지된다. 바뀐 과거 형식 설명의 앞부분도 history에 보존됐고 나머지 내용은 현재 문서에 그대로 남는다. |
| 상단 상대 링크와 현재/이력 분리 | architecture 3행 링크의 같은 폴더 연결 대상이 존재한다. 본문은 주제별 현재 구조이며 날짜별 타임라인이 아니다. history는 2026-11-04 이관일·기존 원문·앞으로의 기록 방법으로 분리됐다. 기본 설계 읽기를 history로 바꾸지 않았다. 기존 문서가 주제별이라는 plan 가정은 실제 HEAD에서 유효하다. |
| changelog 15행: Runtime 공통 지침·템플릿 연결 | 대상 파일들의 아키텍처 분리 변경이 존재한다. detail 기록 위치, 구현/검증 종료, 초기화/갱신/점검, memory curator, shared 안내와 history template이 core 정본을 참조한다. history는 curator의 80줄 삭제·교체 기준에서 제외된다. |
| changelog 16행/plan 68행: 기존 테스트 15개 통과 | task_index_policy 2개와 contract_reference 13개는 이번 35개 실행에서도 통과했다. 따라서 이 제한된 수치 주장은 사실이다. 하지만 구조 로딩 회귀 검사까지 통과했다는 뜻은 아니며, 위 실패 때문에 포괄적인 검증 완료 판정은 성립하지 않는다. 같은 원인인 만큼 별도 finding으로 중복 계산하지 않는다. |
| source/dist 68개 내용 일치 | 생성된 __pycache__/pyc를 제외한 source Runtime 파일 68개를 대응 dist 파일과 byte 비교: mismatches `[]`. 대상 10개도 이 비교에 포함된다. 실제 sync-runtime 실행 이력 자체는 현재 parity만으로 증명하지 않는다. |
| check/audit 정상·복구 자료 없음 | check 종료 0, `일치: reqspec-v1:90f62e2b88612422`; audit 종료 0, frontmatter_exists true / missing [] / invalid []. 해당 작업 폴더 `.plan-renewal*` 없음. |
| 명세 변경·이력 연결 | changelog 23행의 이전 `reqspec-v1:102fd096f7eddfcc` → 현재 `reqspec-v1:90f62e2b88612422` 연결과 범위 확장 사유/명세 영향/승인 근거가 기록돼 있다. 현재 plan hash는 새 기록과 일치한다. 원래 사용자 발화의 승인 의미는 전달된 기록 밖에서 독립 증명할 수 없으므로 해시 검사를 사용자 권한 증명으로 확대하지 않는다. |
| diff 형식 정상 | 대상 Runtime·dist·architecture·history·plan·changelog의 `git diff --check` 종료 0, 출력 없음. |

## 정상·실패 경로 및 추가 탐색

- 정상 신규 작성: layer0_init → shared template 안내 → 제목 아래 링크 및 없는 history만 template으로 생성 → 현재 설계를 주제별 작성. 기존 history 덮어쓰기 지시는 없다.
- 정상 설계 교체: detail/구현 종료/검증 종료/curator → core 92–94행 → 변경 이력 저장·대조 후 현재 주제 교체. 현재 유효한 이유·제약·위험은 현재 문서에 남긴다.
- 실패 저장: core 92행에서 history 저장 실패 시 이전 판단 삭제 금지. curator의 일반 크기 정리에도 architecture별 이력 보존 규칙과 history 제외가 연결되므로 이력을 크기 제한 때문에 지우라는 추가 지시는 발견하지 못했다.
- 기존 이력이 없는 프로젝트, 기존 history가 있는 프로젝트, architecture와 history의 역할 혼동, 유효한 제약의 이력 이관을 반례로 추적했다. 해당 문구에서 별도의 구체적 회귀는 확인하지 못했다.
- Runtime diff에는 이번 관심사 외 완료 목적지 충돌·코드 탐색·후속 질문 처리 변경도 보인다. 공유 작업 공간의 다른 변경을 이번 구현자가 만든 조용한 결정으로 추정하지 않았고, 그 변경 전체를 본 작업의 성과로 인정하지도 않았다. 이번 아키텍처 변경에 귀속할 수 있는 미기록 조용한 결정은 0건이다.

## 1차 누락·가정 판정과 한계

- 1차가 격리 때문에 읽지 않은 history 본문·HEAD 원문 보존·승인 check/audit 및 실행 주장을 이번에 보강했다. 원문 보존·현재 계약 유지에 관한 가정 오류는 추가로 발견하지 못했다.
- 1차 P2를 해소하는 객관적 반증은 없다. 검증 완료 주장과 실패 증거의 차이를 위와 같이 명시했다.
- 현재 파일은 보존 결과를 보여주지만 실제 저장 시간 순서·LLM 준수·원자성을 증명하지 않는다. 승인 이력의 이전 hash가 실제 과거 어느 본문에서 생성됐는지까지 Git 전체 이력으로 재구성하지 않았다.
- 관련 4개 unittest 모듈을 실행했다. 전체 테스트 모음·release·deploy·설치·파일 저장 실패 주입은 실행하지 않았다. 정적 지침 연결 검토와 실행 검사를 구분한다.

정정 회고: 없음.
