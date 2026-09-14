# 로컬 MPA 효과 측정

이 도구는 평가자가 작성한 JSON run record를 검사하고 조건별 요약을 만든다. 실제 프로젝트 파일·대화 원문·credential·개인 경로를 읽거나 전송하지 않으며, agent나 모델을 실행하지 않는다.

```bash
python3 evaluations/summarize.py evaluations/fixtures/valid-study.json \
  --json-out /tmp/evaluation-report.json \
  --markdown-out /tmp/evaluation-report.md
```

먼저 [protocol.md](protocol.md)와 각 scenario를 읽고, 비교하는 두 조건의 model·도구 권한·초기 소스·요청·시간 제한을 같은 `condition_manifest`에 기록한다. `token_count`와 시간 값을 모르면 `null`을 쓴다. 시각은 UTC `Z` 형식이다. `stopped` run에는 `stop_reason`을 기록하고, `session_resume` run에는 재개 요청과 첫 수용 기준 행동의 시각을 함께 기록한다.

생성된 보고서는 작은 표본의 기술 통계다. MPA의 성능 향상·인과관계·통계적 유의성을 증명하지 않으며, 합성 fixture는 집계기 테스트에만 쓴다.
