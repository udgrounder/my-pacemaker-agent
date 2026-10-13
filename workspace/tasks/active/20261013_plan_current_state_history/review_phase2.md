# 독립 구현 검증 2차

## 대상·방법

plan.md, review_phase1.md, changelog.md, critique.md, Runtime layer1_review.md와 실제 git diff를 대조했다. project_rules.md와 shared/architecture.md의 source/dist·승인·과거 자산 보존 경계도 확인했다. 구현 대화 상속 없이 시작했으며 changelog의 자기 설명만으로 1차를 재평가하지 않았다. 승인 발화는 호출에서 제공된 사용자 evidence(상세 개선 방향 보고 뒤 “개선 진행해줘”)를 사용하고 현재 명세·체크섬·구현은 직접 확인했다. 소스 수정 없이 이 보고서와 review_summary.md만 Write 도구로 저장했다.

## 검토 결과

### ✅ 정합성 확인

**구현 주장과 실제 결과**

- 현재 계획/이력 정본, 이력 선저장, 미해결 실패 보존, 점진 전환 주장은 `.mpa/runtime/core/agent_rules.md:284` 이하 실제 추가 규칙과 일치한다. plan 템플릿의 내부 이력·실행 중 변경 기록 제거, changelog의 계획 결정/승인/구현 섹션 구분, sub_template의 취소선 누적 지시 교체도 실제 diff에 있다.
- layer1_design/implement/discovery/review, detail의 재개·minor, session_protocol, glossary, discovery_classification, guidebook의 연관 변경을 실제 diff로 대조했다. 관련 Runtime·guidebook 검색에서 구 `실행 중 변경 기록`을 현재 plan에 요구하는 지시는 남지 않았다. 1차 changelog 격리는 유지된다.
- 승인 도구 주장은 plan_hash.py의 atomic_write(:178), write_approval_pair(:231), renew_spec(:308), 최초 approve 단일 교체(:479)에 실제로 존재한다. code_gate.py의 두 integrity 경로는 실제 plan 경로를 전달해 journal 잔존을 검사한다.
- session_protocol·discovery 분류·gate·최초 approve·정책 테스트 변경은 changelog의 구현 묶음과 대응한다. 파일별 설명을 중복하지 않았다는 이유만으로 누락으로 판정하지 않았다.

**승인 근거·명세 영향·현재 해시**

- 최초 승인 evidence는 현재 plan/changelog 정본, 절차·승인 도구 공동 수정, 새 작업부터 점진 적용, 실패 처리·검증 보존을 보고한 뒤 사용자가 “개선 진행해줘”로 실행을 승인한 것이다. issue의 개선 방향 보고와 현재 명세 범위도 이를 뒷받침한다. 도구 체크섬만으로 사용자 발화를 증명한 것으로 간주하지 않았다.
- 직접 실행한 check는 `일치: reqspec-v1:74809779fbf1bef0`, exit 0이다. 최초 승인 기록과 현재 명세 해시가 같다. audit은 frontmatter_exists=true, missing=[], invalid=[]이며 복구 기록 잔존을 판정하지 않았다.
- 복구 JSON·legacy 구분·잠금 후 원본 재대조는 승인 범위의 실패 처리·호환 구현 구체화다. 해시 알고리즘 함수는 git diff에서 변경되지 않았고 목적·범위·완료 기준 축소 근거가 없다. 최초 승인 뒤 명세 변경 승인이 없으므로 현재 changelog의 빈 명세 변경 표와도 모순되지 않는다.

**폐기 판단·실패 근거 보존**

- 단순 원복에서 중단/원복 실패 탐지로 보완한 판단, 기존 표/legacy 해시 구분, journal 독점 생성만으로 충분하다는 가정의 보완은 changelog의 전후 행에 남아 있다. critique.md의 실패 시나리오·숨은 가정 원문도 보존되어 있다.
- 호출 직전 원본은 이전 승인 명세 복원이 아니라는 구분은 detail의 복구 절차(:81)와 `test_new_layout_rollback_failure_keeps_recovery_and_original_plan`에 있다. 기존 실패 증빙·후행 섹션 보존은 test_plan_hash.py:193, 저장 실패·중단·원복 실패·외부 편집·정리 실패는 :207–354에서 확인한다.
- 현재 plan의 실패 반례, 완료 기준, 유효 제외 범위, 사용자 확인 TODO는 남아 있다. 완료 기준 축소나 미충족 증빙 제거를 확정하지 못했다. 일반 문서 정리의 이력 선저장은 문서 지시이며 자동 트랜잭션을 구현했다고 주장하지 않는다.

