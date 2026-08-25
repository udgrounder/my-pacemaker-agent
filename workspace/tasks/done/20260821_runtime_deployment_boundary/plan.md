---
태스크: 20260821_runtime_deployment_boundary
생성일: 2026-08-21
타입: major
실패비용: critical
상태: 완료 승인
승인해시: reqspec-v1:bbeada88673db12f
승인대상: 요구사항 명세
---

# 작업 계획서: [보류] 구형 Runtime 설치·업그레이드 migration

## 요구사항 명세

### 요청 기준

기존 계획은 `.mpa-workspace` 등 구형 설치본을 `.mpa/runtime` 구조로 자동 migration하는 것을 목표로 했다. 2026-08-25 상태 점검에서 실제 구형 설치 대상은 없고, 구형 구조를 자동 지원하지 않는 정책이 이미 별도 작업으로 확정·구현된 것을 확인했다.

### 목적

폐기된 legacy migration 요구를 실행 대상에서 제외하고, 현재 지원 경계와 향후 재개 조건을 보존한다.

### 범위·제외 범위

- 범위: 구형 자동 migration을 보류 처리하고 현재 `.mpa/runtime`, `.mpa/config`, `.mpa/backups` 전용 정책을 기록한다.
- 범위: 원래 요구사항·결정·미완료 TODO는 [legacy_plan.md](legacy_plan.md)로 보존한다.
- 제외 범위: 구형 설치본 자동 변환 구현, 과거 release·receipt·backup 수정, 테스트 대상 폴더 삭제 또는 변경.

### 완료 기준

- 이 task는 active 실행 대상과 INDEX의 active 행에서 제거된다.
- 현재 지원 경계와 재개 조건이 명확히 기록된다.
- 원본 계획은 변경 없이 보존된다.

### 사용자 결정

- 현재 구형 설치 대상은 없으므로 `.mpa-workspace → .mpa/runtime` 자동 migration을 구현하지 않는다.
- 구형 구조를 사용하는 테스트 폴더는 호환성 지원 대상이 아니라 사전검사 차단 동작을 확인하는 자료로만 유지한다.
- 실제 구형 설치본 지원 요구가 생기면 이 계획을 재개하지 않고, 대상·데이터 보존·rollback을 명시한 새 계획으로 사용자 승인을 받아 시작한다.

### 변경 불가 제약

- 현재 설치·업데이트는 `.mpa/runtime`, `.mpa/config`, `.mpa/backups` 구조만 지원한다.
- 구형 구조에 대한 자동 변환이나 우회 배포를 수행하지 않는다.
- `legacy_plan.md`와 immutable release·receipt·backup 이력은 수정하거나 삭제하지 않는다.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|---|---|---|
| 구형 설치 대상은 없다. | 사용자 확인 및 현재 설치 대상 점검 | 실제 대상의 경로·버전·백업 요구를 받은 뒤 새 migration 계획을 수립한다. |
| 현재 `.mpa` 전용 경계가 필요한 안전 정책이다. | 완료된 legacy compatibility 제거 작업과 현행 install/deploy preflight | 지원 정책을 사용자와 다시 결정하고 신규 task로 설계한다. |

### 결정 대기 항목 (Open Questions)

- 없음

## 실행 TODO

- [x] 원본 계획을 `legacy_plan.md`로 보존
- [x] legacy migration 요구를 hold 정책으로 재구성
- [x] INDEX에서 active 대신 hold로 표시

## 검증 결과

- [x] 현재 `install.py`와 `release_manager.py`는 `.mpa/runtime` 없는 대상의 update를 자동 migration하지 않고 중단한다.
- [x] 관련 완료 task `20260821_remove_legacy_path_compatibility`가 current-layout 전용 코드·문서·테스트와 release audit 증빙을 보존한다.
- [x] 구형 테스트 대상 `/Users/kjkim/Temp/mpa-test3`의 dry-run은 현재 Runtime 레이아웃 부재로 차단됨을 확인했다.

## 보존·재개 안내

- 원본 범위·결정·미완료 항목: [legacy_plan.md](legacy_plan.md)
- 재개 트리거: 실제 구형 설치 대상의 지원 요청
- 재개 방식: 새 task 생성 → 대상별 backup·rollback·데이터 보존 범위 설계 → 사용자 승인

## 실행 중 변경 기록

| 변경 내용 | 이유 | 명세 영향 |
|---|---|---|
| active에서 hold로 이동하고 보류 계획으로 재구성 | legacy migration은 현행 정책과 충돌하며 실제 대상도 없음 | 사용자 폐기 결정 반영 |
| hold 기록 완료 승인 및 done 이관 | 추가 실행 항목이 없으며 사용자가 완료 처리를 명시 승인 | 없음 |
