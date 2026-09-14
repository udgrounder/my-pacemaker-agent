# session_resume

- 입력: 중단된 합성 작업을 이어서 완료하라는 요청
- 초기 상태: plan/state/partial change가 남은 fixture
- 수용 기준: 재개 요청부터 최초 기준 충족 행동 시각을 기록하고 최종 acceptance test 통과
- 실패 판정: 이전 상태 무시, 중복 질문, 기존 부분 작업 훼손
- 중단 조건: 재개에 필요한 상태 또는 수용 기준이 없거나 모순됨
