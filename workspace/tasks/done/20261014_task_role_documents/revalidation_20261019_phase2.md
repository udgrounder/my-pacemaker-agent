# 2026-10-19 독립 2차 재검증

## 판정

즉시 수정 필요 1건(P2), 별도 주의 사항 0건. 1차의 구형 단일 plan 비평 입력 유실을 현재 소스에서 독립 재현했다. 검증 요청 범위에 따라 소스·승인해시·상태는 변경하지 않았다.

## 재현과 정책 구분

- `.mpa/runtime/hooks/task_documents.py:213-221,253-257`은 새 요구사항 제목과 `실행 계획` 두 종류만 추출한다. reqspec 도입 이전의 `## 목적`, `## 핵심 기능`, `## 구현 계획`은 추출하지 않는다.
- `tests/test_plan_hash.py:624-632`가 승인 전 정상 구형 형식으로 인정하는 목적/구현 계획 구조에 핵심 기능을 추가하고 세 섹션에 canary를 넣었다. `Path.read_text`와 승인 확인용 `open`만 메모리에서 대체했으며 실제 파일은 바꾸지 않았다.
- `상태: 설계 중`(해시 없음)과 `상태: 설계 완료`(일치 legacy 해시 `7249e0480bcc1cbd`) 모두 `approval_hash_issue=None`이다. `inputs(...,'critique')`는 오류 없이 프론트매터만 반환했고 목적·핵심 기능·구현 계획 canary 세 개가 모두 누락됐다. `inspect(before_approval=True)`도 `layout=single-v1, documents=[], issues=[]`이다.
- 같은 본문을 `상태: 검증 중`으로 주면 implement 입력은 reqspec-v1 해시 형식 오류로 거부된다. 이는 기존 `test_audit_rejects_legacy_hash_in_post_approval_status`와 일치하는 승인 정책이며 이번 결함이 아니다. 비평은 미승인 입력을 허용하므로 승인 후 거부 정책으로 비평 입력 유실을 설명할 수 없다.
- `inject/task_documents.md:16,18,73`과 implementation.md:79,103은 기존 단일형·구형 원문 유지 및 자동 전환 금지를 약속한다. 이 fixture는 명시 지원한 기존 형식 범위다. 권고는 구형 비평 입력 보존과 해당 fixture 회귀 검사이며 승인 정책 완화가 아니다.

## 이전 주장과 현재 증거 대조

- plan.md:109의 남은 즉시 수정 없음, implementation 실행 계획의 기존 단일형 인계 검증 완료, changelog.md:44의 기존 설계 기준 누락 보완 및 네 건 재검증 성공은 이 구형 제목 입력까지 포괄하는 근거로 사용할 수 없다.
- `test_legacy_design_criteria_retained_without_execution_claims`는 reqspec 기반 plan에 `실행 계획 (Implementation Plan)`을 추가한 review1 사례다. 구형 목적/핵심 기능/구현 계획의 critique 입력은 검사하지 않아 기존 통과와 현재 실패가 양립한다.
- 부모가 직접 실행한 전체 236개 테스트(4.669초) 통과·승인 명세 일치·inspect issues=[]·source/dist 동치·diff 검사 통과는 전달받은 증거이며 전체 테스트를 반복하지 않았다. 이 결과로 위 미검사 입력의 충족을 판단하지 않는다.
- HTML 변경은 요청 시 파일 작성·연결·렌더링 확인·사용자에게 열기·링크 제공 지침의 추가다. changelog.md:38은 실제 HTML 생성·렌더링/열기를 수행하지 않았다고 명시하므로 그 한계를 유지한다.

결론: 구형 plan 비평 입력 호환성 P2 한 건이 남아 있으므로 전 범위 통과/남은 수정 없음으로 보고할 수 없다. 실제 호스트 hook 및 HTML 실행은 이번 검증 증거에 포함되지 않는다.

정정 회고: 없음.
