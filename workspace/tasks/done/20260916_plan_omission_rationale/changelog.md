# 태스크 내역서: 계획서 생략 사유 기록

**작업일:** 2026-09-18
**계획서:** `plan.md`

---

## 변경 파일 목록

| 파일 경로 | 변경 유형 | 설명 |
|---------|---------|------|
| `.mpa/runtime/templates/plan_template.md` | 수정 | 작업 분류 판단 근거와 선택적 섹션 생략 사유 표, 변경 기록 형식을 추가 |
| `.mpa/runtime/inject/layer1_design.md` | 수정 | major 계획 작성과 자기 점검에 생략 사유 확인을 추가 |
| `.mpa/runtime/core/agent_rules_detail.md` | 수정 | minor 자동 승인 전 기록과 최소 확인 기준을 정렬 |
| `.mpa/runtime/inject/layer1_review.md` | 수정 | 구현 후 초기 표와 후속 변경 기록을 대조하는 검토 기준을 추가 |
| `tests/test_plan_hash.py` | 수정 | 분류 근거 checksum 및 source/dist CLI 결과 일치 검증을 추가 |
| `tests/test_todo_policy.py` | 수정 | 템플릿·major/minor 절차·변경 경로의 정책 검증을 추가 |
| `tests/test_policy_consistency.py` | 수정 | source와 dist Runtime의 규칙 일치 검증을 추가 |
| `dist/.mpa/runtime/` | 수정 | `sync-runtime`으로 source Runtime을 동기화 |

---

## 상세 변경 내역

### `Runtime 계획·검토 절차`

- **대상:** plan 템플릿과 major/minor 작성·검토 지침
- **변경 유형:** 수정
- **내역:** 선택적으로 생략한 섹션은 초기 표에 조건과 작업 사실을 한 줄로 기록하게 했다. 사용자 승인 뒤 초기 표는 보존하고, 명세에 영향이 없는 후속 판단만 다섯 열의 실행 중 변경 기록으로 남기게 했다.

- **독립 검토 보완:** minor가 생략했던 변경 기록 섹션을 구현 중 다시 만들 수 있게 하고, `확인 필요`와 완료 증거 축소를 사용자 확인·`renew-spec` 경로로 보냈다. major의 분류 근거와 선택적 섹션 목록도 템플릿과 설계 절차에 같은 의미로 맞췄다.

### `회귀 검증`

- **대상:** Runtime 정책·checksum 검사
- **변경 유형:** 수정
- **내역:** 작업 분류 근거가 요구사항 명세 checksum에 포함되는지, source와 dist hook이 같은 결과를 내는지, Runtime 문서가 동기화되는지를 검사한다. 절차별 필수 문구를 직접 확인하고 minor 후속 변경 기록 지시를 제거한 입력이 실패하는 음성 사례도 추가했다.

- **2차 검토 보완:** major 설계 자기 점검에서 표의 각 행을 실제 조건·작업 사실과 대조하게 하고, 형식적 생략 사유와 구체 사유 형식을 제거한 입력이 실패하는 정책 음성 사례를 추가했다.

---

## 요구사항 명세 대비 변경 사항

| 변경 | 이유 | 명세 영향 | 보고 |
|---|---|---|---|
| 없음 | 승인된 범위와 완료 기준 안에서 절차와 회귀 검증을 구현함 | 없음 | 검증 진입 시 누적 기록 |

## 이번 작업 범위 밖의 기존 변경

| 파일 경로 | 구분 사유 |
|---------|----------|
| `.mpa/runtime/.mpa-version`, `dist/.mpa/runtime/.mpa-version` | 이전 TOML 참조 계약 릴리즈 작업에서 이미 생성된 현재 릴리즈 포인터 변경이며, 이번 작업에서는 수정·릴리즈·배포하지 않음 |

---

## 검증 포인트

- [x] 정상 경로 확인: major/minor 기록 시점과 구체 사유 형식을 정책 검사로 확인
- [x] 실패 경로 확인: 형식적 사유와 `확인 필요`의 명세 변경 경로를 정책 검사로 확인
- [x] plan.md 완료 기준 충족 여부: source 정책·checksum 회귀, Runtime parity, source/dist CLI fixture, 전체 회귀 및 형식 검사 통과
- [x] 독립 검토: 1차·2차 지적을 반영한 재검토에서 추가 발견 없음
