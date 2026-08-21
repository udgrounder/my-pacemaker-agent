# Issue Intake Profile

## Trigger

사용자가 지정 프로젝트의 특정 issue 수집을 요청하거나, 승인된 Runtime update가 dry-run에서 수집 후보를 고지한 뒤 issue batch를 처리할 때.

## Input

project root, safe project-ref, issue filename, 수집 목적.

## Allowed Actions

지정 issue 또는 고지·승인된 update batch만 inbox에 임시 파일을 통해 안전하게 생성하고 archive 유사 filename 후보를 기록한다. 목적지 파일 존재를 확인한 뒤에만 원본을 삭제한다. 수집 뒤 검토 내용은 사용자에게 먼저 제시한다.

## Checks

민감정보·절대 경로·중복·archive 충돌과 유사 이력을 확인한다.

## Gates

명시 요청 또는 update 고지·승인 없이 issue를 이동하지 않는다. 사용자가 채택·기각을 결정하기 전에는 archive하지 않는다.

## Output

inbox issue와 이동 결과 고지. 수집은 목적지 파일 존재 확인 뒤 원본을 삭제하고 원본 부재를 확인한다. 사용자의 기각은 판단 근거를 이슈 파일에 기록한 뒤 즉시 archive하고, 채택은 새 작업 항목 plan.md를 만든 뒤 그 경로를 이슈에 기록하고 즉시 archive한다.

## Failure State

이동 확인 실패 시 원본을 유지·복원하고 차단 이유를 보고한다. 원본이 이동 뒤 새로 생겼다면 두 파일을 보존하고 수동 조정을 요청한다.

## Prohibited

copy 후 delete, 목적지 덮어쓰기, 고지 없는 자동 수집을 하지 않는다. update 수집은 검증 성공 뒤 목적지 존재·원본 부재를 확인한 경우에만 원본 정리를 완료로 처리한다.
