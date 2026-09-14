---
태스크: minor_index_registration_issue_closure
생성일: 2026-09-14
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: reqspec-v1:4a34f958d2487364
승인대상: 요구사항 명세
---

# 작업 계획서: minor 태스크 INDEX 등록 이슈 정리

**파생 출처:** `workspace/issues/inbox/my-pacemaker-agent/index_registration_omission.md` — minor 태스크 생성 시 INDEX 등록 누락 방지 규칙

## 요구사항 명세

### 요청 기준

사용자는 남은 2번 작업도 처리해 달라고 요청했다.

### 목적

minor 태스크 생성 절차에 INDEX 즉시 등록이 이미 반영됐는지 source·dist Runtime에서 확인하고, 중복 구현을 유발할 수 있는 inbox 이슈를 처리 근거와 함께 보관한다.

### 범위·제외 범위

- 범위: minor 절차의 INDEX 등록 단계와 source/dist 동기화 확인, 이슈의 해결 근거 및 연결 작업 기록, legacy archive 처리.
- 제외 범위: plan hash hook의 동작 변경, Runtime release·deploy, 태스크 INDEX 자동 등록 기능 추가.

### 완료 기준

- source·dist Runtime의 minor 경량 처리 절차가 새 태스크의 INDEX 등록을 독립 단계로 명시함을 확인한다.
- 이슈는 사용자 요청과 확인 근거, 이 작업 계획의 경로를 보존한 채 archive된다.

### 사용자 결정

- 2번 이슈를 처리한다.

### 변경 불가 제약

- 이미 반영된 Runtime 규칙과 배포본을 중복 수정하지 않는다.
- 실제 release 또는 deploy를 실행하지 않는다.

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|---|---|---|
| minor 절차의 INDEX 등록 단계가 재발 방지에 충분하다 | 등록을 승인보다 앞선 독립 3단계로 명시한다 | hook 기반 강제를 별도 설계 작업으로 분리한다 |

### 결정 대기 항목 (Open Questions)

없음.

### minor 판단 근거

- 한 파일/단일 관심사: 이미 해결된 INDEX 등록 이슈의 확인·보관만 수행한다.
- 설계 결정 불필요: 예방 절차가 source·dist에 이미 동일하게 존재한다.
- git reset으로 복구 가능: 저장소 내부 작업 기록과 이슈 이동만 수행한다.
- 사용자 취향·의사결정 불필요: 2번 이슈 처리 요청을 이미 받았다.

## 실행 계획 (Implementation Plan)

### 구현 단계

- [x] Step 1 — source·dist minor 절차의 INDEX 등록 단계를 대조한다. / 이유: 해결되지 않은 이슈를 잘못 닫지 않는다.
- [x] Step 2 — 이슈에 확인 근거와 연결 작업을 남기고 legacy archive로 이동한다. / 이유: 중복 구현을 막고 사용자 결정을 보존한다.

## 실행 TODO

### 구현·에이전트 검증

- [x] source·dist의 INDEX 등록 단계와 동기화 상태 확인.
- [x] legacy archive 결과와 작업 계획 링크 확인.

### 사용자 결정·승인 필요

- [x] 2번 이슈를 처리.
- [x] 구현 결과 확인 후 완료 승인.

## 검증 결과

### 검증 체크리스트

- [x] 정상 경로: source·dist minor 절차가 같은 INDEX 등록 단계를 가진다.
- [x] 실패 경로: 절차가 없거나 불일치하면 archive하지 않고 별도 Runtime 개선 작업으로 분리한다.
- [x] 엣지 케이스: plan hash hook의 리마인더는 이 이슈에서 선택 사항이므로 구현하지 않는다.

## 실행 중 변경 기록

| 변경 내용 | 이유 | 명세 영향 |
|---|---|---|
| legacy archive 방식 사용 | inbox 이슈에 구조화 metadata가 없어 자동 archive가 적용되지 않는다 | 없음 |

## 운영 시 안내 사항

| 영향 대상 | 운영상 달라지는 점 | 사용자 안내 |
|---|---|---|
| minor 태스크 생성 | INDEX 등록은 plan 작성 뒤, approve 전에 수행한다 | 별도 수동 리마인더를 요청할 필요가 없다 |
