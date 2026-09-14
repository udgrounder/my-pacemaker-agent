# multi_step_feature

- 입력: 명시된 하위 결과를 갖는 합성 기능 요청
- 초기 상태: 독립된 작은 fixture repository와 acceptance test
- 수용 기준: 모든 하위 결과와 acceptance test가 충족
- 실패 판정: 일부 하위 결과 누락, 테스트 실패, 요구 범위 밖 기능 추가
- 중단 조건: 하위 결과가 서로 모순돼 하나의 수용 기준을 만들 수 없음