**새 배치·기존 배치 호환**

- 표 없는 reqspec-v1 plan은 changelog 경로, 표가 남은 reqspec-v1 plan은 기존 단일 파일 경로를 사용한다. 정상·반복 갱신, 기존 파일/후행 섹션·특수문자 보존은 test_plan_hash.py:160–205 및 :386–425에 있다.
- approval_history_match는 정확한 헤딩·중복·명세 앞/안 위치를 검사한다. 잘못된 배치·legacy/잘못된 해시는 쓰기 전에 거부된다. 기존 표를 changelog에 보존·대조한 뒤 제거하고 전환만으로 명세/해시를 바꾸지 않는 절차는 agent_rules.md:291와 detail:83에 있다.
- 완료 이력·다른 작업의 일괄 재작성은 실제 git status/diff에서 발견하지 못했다. 접두사 없는 legacy 해시 자동 승인 전환을 구현했다고 해석하지 않았다.

**기록 현재성 보완 재대조**

- 2차에서 architecture를 참고 전용으로 표시한 plan과 실제 수정의 불일치, 완료 테스트/parity를 남은 확인에 남긴 changelog를 전달했다. 실제 최종 파일에서 architecture가 수정 대상으로 이동했고 완료 증빙은 보존한 채 남은 확인을 독립 2차·사용자 확인으로 정리했다. 변경 이유도 changelog의 결정 행에 보존되었다. 이후 check를 다시 실행해 같은 승인해시를 확인했다. 이 두 후보는 해결되어 잔여 계수에서 제외한다.

**직접 실행 증빙**

- 전체 단위 테스트: 208 tests / failures 0 / errors 0 / OK / exit 0. 1차 및 메인 보고와 별개로 2차가 직접 실행했다.
- Runtime source/dist 전체 비교: 출력 없음, exit 0.
- git diff --check: 출력 없음, exit 0.
- 객관적 소스·문서·테스트 근거로 1차 잔여 지적 0개 판정을 유지한다. 구현자 설명만으로 뒤집은 항목은 없다.

### ⚠️ 주의 필요

최종 잔여 0개. 기록 현재성 두 후보는 실제 수정과 이력 보존을 재확인했다.

### 🚨 즉시 수정 필요

0개. 승인 없는 기준 완화·승인해시 불일치·구현 주장과 실제 결과의 필수 불일치를 확정하지 못했다.

### 📝 조용한 결정 목록

0개. journal·외부 편집 보존·legacy 분리·최초 승인 단일 교체·동시 원본 재대조는 계획 또는 변경 이력에 공개되어 있으며 승인 범위에 맞는다.

### 🔍 에이전트 가정 검증

- 내부 이력 표로 저장 배치 판별 / 유효 / 정확한 헤딩·명세 위치 검사와 reqspec-v1 배치 호환으로 구현되어 있다.
- 규칙 정리와 제한된 승인 도구 변경으로 해결 가능 / 검증 범위에서 유효 / 해시 알고리즘·사용자 승인 필요 조건·독립 1차 격리는 유지된다.
- 틀린 가정 0개. journal 독점 생성만으로 충분하다는 중간 판단은 원본 재대조로 보완됐고 이전 판단과 이유가 보존되어 있다.

## 판정

최종 잔여 지적 없음. 테스트 진행 가능하며 이미 에이전트가 확인한 테스트를 반복 요구하기보다 사용자 관점의 결과 확인으로 진행할 수 있다. 사용자 결과 확인·명시적 완료 승인은 남아 있고 이 보고서가 이를 대신하지 않는다. major 실패비용 판단은 다중 Runtime 규칙·승인 저장/복구 계약의 실제 복잡도에 맞아 보정 기록을 요구할 틀린 추정은 발견하지 못했다.
