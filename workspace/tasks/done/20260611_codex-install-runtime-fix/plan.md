---
태스크: codex-install-runtime-fix
생성일: 2026-06-11
타입: minor
실패비용: minor
상태: 완료 승인
승인해시: 0f293fad76e7bae0
---
# 작업 계획서: codex-install-runtime-fix

## 에이전트 보고

### 사용자 결정 필요

없음

### 암묵적 결정

- Codex 설치 결과를 현재 저장소에서 실제 사용 중인 방식에 맞춘다 — `AGENTS.md` include, `.codex/hooks.json`, `.codex/agents/` 기준 / 다른 방향이면: 문서에만 한계 고지 유지

### 에이전트 가정

| 가정 | 근거 | 틀렸다면 |
|-----|------|---------|
| `.codex/agents/*.toml` 기반 developer instructions 구성이 현재 Codex 운영 기준과 맞다 | 이 저장소가 이미 해당 구조를 사용 중이다 | 설치 산출물에서 `.codex/agents/` 생성을 제외하고 다른 로딩 방식으로 재조정해야 한다 |
| Codex hook matcher는 `apply_patch` 등 Codex 편집 도구명을 포함해야 실효성이 있다 | `code_gate.py`가 이미 Codex 도구명을 별도로 인지한다 | 실제 Hook matcher 문법이 다르면 `.codex/hooks.json` 생성 형식을 다시 맞춰야 한다 |

### minor 판단 근거

- 한 파일/단일 관심사: 아니오, 다파일이지만 모두 Codex 설치 체계 정합화라는 단일 관심사
- 설계 결정 불필요 (방법이 자명함): 예, 현재 저장소의 실사용 구성을 설치 산출물에 반영하면 된다
- git reset으로 복구 가능: 예
- 사용자 취향·의사결정 불필요: 예

## 요청 원문

실제 동작하게 수정안 만들어줘

## 목적

Codex 설치 절차가 문서·spec·설치 결과물까지 실제 동작 가능한 한 가지 방식으로 일치하도록 수정한다.

## 요구사항

- `AGENTS.md` 주입 내용이 Codex에서 규칙 파일을 실제로 참조할 수 있어야 한다
- Codex hook 등록이 실제 편집 도구에도 적용되도록 matcher를 보강한다
- 설치 결과물이 현재 저장소의 Codex 운영 방식과 일치해야 한다
- 설치 문서와 spec 설명을 구현과 맞춘다
- 임시 프로젝트 설치 검증으로 결과를 확인한다

## 구현 단계

- [ ] Step 1 — Codex 현재 운영 파일과 설치 산출물 차이를 정리하고 반영 대상 결정 / 이유: 설치 결과 정합화
- [ ] Step 2 — `install.py`, `install.md`, `agent-specs/codex/*` 수정 / 이유: 문서와 구현 일치
- [ ] Step 3 — 배포용 Codex 기본 파일 추가 또는 동기화 / 이유: 설치 시 실제 동작 구성 보장
- [ ] Step 4 — 임시 프로젝트 설치 검증 / 이유: 문서 검토가 아닌 실제 결과 확인

## 예상 조용한 결정

- Codex native 규칙 파일 경로: `.agents/rules/`는 유지하되 실제 진입은 `AGENTS.md`와 `.codex/agents/*.toml`로 이중 보강
- Hook matcher 범위: `Edit|Write` 외 Codex 편집 도구명을 함께 포함

## 수정 대상 파일

| 파일 경로 | 변경 내용 |
|---------|---------|
| install.py | Codex 설치 산출물 및 hook 생성 로직 보강 |
| install.md | Codex 설치 절차와 결과 설명 수정 |
| agent-specs/codex/spec.md | Codex spec을 실제 구현 기준으로 정렬 |
| agent-specs/codex/inject/AGENTS.md | Codex include 문법 반영 |
| agent-specs/codex/files/* | 필요 시 Codex 기본 설정 파일 추가 |
| workspace/tasks/INDEX.md | active 태스크 등록 |

## 참고 파일 (수정 없음)

- AGENTS.md — 현재 저장소의 Codex include 사용 예시
- .codex/hooks.json — 현재 저장소의 Codex hook 예시
- .codex/agents/mpa_pacemaker.toml — 현재 저장소의 Codex developer instructions 예시
