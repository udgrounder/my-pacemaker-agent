# Changelog — MPA 시스템 개선

## 수정 파일

### dist/.mpa-workspace/core/agent_rules.md
- **판단 불가 처리** (§요청 유형 자동 판단): 3지선다 메뉴 → 에이전트가 추론 후 단일 제안으로 변경
- **Task 기준** (§Task 필요 여부 판단): "단일 파일" → "영향 범위가 해당 파일로 국한됨 (다른 모듈 인터페이스·전역 설정 변경 없음)"
- **비평 임계값** (§비평 필요 여부 자동 평가): 기준 1개 이상 → 🔴고위험 1개 이상 OR 🟡중위험 2개 이상으로 상향. 기준 테이블에 위험도 컬럼 추가
- **자가 개선 필터** (§역할 메모리 업데이트): "놀라움 필터" 명칭을 "자가 개선 필터"로 변경. 사실 기반 조건 3개 추가 (가정 틀림 / plan.md 수정 / 범위 밖 보고). 기존 질문은 보조 기준으로 유지
- **Layer 2 자동 제안** (§작업 완료): done/ 태스크 3개 이상 시 Layer 2 제안 로직 추가

### dist/.mpa-workspace/inject/layer1_implement.md
- §세션 종료 시 6번: "놀라움 필터" → "자가 개선 필터"

### dist/.mpa-workspace/inject/layer1_review.md
- §세션 종료 시 2번: "놀라움 필터" → "자가 개선 필터"

## 추가 수정 (작업 결과 검토 후)

### dist/.mpa-workspace/core/agent_rules.md
- **Layer 2 추적 기준 명확화** (§작업 완료): `INDEX.md`의 `[Layer 2 완료] YYYY-MM-DD` 마커 기준으로 이후 done 태스크를 카운트하도록 수정. Layer 2 완료 시 마커 기록 의무 추가
- **검토 생략 위험 고지** (§작업 생성): "바로 진행" 요청 시 에이전트 가정 목록을 먼저 고지하고 재확인 받도록 추가 (비평 3)
- **critique 새 스레드 강제** (§비평 필요 여부 자동 평가): 같은 스레드에서 critique 수행 금지 명시 (비평 9)
- **upgrade-candidates 처리 트리거** (§작업 종료 시): 3개 이상 누적 시 하네스 업데이트 세션 제안 추가 (비평 6)

### dist/.mpa-workspace/inject/layer1_design.md
- **critique 새 스레드 강제** (§세션 종료 시 7번): 설계 세션에서 직접 critique 수행 금지, 사용자에게 새 스레드 안내 의무 추가 (비평 9)

## 반영
- `python3 install.py --project . --agents claude --upgrade` 2회 실행 완료
- `.mpa-workspace/` 교체 확인됨
