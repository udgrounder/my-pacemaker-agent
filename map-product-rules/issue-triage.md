# Issue Triage Profile

## Trigger

사용자가 검토 내용을 보고 채택 또는 기각을 결정할 때.

## Input

issue, 사용자 결정, 판단 근거, 채택 시 새 작업 항목 plan.md.

## Allowed Actions

채택 시 새 작업 항목을 만들고 plan.md 경로를 이슈에 연결한 뒤 archive한다. 기각 시 판단 근거를 이슈에 기록한 뒤 archive한다.

## Checks

사용자가 결정하기 전에 검토 내용을 제시했는지, 채택 시 연결할 task plan이 존재하는지, archive 충돌을 확인한다.

## Gates

사용자 결정 없이 archive하지 않는다. 채택은 새 작업 항목의 plan.md가 만들어진 뒤에만 archive하며, 기각은 비어 있지 않은 판단 근거가 있어야 archive한다.

## Output

판단 근거와 사용자 결정, 선택적으로 연결 작업 경로를 포함한 archive issue.

## Failure State

issue를 inbox에 유지하고 필요한 검토 정보 또는 사용자 결정을 요청한다.

## Prohibited

별도 review receipt·triage receipt를 만들지 않는다. 채택 이슈를 새 작업 항목 없이 archive하거나, 기각 이슈를 판단 근거 없이 archive하지 않는다.
