# Issue Triage Profile

## Trigger

accepted review receipt가 있는 inbox issue를 분류할 때.

## Input

issue, review receipt, 재현성, 영향도, 우선순위, 관계, 후속 task.

## Allowed Actions

triage, `needs_information`/`undetermined` 유지, release·deployment·verification 근거가 있는 resolve/archive.

## Checks

accepted receipt, deployment의 release ID 일치, archive 충돌과 유사 관계를 확인한다.

## Gates

근거가 부족하면 archive하지 않는다. resolved archive에는 release, deployment, verification 근거가 모두 필요하다.

## Output

triage/resolution/archive receipt와 inbox 또는 archive 상태.

## Failure State

issue를 inbox에 유지하고 필요한 정보를 보고한다.

## Prohibited

review 없이 triage, triage만으로 resolved 주장, 다른 release deployment를 해결 근거로 연결하지 않는다.
