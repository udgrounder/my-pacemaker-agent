---
태스크: docs_location_issue_closure
생성일: 2026-09-14
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: reqspec-v1:7da409cd7a822dde
승인대상: 요구사항 명세
---

# 작업 계획서: 프로젝트 문서 위치 이슈 정리

**파생 출처:** `workspace/issues/inbox/my-pacemaker-agent/docs_default_location_workspace_docs.md` — 이미 반영된 문서 위치 규칙과 남아 있는 inbox 이슈의 불일치

## 요구사항 명세

### 요청 기준

사용자는 정리된 프로젝트 문서가 `workspace/`가 아니라 최상위 `docs/`에 있어야 한다고 결정했고, 4번 이슈부터 정리해 달라고 요청했다.

### 목적

현재 Runtime과 배포본에 반영된 최상위 `docs/` 기본 위치를 확인하고, 중복 구현을 유발할 수 있는 오래된 inbox 이슈를 해결 기록과 함께 보관한다.

### 범위·제외 범위

- 범위: 현재 source·dist Runtime의 문서 경로 확인, 이슈에 채택 근거와 연결된 작업 계획을 기록한 뒤 archive 처리.
- 제외 범위: 문서 위치 규칙 재수정, 기존 프로젝트 문서 이동, Runtime release·deploy, 다른 프로젝트의 문서 관례 변경.

### 완료 기준

- `docs/`와 `docs/INDEX.md`를 기본 문서 위치로 지정한 source·dist 규칙이 확인된다.
- 이슈는 사용자 결정과 확인 근거, 이 작업 계획의 경로를 보존한 채 archive된다.

### 사용자 결정

- 정리된 프로젝트 문서는 최상위 `docs/`에 둔다. `workspace/`에는 두지 않는다.

### 변경 불가 제약

- Runtime·배포본·기존 문서를 수정하거나 이동하지 않는다.
- 실제 release 또는 deploy를 실행하지 않는다.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|---|---|---|
| 이슈의 구현 제안은 이미 완료됐다 | source·dist Runtime이 모두 `docs/INDEX.md`를 참조한다 | 규칙 구현 작업으로 별도 major 태스크를 만든다 |

### 결정 대기 항목 (Open Questions)

없음.

### minor 판단 근거

- 한 파일/단일 관심사: inbox 이슈의 해결 기록과 archive 처리만 수행한다.
- 설계 결정 불필요: 사용자가 문서 위치를 이미 확정했고 현재 규칙도 일치한다.
- git reset으로 복구 가능: 저장소 내부 작업 기록 이동만 수행한다.
- 사용자 취향·의사결정 불필요: 최상위 `docs/` 선택은 이미 전달됐다.

## 실행 계획 (Implementation Plan)

### 구현 단계

- [x] Step 1 — source·dist Runtime의 문서 위치 규칙을 대조한다. / 이유: stale 이슈를 잘못 닫지 않는다.
- [x] Step 2 — 이슈에 사용자 결정·확인 근거·연결 작업을 기록하고 legacy archive로 이동한다. / 이유: 사용자 결정과 해결 근거를 보존한다.

## 실행 TODO

### 구현·에이전트 검증

- [x] 문서 위치 규칙과 source/dist 동기화 상태 확인.
- [x] legacy archive 결과와 작업 계획 링크 확인.

### 사용자 결정·승인 필요

- [x] 최상위 `docs/`를 프로젝트 문서 위치로 사용.
- [x] 구현 결과 확인 후 완료 승인.

## 검증 결과

### 검증 체크리스트

- [x] 정상 경로: source·dist가 모두 `docs/INDEX.md`를 참조한다.
- [x] 실패 경로: legacy issue는 metadata 누락으로 자동 archive가 거부됨을 확인하고 원문에 처리 근거를 보존한다.
- [x] 엣지 케이스: `workspace/tasks/` 산출물은 프로젝트 문서와 구분해 유지한다.

## 실행 중 변경 기록

| 변경 내용 | 이유 | 명세 영향 |
|---|---|---|
| legacy archive 방식 사용 | inbox 이슈에 구조화 metadata가 없어 자동 archive가 안전하게 거부됨 | 없음 |

## 운영 시 안내 사항

| 영향 대상 | 운영상 달라지는 점 | 사용자 안내 |
|---|---|---|
| 프로젝트 문서 | 새 프로젝트 수준 문서는 최상위 `docs/`에 기록 | 작업 계획·검증 기록은 계속 `workspace/tasks/`에 둔다 |
