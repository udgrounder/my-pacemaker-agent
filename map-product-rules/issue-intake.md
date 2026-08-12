# Issue Intake Profile

## Trigger

사용자가 지정 프로젝트의 특정 issue 수집을 요청할 때.

## Input

project root, safe project-ref, issue filename, 수집 목적.

## Allowed Actions

지정 issue만 inbox로 원자 이동하고 archive 유사 filename 후보를 기록한다.

## Checks

민감정보·절대 경로·중복·archive 충돌과 유사 이력을 확인한다.

## Gates

사용자가 지정하지 않은 issue는 이동하지 않으며 review 전 triage·archive를 허용하지 않는다.

## Output

inbox issue와 collection receipt.

## Failure State

원본을 유지하고 차단 이유를 보고한다.

## Prohibited

copy 후 delete, 목적지 덮어쓰기, 자동 수집을 하지 않는다.
