---
태스크: operational_docs_sync
생성일: 2026-08-25
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: reqspec-v1:83086bf829be4676
승인대상: 요구사항 명세
---

# 작업 계획서: 운영 문서 정합성 보완

**파생 출처:** zip_runtime_backups — README 전체 검토에서 발견한 운영 설명 불일치

---

## 요구사항 명세

### 요청 기준

사용자가 README 기존 내용 검토에서 확인된 운영 설명 보완을 진행하도록 요청했다.

### 목적

README와 `install.md`가 현재 이력 정리·소스 수정 게이트 정책을 같은 의미로 설명하도록 한다.

### 범위·제외 범위

- 범위: root `README.md`의 Runtime update 설명 가독성·게이트 표현, `install.md`의 오래된 backup retention 설명
- 제외 범위: `release_manager.py` 동작, 보관 수, 배포 절차 자체 변경

### 완료 기준

- 두 문서가 일반 deploy/upgrade에서 이력을 자동 삭제하지 않는 정책과 명시 이력 정리 절차를 일관되게 설명한다.
- README의 source 수정 게이트 설명이 기본 warn·critical/block 및 MPA Runtime 예외와 모순되지 않는다.

### 사용자 결정

- 문서 보완 — 검토에서 제안한 기존 설명 보완을 진행한다.

### 변경 불가 제약

- 실제 Runtime release·deploy·backup 파일을 변경하지 않는다.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|---|---|---|
| 문서 간 정책 동기화만 필요하다. | 사용자는 검토 결과의 문구 보완 진행을 요청했다. | 동작 변경 작업으로 분리한다. |

### 결정 대기 항목 (Open Questions)

없음

### minor 판단 근거

- 한 파일/단일 관심사: 두 문서의 동일한 운영 설명만 동기화한다.
- 설계 결정 불필요: 현재 구현과 command contract가 기준이다.
- git reset으로 복구 가능: 문서 변경만 수행한다.
- 사용자 취향·의사결정 불필요: 사용자가 보완 진행을 명시 승인했다.

---

## 실행 계획

- [x] README의 Runtime update 설명을 release 생성·배포·rollback 단위로 분리하고 source 수정 gate 표현을 현재 정책에 맞춘다.
- [x] `install.md`의 자동 backup retention 설명을 명시 `history-cleanup` 절차로 갱신한다.
- [x] Markdown diff 검사를 수행한다.

## 실행 TODO

- [x] 문서 동기화와 검증을 완료한다.

## 운영 시 안내 사항

| 영향 대상 | 운영상 달라지는 점 | 사용자 안내 |
|---|---|---|
| 문서 독자 | 이력 정리와 gate 동작을 현재 정책대로 읽을 수 있다. | 실행 동작은 바뀌지 않는다. |
