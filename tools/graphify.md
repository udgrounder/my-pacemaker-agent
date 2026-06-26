# graphify

> 한 줄 정체: 코드·문서·PDF·이미지를 "쿼리 가능한 지식 그래프"로 변환해, 대규모 코드베이스의 관계·흐름을 파일을 일일이 열지 않고 질문할 수 있게 하는 도구.
> 출처: https://github.com/safishamsi/graphify · 확인일: 2026-06-25

---

## 머릿말 — 이게 나에게 맞는가

- **언제 필요한가** (결론 먼저): **소스·문서가 많은 대규모(특히 다언어) 코드베이스를 처음 파악할 때.** "이 기능이 어디서 어디로 흐르나"를 그래프로 묻고 싶을 때 가치가 크다.
  - 안 맞는 경우: 파일 수가 적거나 마크다운/설정 위주의 작은 repo. 그래프화의 이득보다 인덱싱 비용이 크다.
- **사상** (태그): **생성·인덱스형** — 한 번 스캔해 그래프 산출물을 만들고, 그 산출물을 반복 질의한다. (이 사상에서 2번 연결의 CLI 중심, 8번 산출물 폴더, 9번 one-shot 실행이 따라온다)
- **동작 방식** (운영 메커니즘만): 프로젝트를 스캔 → **코드는 tree-sitter로 AST를 로컬 추출**, **문서·PDF·이미지는 LLM으로 의미 추출** → `graphify-out/`에 그래프(HTML·MD·JSON)를 떨군다 → 그 그래프에 질의. 코드가 바뀌면 산출물이 낡으므로 재인덱싱이 필요하다.

---

## 운영 절차

### 1. 설치
PyPI 패키지 `graphifyy`. **머신 전역 1회** 설치.

### 2. 연결
세 가지 방식이 있고, 어떤 방식으로 노출하느냐에 따라 9번 생명주기가 갈린다. **CLI·스킬은 대상 경로를 인자로 받으며, 보통 대상 프로젝트의 루트에서 `.`(현재 폴더)로 전체를 스캔한다** — 실행한 자리에 `graphify-out/`이 생긴다(3번 참조).
- **CLI** — 프로젝트 루트에서 `graphify .` (또는 `graphify ./docs`처럼 하위 경로 지정)
- **스킬** — `graphify install`(머신 1회) 후, 프로젝트 루트에서 IDE에 `/graphify .`
- **MCP 서버** — `python -m graphify.serve graphify-out/graph.json` (stdio·HTTP) — 이미 만들어진 그래프에 질의

**중요:** `graphify install`은 프로젝트 안이 아니라 **사용자 홈의 Claude 전역 skill 경로**(`~/.claude/skills/graphify/`)에 설치된다. 따라서 팀원이 각자 자기 Claude Code에서 `/graphify`를 직접 쓰려면 **각자 설치해야 한다.** 반대로, 한 사람이 생성한 `graphify-out/` 산출물만 공유받아 읽는 쪽은 graphify 설치가 필수는 아니다.

### 3. 프로젝트별
전통적 config 파일은 **없다.** 프로젝트 루트에서 명령을 돌리면 그 자리에 산출물이 격리 생성된다. 손댈 수 있는 설정은 제외 규칙뿐 — `.graphifyignore`(`.gitignore` 유사, 선택). ⚠️ **`.graphifyignore` 위치는 README 미명시** — 프로젝트 루트로 추정되나 확인되지 않음.

프로젝트 규모가 커지면 `.graphifyignore`를 사실상 기본 운영 규칙으로 보는 편이 안전하다. 특히 아래처럼 **다시 만들 수 있는 산출물**이나 **질의 가치가 낮은 대용량 바이너리**는 초기에 빼 두는 편이 낫다.
- 빌드 산출물: `dist/`, `build/`, `.next/`, `coverage/`
- 의존성/캐시: `node_modules/`, `.cache/`, `.turbo/`
- 대용량 미디어: `*.png`, `*.jpg`, `*.jpeg`, `*.gif`, `*.mp4`, `*.zip`, `*.pdf`
- Graphify 결과물 재스캔 방지: `graphify-out/`

이유는 세 가지다.
- 스캔 시간이 줄어든다.
- 문서·PDF·이미지는 LLM 전송 대상이라 비용이 커질 수 있다(6번 참조).
- `graphify-out/`를 팀 공유용으로 커밋할 때, 내부에 100MB를 넘는 파일이 섞이면 GitHub 일반 푸시 제약에 걸릴 수 있다.

