# serena

> 한 줄 정체: 언어 서버(LSP) 기반으로 코드를 **심볼 단위**로 이해·편집하게 해주는 코딩 에이전트 툴킷. AI 에이전트가 "이 함수 어디서 쓰여?"를 정확히 묻고 고치게 한다.
> 출처: https://github.com/oraios/serena · 확인일: 2026-06-25 (+ 이 repo의 `.serena/` 실측)

---

## 머릿말 — 이게 나에게 맞는가

- **언제 필요한가** (결론 먼저): **에이전트가 코드를 정확히 탐색·편집해야 할 때.** grep/문자열 매칭이 아니라 심볼(정의·참조·호출) 단위로 다뤄야 하는 중·대형 코드 프로젝트에 가치가 크다.
  - 안 맞는 경우: 해당 언어의 language server가 없거나 미성숙한 스택. serena의 정확도는 LSP에 의존하므로 지원 언어 여부가 도입 전 결정 요인이다. (지원 언어 목록은 `.serena/project.yml` 주석 참조)
- **사상** (태그): **질의·상주형** — 영구 산출물을 만들지 않고, 세션 동안 떠 있으며 에이전트 질의에 실시간 응답한다. (이 사상에서 2번 MCP, 9번 상주, 8번 산출물 "해당 없음"이 따라온다)
- **동작 방식** (운영 메커니즘만): 프로젝트 언어의 **language server(LSP)를 로컬에서 띄워** 심볼 그래프를 잡고 → 에이전트의 탐색·편집 요청에 심볼 레벨로 응답한다. 코드를 외부 LLM에 보내지 않는다.

---

## 운영 절차

### 1. 설치
`uv`로 관리한다. `uv tool install -p 3.13 serena-agent` (uv 설치가 유일한 선행 조건). **머신 전역 1회** 설치하면 `serena` 명령을 쓸 수 있다.

### 2. 연결
**MCP 서버.** 클라이언트(Claude Code/Desktop, VSCode·Cursor·JetBrains 등)에 실행 명령을 주거나, HTTP 모드로 직접 띄워 URL을 제공한다.

### 3. 프로젝트별
`serena init` → 프로젝트 루트에 **`.serena/` 폴더**가 생성된다. (실측: `project.yml` = 언어·인코딩 등 진짜 config, `project.local.yml` = 로컬 오버라이드, `cache/`, `memories/`, `.serena/.gitignore`) 설정은 전역·프로젝트·컨텍스트 레벨로 합성된다.

### 4. 팀원 공유
공식 docs에는 명시가 없다. **실측 근거**: serena가 `.serena/.gitignore`로 `cache/`·`project.local.yml`만 제외하고, `project.yml`엔 "intended to be versioned" 주석이 있다. 따라서 최소한 다음처럼 보는 것이 안전하다.
- **공유**: `project.yml`
- **각자**: `project.local.yml`, `cache/`
- **정책 결정 필요**: `memories/`는 기본 ignore 대상이 아니므로, 팀이 공유할지 로컬로 둘지 별도 결정해야 한다

(출처: 이 repo `.serena/` 실측)

### 5. 유지보수
⚠️ **미확인** — 공식 docs에 재인덱싱 필요 여부 명시가 없다. LSP 특성상 코드 변경을 서버가 실시간 반영하는 것이 일반적이나, serena 문서로는 확인되지 않았다.

### 6. 비용·주의·보안
**로컬 실행.** 오픈소스 language server(또는 유료 JetBrains 백엔드)를 사용한다. 검색·편집이 "at the symbol level"로 동작하며 **코드를 외부 LLM에 보내지 않는다.**

### 7. 되돌리기
⚠️ **미확인** — 공식 docs에 제거 절차 명시가 없다. (uv 설치이므로 `uv tool uninstall serena-agent` + 프로젝트 `.serena/` 삭제로 추정되나 문서 미확인.)

### 8. 산출물 위치
**해당 없음** (질의형 — 영구 산출물 없음). 부수적으로 `.serena/`에 `cache/`·`memories/`(에이전트 메모리)가 쌓인다.

### 9. 실행/생명주기
**상주 서버**(MCP, long-lived). 공식 README 기준으로는 보통 **클라이언트에 launch command를 설정**해 연결한다. 정확한 start/stop과 자동 기동 방식은 클라이언트별 설정에 따라 달라진다. (이 repo 환경에서는 클라이언트가 기동 시 연결하는 형태로 관찰됨.)

---

## 출처 메모

- 1·2·3·6번: 공식 README(https://github.com/oraios/serena, 2026-06-25).
- 4번: 공식 미명시 → 이 repo `.serena/.gitignore`·`project.yml` 주석·`memories/` 존재 실측으로 보강.
- 5·7번: 공식 docs에서 확인 불가 → **미확인** 표기 유지(추측으로 채우지 않음).
- 9번: "long-lived" 언급은 공식, 자동 기동 형태는 환경 관찰 기반.
