# Issue Intake Profile

## Trigger

사용자가 지정 프로젝트의 특정 issue 수집을 요청하거나, 승인된 Runtime update가 dry-run에서 수집 후보를 고지한 뒤 issue batch를 처리할 때.

## Input

project root, safe project-ref, issue filename, 수집 목적.

## Allowed Actions

지정 issue 또는 고지·승인된 update batch만 inbox로 원자 이동하고 archive 유사 filename 후보를 기록한다.

## Checks

민감정보·절대 경로·중복·archive 충돌과 유사 이력을 확인한다.

## Gates

명시 요청 또는 update 고지·승인 없이 issue를 이동하지 않으며 review 전 triage·archive를 허용하지 않는다.

## Output

inbox issue와 collection receipt.

## Failure State

원본을 유지하고 차단 이유를 보고한다.

## Prohibited

copy 후 delete, 목적지 덮어쓰기, 고지 없는 자동 수집을 하지 않는다. update 수집은 검증 성공·receipt 확정 뒤에만 원본을 정리한다.