예시:

```gitignore
dist/
build/
.next/
coverage/
node_modules/
.cache/
.turbo/
graphify-out/
*.png
*.jpg
*.jpeg
*.gif
*.mp4
*.zip
*.pdf
```

처음에는 넓게 제외하고, "이 파일군도 그래프 질의에 필요하다"는 근거가 생길 때만 다시 포함하는 쪽이 운영상 덜 위험하다.

### 4. 팀원 공유
공식 README 권장은 **`graphify-out/` 자체는 커밋해 팀이 공통 그래프를 공유**하는 방식이다. 다만 전부를 동일하게 다루진 않는다.
- 기본 공유: `graphify-out/` 커밋
- 로컬 전용 권장: `graphify-out/cost.json`
- 선택: `graphify-out/cache/`는 속도를 위해 커밋할 수도 있고, 저장소를 가볍게 유지하려면 제외할 수도 있다

대규모 프로젝트라면 이 권장을 그대로 따르기보다, 먼저 `.graphifyignore`로 입력 집합을 줄여서 **산출물 크기 자체가 커지지 않게** 관리하는 편이 현실적이다. 그래프 산출물에 대용량 이미지·PDF가 섞이면 공유 편의보다 저장소 부담이 더 커질 수 있다.

`/graphify` 스킬 호출은 **사용자별 전역 설치**이므로, 팀원이 직접 graphify를 돌리려면 각자 `graphifyy` 설치 + `graphify install`이 필요하다. 자동 최신화를 원하면 그 상태에서 팀원이 각자 `graphify hook install`을 실행한다.

### 5. 유지보수
재인덱싱은 세 가지 모두 지원한다.
- **수동** — `graphify <path> --update` (변경분만)
- **자동** — `graphify hook install` (**`.git/hooks/`에 post-commit 훅 설치**, git commit 후 재구성, **AST만 → API 비용 없음**)
- **실시간** — `graphify <path> --watch`

### 6. 비용·주의·보안
- **코드는 로컬 처리**(tree-sitter)되어 외부로 나가지 않는다 — "Nothing leaves your machine."
- 단 **문서·PDF·이미지는 의미 추출을 위해 LLM API로 전송된다.**
- 헤드리스(`graphify extract`)는 API 키 필요(`ANTHROPIC_API_KEY` 등) 또는 로컬 Ollama. 코드 전용 corpus는 키 불필요·완전 오프라인.
- 비용은 `graphify-out/cost.json`으로 추적한다.

### 7. 되돌리기
- `graphify uninstall` — 스킬만 제거
- `graphify uninstall --purge` — `graphify-out/` 포함 삭제
- `graphify <platform> uninstall` — 플랫폼별 (예: `graphify claude uninstall`)

### 8. 산출물 위치
**프로젝트 안 산출물은 전부 `graphify-out/` 한 폴더에 격리된다:**
- `graph.html` · `obsidian/` · `wiki/` · `GRAPH_REPORT.md` · `graph.json` · `cost.json` · `cache/`
- git 커밋(공유) vs `.gitignore`(각자)는 4번 참조.

**단, `graphify-out/` 밖에도 흔적이 남는다:**
- 자동 재인덱싱(5번)을 켜면 → `.git/hooks/post-commit`
- 스킬로 설치(2번)하면 → `~/.claude/skills/graphify/SKILL.md` + Claude Code 설정 (프로젝트가 아닌 **머신 레벨**)

### 9. 실행/생명주기
- **CLI·스킬 = one-shot** (돌리고 끝)
- **MCP serve = 상주** (장기 실행 프로세스, 그래프에 계속 질의)

---

## 출처 메모

- 공식 README 기반(https://github.com/safishamsi/graphify, raw 포함, 2026-06-25 확인).
- 3번 `.graphifyignore` **위치만 미확인**(README 미명시). 그 외 칸은 README로 확인.
- `graphify-out/` 내부 구조(obsidian/·wiki/ 포함), `.git/hooks/post-commit`, 스킬 설치 위치(`~/.claude/skills/`)는 raw README 인용 확인.
- 코드 로컬/문서 LLM 전송 구분, `cost.json`, `--purge`는 README 원문 인용 확인.
