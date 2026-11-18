# 역할 문서 설계에서 화면 디자인 입력 누락 방지

**타입**: 방법론 개선
**발견 상황**: 역할 문서 도입 계획의 design.md를 기술 설계로 정의하면서 화면 설계 입력은 빠뜨렸고 사용자가 이를 지적했다.
**적용 범위**: 모든 프로젝트

## 현재 방식

기술 설계 문서만으로 화면 구성·상호작용·상태·디자인 원본을 전달하면 화면 설계 담당과 구현/검증 담당의 입력 경계가 불명확하다.

## 개선 방안

화면 설계가 필요한 경우만 ui_design.md를 추가하고 design.md와 책임을 구분한다. 실제 디자인 원본을 연결하고 역할별 구현·시각 검증 입력으로 사용한다. 설계 당시 task_role_documents 계획에 반영했고 Runtime은 미구현 상태였다. 현재 구현 상태는 아래 정합성 점검 기록을 따른다.

## 적용 대상 파일

- workspace/tasks/active/20261014_task_role_documents/plan.md
- .mpa/runtime/templates/ui_design_template.md (계획상 신규)
- .mpa/runtime/inject/layer1_design.md
- .mpa/runtime/inject/layer1_review.md

## 현재 상태 확인 — 2026-11-17
현재 Runtime에 templates/ui_design_template.md가 존재하며 inject/task_documents.md에 선택적 UI 기준·HTML 미리보기·역할별 입력 연결이 구현되어 있다. 연결 작업은 독립 검증 후 테스트 중이며 사용자 결과 확인을 기다린다. 실제 호스트의 HTML 생성·렌더링까지 검증됐다고 주장하지 않는다. 위 미구현 설명은 발견 당시 이력이며 이 상태 보완으로 채택·archive·작업 완료를 자동 처리하지 않는다.
