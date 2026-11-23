# 2026-10-19 독립 1차 재검증

## 범위와 입력 격리

- 구현 대화·기존 검증 결과를 상속하지 않은 독립 담당이 수행했다.
- 최초 기준은 `python3 .mpa/runtime/hooks/task_documents.py inputs workspace/tasks/active/20261014_task_role_documents/plan.md --stage review1` 출력이다. plan/implementation 원본 전체·진행 기록·changelog·기존 리뷰는 읽지 않았다.
- `.mpa/runtime/hooks/task_documents.py`, plan_hash/code_gate/session_start, Runtime 지침·템플릿 및 `tests/test_task_documents.py`를 확인했다. diff는 `.mpa/runtime`로 한정했다. legacy 계약의 기존 fixture 확인에 `tests/test_plan_hash.py`의 관련 부분만 추가 참조했다.
- 소스는 수정하지 않았다. 추가 재현은 `unittest.mock`의 메모리상 읽기 fixture이며 파일 내용 변경은 이 보고서만이다. 전체 테스트는 메인에서 실행하므로 반복하지 않았다.

## 발견 사항

### [P2] 구형 단일 plan의 비평 입력이 요구사항을 누락한다

- 위치: `.mpa/runtime/hooks/task_documents.py:213-221`, `253-257`.
- 계약: `inject/task_documents.md:16,18,73`은 표식 없는 기존 단일 plan/구형 해시를 그대로 읽고 자동 전환하지 않는다고 명시한다. `layer1_critique.md:5`는 비평 입력을 helper의 `inputs --stage critique`로 전달하도록 한다.
- 실제: base는 `## 요구사항 명세`·선택 문서·설계 기준·검증 기준이라는 최신 제목만 추출한다. legacy fallback도 `## 실행 계획` 또는 `## 실행 계획 (Implementation Plan)`만 지원한다. 기존 `## 목적`, `## 핵심 기능`, `## 구현 계획` 등은 전달하지 않는다.
- 재현: `tests/test_plan_hash.py:624-632`의 `test_audit_allows_matching_legacy_hash_before_approval`가 사용하는 정상 구형 구조를 그대로 사용했다. `상태: 설계 완료`, 실제 `plan_hash.compute(body)`로 구한 일치 해시, 본문 `## 목적\n초기 목적 LEGACY_PURPOSE_CANARY\n## 구현 계획\n- [ ] 구현 LEGACY_PLAN_CANARY`를 Path.read_text mock으로 제공해 `docs.inputs(path, 'critique')`를 호출했다.
- 관측 출력: `[{'source': 'plan.md', 'content': '---\n상태: 설계 완료\n승인해시: 468cfc17030e1c16\n---'}]`. 목적과 구현 계획 canary가 모두 False였다. 성공 형태로 반환하지만 독립 비평자가 무엇을 만족해야 하는지 읽을 수 없다.
- 영향: 지원한다고 안내한 기존 형식에서 독립 비평 입력의 충분성을 충족하지 않는다. 기존 원문을 보존하는 경로에서 호출자가 원본을 다시 발췌해야 한다.
- 권고: 구형 plan의 실제 요구사항·설계 섹션을 보존하는 별도 legacy 입력 경로를 제공하고, 기존 구형 제목 fixture에서 목적·기준이 비평 입력에 남는지 검증한다. 구형 승인해시의 실행 허용 정책을 변경하라는 권고는 아니다.

## 확인 근거와 통과 범위

- **정상 템플릿 직접 확인:** 배포 원본 `templates/plan_minimal_template.md`와 `templates/implementation_template.md`를 읽어 메모리 fixture를 구성했다. implementation의 원래 설계 기준·실행 계획·진행 기록 칸에 각각 식별 문구를 넣고 유효한 reqspec-v1 및 문서 basis checksum을 연결했다. 실제 helper 반환에서 review1은 `설계=True / 실행=False / 진행=False`, implement는 `설계=True / 실행=True / 진행=False`였다. 이 정상 분리형의 선언과 실제 입력은 일치했다.
- **plan 단독 UI:** 최소형의 `## 설계 기준` 하위 화면 기준에 둔 UI 제약과 HTML 원본/버전 연결이 review1 입력에 유지됐다. 별도 `## 화면 기준` 제목의 지원은 계약이 고정하지 않아 발견 사항으로 올리지 않았다.
- **최소 plan과 선택 문서:** 최소 템플릿은 roles-v1이며 추가 문서를 강제하지 않는다. inspect는 명시 등록만 선택하고 미등록 존재 파일을 자동 포함하지 않는다. 등록된 문서의 누락·기준 checksum·명세 연결을 검사한다.
- **승인/연결:** 승인 전 구성 검사와 승인 후 기준 연결 검사가 분리되어 있다. approve는 기존 plan 단독 저장을 유지하고 문서 metadata는 후속 갱신이다. gate/session의 문서 연결 경고는 재승인 대신 연결 보완을 지시한다.
- **독립 검증:** review1은 구현 설계 기준만 추출하고 review2는 plan 실행 기록 및 changelog를 포함한다. 1차 결과는 호출자가 명시 추가한다는 계약이다. fence 상태를 추적해 코드 블록 제목을 경계로 오인하지 않도록 한다.
- **큰 작업/조사:** 상위 plan 등록, 작업 내부 상대 경로, research/work 역할, 선택적 하위 폴더를 정의한다. 외부·상위 경로와 symlink 자동 추적을 막고, 폴더 분리로 모델 상한·병렬 수정 권한을 확대하지 않는다.
- **HTML 요청:** `inject/task_documents.md:48-52` 및 ui_design 템플릿은 요청 시 HTML 작성, 기존 원본/상태/상호작용 연결, 실제 렌더링 확인, 사용자에게 열기, 클릭 가능한 최종 파일 링크, 도구 부재 시 렌더링 미확인 고지를 포함한다. HTML은 Markdown 역할 문서로 등록하지 않는다.

## 한계·미확인

- 이 검증은 읽기 검토와 메모리 fixture 재현이다. 전체 테스트는 반복하지 않았으며 메인의 실행 결과와 대조해야 한다.
- 실제 설치 호스트의 hook 자동 실행·브라우저 렌더링/열기·UI HTML 제작 수행은 이번 읽기 검증에서 실행하지 않았다. 절차 문서 존재를 실제 호스트 수행 성공으로 판정하지 않는다.
- legacy 실행 입력의 reqspec-v1 요구에 따른 거부는 기존 `test_audit_rejects_legacy_hash_in_post_approval_status`의 승인 정책이므로 신규 회귀로 보고하지 않았다. 발견 사항은 승인 전에도 허용되는 critique 입력의 내용 유실에 한정한다.
- 기준 섹션 자체에 실행 결과를 잘못 기록한 경우의 주장 유입은 정상 문서 계약을 벗어나므로 별도 발견 사항으로 올리지 않았다.

정정 회고: 없음.
