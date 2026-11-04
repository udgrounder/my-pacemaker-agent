# 독립 구현 검증 — 1차

## 대상과 입력 격리

- 대상: `.mpa/runtime/`의 `core/agent_rules.md`, `core/agent_rules_detail.md`, `templates/shared_template.md`, `templates/architecture_history_template.md`, `personas/memory_curator.md`, `inject/layer0_init.md`, `layer0_update.md`, `layer1_implement.md`, `layer1_review.md`, `layer2_checkpoint.md`와 dist 대응 파일.
- 승인·요구사항·설계·검증 기준은 `python3 .mpa/runtime/hooks/task_documents.py inputs workspace/tasks/active/20261104_architecture_current_snapshot/plan.md --stage review1` 출력으로만 받았다. plan 전체·실행 TODO·changelog·기존 검증 결과·workspace/issues·workspace architecture_history 본문을 읽지 않았다.
- 현재 `workspace/memory/shared/architecture.md`와 Runtime의 reviewer·실행 격리·분석 방법 지침을 참고했다. `workspace/memory/shared/contracts.md`는 존재하지 않았다.
- Runtime 경로를 한정한 diff만 읽었다. 다른 동시 변경은 수정하지 않았다.

## 판정

수정 필요. P2 발견 1건이다. 현재/이력 분리 정책의 정상·실패 경로에서 별도의 구체적 의미 충돌은 발견하지 못했으나 기존 구조 로딩 회귀 검사가 실제 실패한다.

## 의미 있는 발견

### [P2] 항상 로드되는 core에 상세 정책을 추가해 기존 크기 회귀 검사를 실패시킴

- 위치: `/Users/kjkim/Study/my-pacemaker-agent/.mpa/runtime/core/agent_rules.md:88`–95, dist 대응 위치 동일.
- 재현: `python3 -m unittest tests.test_policy_consistency tests.test_structure_loading tests.test_contract_reference`
- 실제 출력: `Ran 33 tests`; `FAILED (failures=1)`; `test_core_is_smaller_than_the_recorded_pre_refactor_baseline`에서 `AssertionError: 35310 not less than 34731`.
- 근거: `/Users/kjkim/Study/my-pacemaker-agent/tests/test_structure_loading.py:9`의 baseline은 34,731 bytes이며 70–72행이 항상 로드되는 core의 크기를 검사한다. HEAD core는 33,202 bytes로 기준을 충족한다. 현재 core는 35,310 bytes이고 이번 아키텍처 분리 블록은 1,934 bytes다. 해당 블록만 제외한 현재 core는 33,376 bytes이므로 이번 추가가 기준 초과를 일으킨다.
- 영향: 요청한 기존 정책/계약 검증 통과 조건을 충족하지 못하며 항상 로드되는 정책을 작게 유지하는 기존 회귀 기준을 깨뜨린다. 전체 검사 성공을 전제로 하는 후속 release preflight도 이 실패가 남으면 통과할 수 없다.
- 수정 권장: core에는 현재/이력 정본 구분과 즉시 로드할 트리거·정본 링크를 유지하고, 이관·보존·선택적 읽기 등의 상세 절차를 on-demand detail로 이동하는 등 기존 크기 기준 안에 맞춘다. 이동 시 초기화·구현·검증·memory curator·점검 참조와 source/dist를 함께 맞추고 기존 검사를 다시 실행한다. 의미 있는 규칙을 누락하거나 baseline 숫자만 높여 실패를 숨기지 않는다.

## 검증 방법과 실제 결과

1. 대상 파일 10쌍 byte 대조: `source-dist files: 10`, `mismatches: []`.
2. 위 unittest 실행: 33개 중 32개 통과, 위 크기 검사 1개 실패. 전체 Runtime 파일 집합과 byte parity를 검사하는 `test_source_and_distribution_runtime_files_are_identical`도 이 실행에서 통과했다.
3. `python3 .mpa/runtime/hooks/contract_reference.py --runtime-root .mpa/runtime`: `{"code": 0, "runtime_root": ".mpa/runtime", "contract_version": 1, "profile": "mpa-toml-v1", "references": 3}`.
4. dist validator 대응 실행: `{"code": 0, "runtime_root": "dist/.mpa/runtime", "contract_version": 1, "profile": "mpa-toml-v1", "references": 3}`.
5. `git diff --check -- .mpa/runtime dist/.mpa/runtime`: 종료 코드 0, 출력 없음.
6. 현재 architecture 3행에 같은 폴더 상대 링크가 있으며 연결 대상 파일 존재를 확인했다. history 본문은 읽지 않았다.

## 정상·실패 경로 추적

- 정상 — 신규 초기화: `layer0_init.md:123` → shared template 작성 안내 → core 분리 규칙을 따른다. 현재 설계는 주제별로 작성하고 제목 아래 상대 링크를 둔다. history가 없을 때만 별도 template으로 연결 대상을 만들고 기존 파일은 유지한다. template은 빈 이력을 허용하고 실제 변경 또는 이관이 있을 때만 항목을 추가하도록 한다.
- 정상 — 기존 설계 대체: 구현 종료의 `layer1_implement.md:140`–142와 검증 종료의 `layer1_review.md:316`–317 → core의 먼저 저장·대조 규칙 → 현재 주제 교체로 이어진다. 기존 문서의 타임라인도 원문 보존 확인 뒤 분리하며, 유효한 결정 이유·제약·미해결 위험은 현재 문서에 남는다.
- 실패 — history 저장 실패: core 92행은 이전 판단 삭제를 금지한다. 구현·검증의 교체 절차가 같은 정본을 참조하므로 저장 실패를 현재 문서의 파괴적 교체로 진행하도록 지시하는 경로는 발견하지 못했다. 이는 지침의 논리 추적이며 실제 LLM의 파일 저장 실패 대응을 실행해 보장한 것은 아니다.
- 실패 — 크기 정리 시 history 손실 위험: memory curator 40–41행은 history를 80줄 삭제·교체 기준에서 제외한다. architecture의 오래된 규칙 삭제에는 51행의 이력 보존 확인이 적용되고 유효한 위험은 유지한다. 기존 history를 일괄 정리하거나 덮어쓰도록 하는 충돌은 발견하지 못했다.
- 선택적 로드·갱신: core 95행과 Phase 2 입력표는 기본 입력을 architecture로 유지한다. history를 필수 메모리 INDEX 항목으로 등록하지 않으며 memory index template의 shared 제외와 일치한다. layer0_update는 Runtime 업데이트만으로 프로젝트 문서를 일괄 재작성하지 않고, layer2_checkpoint는 갱신 대상에 혼재한 이력을 보존 후 정리하도록 한다.

## 미확인 한계

- 이력 본문과 과거 architecture 원문의 일치·전량 보존은 1차 격리상 확인하지 않았다. 2차에서 별도 대조가 필요하다.
- `contracts.md`가 없어 해당 프로젝트 계약 문서와의 직접 대조는 불가능했다. Runtime inspect-only 계약 validator는 양쪽 모두 통과했다.
- 지침 추가는 실제 LLM 준수나 저장 원자성을 보장하지 않는다. 이 검토는 문구의 연결과 정상/실패 절차를 정적으로 추적했고 실제 memory는 수정하지 않았다.
- 위 3개 기존 unittest 모듈을 실행했으며 전체 테스트 모음·배포·설치는 실행하지 않았다.

정정 회고: 없음.
