# bug_fix

- 입력: 재현 절차가 있는 합성 버그 보고
- 초기 상태: 실패하는 regression test와 최소 구현 fixture
- 수용 기준: 재현 test가 통과하고 관련 회귀 검사가 유지
- 실패 판정: 재현 실패 유지, unrelated test 실패, 재현 없이 증상만 숨김
- 중단 조건: 재현 절차가 fixture에서 성립하지 않음
