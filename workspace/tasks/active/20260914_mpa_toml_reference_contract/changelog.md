# 태스크 내역서: mpa_toml_reference_contract

**작업일:** 2026-09-15
**계획서:** plan.md

---

## 변경 파일 목록

| 파일 경로 | 변경 유형 | 설명 |
|---|---|---|
| .mpa/runtime/contracts/agent_reference.toml | 추가 | experimental 읽기 전용 참조 계약 |
| .mpa/runtime/contracts/agent_reference_profile.md | 추가 | V1 TOML profile·호환성·권한 규격 |
| .mpa/runtime/hooks/contract_reference.py | 추가 | Python 3.9 validator CLI |
| .mpa/runtime/core/agent_rules.md | 수정 | 경로·상태 binding marker와 stable anchor |
| .mpa/runtime/core/agent_rules_detail.md | 수정 | stable entry anchor |
| guidebook/guidebook.md | 수정 | 설치본 검증 사용법과 제한 |
| tests/test_contract_reference.py | 추가 | profile·drift·discovery·권한 경계 회귀 |
| dist/.mpa/runtime/ | 수정 | source Runtime 동기화 결과 |

---

## 상세 변경 내역

### Runtime 참조 계약

- **대상:** contracts/agent_reference.toml, contracts/agent_reference_profile.md
- **변경 유형:** 추가
- **내역:** 작업·문서 기본 경로, major/minor 상태 모델, Markdown 진입점을 protocol version 1의 inspect-only 계약으로 제공했다. hook 실행·파일 변경·승인·배포 권한은 제공하지 않는다.

### 검증기와 정본 연결

- **대상:** hooks/contract_reference.py, core/agent_rules.md, core/agent_rules_detail.md
- **변경 유형:** 추가/수정
- **내역:** 제한된 TOML 부분집합을 Python 3.9 표준 기능으로 검사하고, Markdown anchor와 binding marker의 값 단위 drift를 검출한다. version 20, schema 21, reference 22, drift 23의 종료 코드를 제공한다.

### 설치본 사용과 회귀

- **대상:** guidebook/guidebook.md, tests/test_contract_reference.py
- **변경 유형:** 수정/추가
- **내역:** 프로젝트 root 기반 discovery 사용법을 문서화하고, 독립 TOML parser oracle, source/dist, invalid version, path escape, anchor 누락, semantic drift, symlink, 비변경 consumer 흐름을 테스트했다.

### 독립 검토 보완

- **대상:** contracts/agent_reference.toml, contracts/agent_reference_profile.md, hooks/contract_reference.py, tests/test_contract_reference.py
- **변경 유형:** 수정
- **내역:** 독립 검토 결과에 따라 모든 public path·lifecycle·reference의 V1 baseline을 고정했다. 같은 version의 의미 변경과 새 reference는 code 20으로 중단한다. authority를 계약 필드로 추가하고, 손상 입력의 JSON diagnostic, 중복 marker, source와 dist CLI 실행·바이트 parity를 회귀 검사로 추가했다.

### 2차 검토 후 profile 경계 보완

- **대상:** hooks/contract_reference.py, tests/test_contract_reference.py
- **변경 유형:** 수정
- **내역:** 문자열 배열에도 scalar와 같은 non-TOML slash escape 거부를 적용했다. profile parser와 독립 parser oracle의 허용 경계를 맞추고 회귀 fixture를 추가했다.

---

## 요구사항 명세 대비 변경 사항

| 변경 | 이유 | 명세 영향 | 보고 |
|---|---|---|---|
| TOML profile을 JSON 호환 문자열·문자열 배열로 한정 | Python 3.9에서 외부 설치 의존성 없이 표준 호환 subset을 안정적으로 검사 | 없음 — 설계의 제한 profile 정책을 구현 | 구현 완료 보고에 포함 |
| V1 public field baseline 고정과 validator 오류 정규화 | 독립 검토에서 같은 version의 경로·상태·reference 의미 변경 및 손상 입력 처리 빈틈을 발견 | 없음 — 승인된 compatibility·safe-stop 정책의 구현 보완 | 구현 완료 보고에 포함 |

---

## 검증 포인트

- [x] 정상 경로 확인: source와 dist validator가 contract version 1을 성공으로 보고.
- [x] 실패 경로 확인: version, profile, reference, semantic drift, symlink 회귀 검사.
- [x] plan.md 완료 기준 충족 여부: 구현·문서·source/dist 동기화 및 전체 테스트 통과. 독립 구현 검증은 다음 단계에서 수행.
