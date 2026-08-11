# MPA 규칙의 TOML 기반 외부 에이전트 참조 형식

**타입**: 방법론 개선

**발견 상황**: 현재 MPA 규칙이 Markdown 문서로만 존재하여 다른 AI 에이전트가 프로그래매틱하게 참조하거나 자동화 도구가 파싱하기 어려운 상황에서 발견됨

**적용 범위**: 이 프로젝트 및 모든 MPA 채택 프로젝트

---

## 현재 방식

MPA 규칙이 다음과 같이 분산되어 있다:

- `.mpa-workspace/core/agent_rules.md` — 핵심 규칙 (Markdown)
- `.mpa-workspace/core/agent_rules_detail.md` — 상세 가이드 (Markdown)
- `CLAUDE.md` — 프로젝트 지시사항 (Markdown)
- `.claude/CLAUDE.md` — 사용자 정의사항 (Markdown)

**문제점:**
1. **외부 에이전트 통합 어려움** — 다른 AI 에이전트가 MPA 규칙을 자동으로 파싱하고 따르기 어렵다
2. **프로그래매틱 참조 불가** — 라우팅 테이블, 워크플로우 단계, 승인 프로세스 등을 코드에서 직접 접근 불가
3. **정책 변경 시 다중 파일 수정** — 규칙을 변경하면 여러 문서를 일일이 갱신해야 한다
4. **자동화 도구 개발 불가능** — config 파일이 없으면 MPA 자동화(linting, 검증, 제안 생성)를 구현할 수 없다

---

## 개선 방안

TOML 기반 단일 소스 설정 파일 도입:

```
.mpa-workspace/config.toml
├─ [mpa]                          # 메타데이터
├─ [workflow.major]               # 7단계 워크플로우
├─ [workflow.minor]               # 3단계 워크플로우
├─ [routing]                      # 요청 타입 라우팅 테이블
├─ [approval]                     # 승인 프로세스 & 해시 검증
├─ [memory]                       # 메모리 시스템 (workspace/session)
├─ [task.*]                       # 태스크 생명주기
├─ [zones]                        # 사용자 개입 강도
├─ [code_gate]                    # 소스 수정 게이트
├─ [context]                      # 컨텍스트 선택 로딩
├─ [paths]                        # 파일 경로 패턴
├─ [index_maintenance]            # INDEX.md 유지보수
├─ [exploration]                  # 탐색·토론 모드
├─ [upgrade_candidates]           # 개선 후보 관리
├─ [session.*]                    # 세션 시작·종료
├─ [tools]                        # 도구 명령 (plan_hash, code_gate)
└─ [detailed_guides]              # 트리거별 상세 문서 참조맵
```

**장점:**
1. **구조화된 참조** — 라우팅 테이블, 워크플로우, 게이트를 프로그래매틱하게 접근 가능
2. **외부 에이전트 통합** — Python, Node.js, Go 등 언어에서 toml 라이브러리로 쉽게 로드 가능
3. **자동화 도구 기반** — linting, 규칙 검증, CLI 자동 생성 등 가능
4. **단일 소스** — 정책 변경 시 config.toml만 갱신하면 모든 에이전트에 즉시 반영
5. **버전 관리** — `[mpa]` 섹션의 `version`으로 MPA 버전 추적 가능

---

## 구현 세부사항

### 1. config.toml 파일 생성

위치: `.mpa-workspace/config.toml`

주요 섹션:
- **[mpa]** — 이름, 버전, 설명
- **[workflow.major/minor]** — 단계 모델, 게이트 정의
- **[routing]** — 요청 타입별 라우팅 (explicit_keywords, workflows)
- **[approval]** — 계획 승인, 완료 승인, 해시 검증
- **[memory]** — workspace/session 우선순위
- **[task.creation/completion/structure]** — 태스크 생명주기
- **[code_gate]** — 소스 수정 제약 조건
- **[session.startup/closure]** — 세션 루틴
- **[detailed_guides]** — 트리거별 가이드 맵

### 2. 기존 Markdown 문서와의 관계

TOML은 **참조용 구조화 설정**이고, 상세 내용은 여전히 Markdown에 있다:

```
config.toml (구조 + 주요 내용)
    ↓
agent_rules.md (개요, 라우팅 표, 단계 모델)
    ↓
agent_rules_detail.md (트리거별 상세 절차)
```

TOML에서 `[detailed_guides]` 섹션이 각 트리거를 상세 문서로 매핑한다:

```toml
[detailed_guides]
frontmatter_missing_handling = "agent_rules_detail.md: 프론트매터 누락 처리"
plan_approval_reverification = "agent_rules_detail.md: 계획 승인 재확인"
task_resumption = "agent_rules_detail.md: 태스크 재개"
```

### 3. 외부 에이전트 통합 패턴

**Python 예시:**
```python
import toml

config = toml.load('.mpa-workspace/config.toml')

# 라우팅 판단
if user_input in config['routing']['explicit_keywords']['bug']:
    task_type = 'bug_fix'
    workflow = config['routing']['workflows'][task_type]
    print(f"→ {task_type}: {workflow['file']}")

# 워크플로우 단계 확인
current_state = '구현 중'
allowed_states = config['code_gate']['allow_in_states']
if current_state in allowed_states:
    print("✓ 소스 수정 허용")
else:
    print("✗ 소스 수정 차단")
```

**YAML 변환 (필요 시):**
```bash
# Python로 TOML → YAML 변환 가능
pip install toml pyyaml
python -c "import toml, yaml; print(yaml.dump(toml.load('.mpa-workspace/config.toml')))"
```

### 4. CI/CD 자동화 예시

```bash
# 규칙 검증
./scripts/validate_mpa_config.sh .mpa-workspace/config.toml

# 에이전트 규칙 변경 감지
git diff .mpa-workspace/config.toml | grep -E "^\+" | ./scripts/notify_agent_updates.sh
```

---

## 적용 대상 파일

- `.mpa-workspace/config.toml` (신규 파일)
- `.mpa-workspace/core/agent_rules.md` (참조 추가: "config.toml로도 구조화된 참조 가능")
- `.mpa-workspace/core/agent_rules_detail.md` (트리거 섹션 상단에 config.toml 경로 링크)
- `CLAUDE.md` (graphify 다음으로 "config.toml 참조" 안내)

---

## 마이그레이션 계획

| 단계 | 작업 | 대상 |
|------|------|------|
| 1 | config.toml 생성 | 이 프로젝트 |
| 2 | Markdown 문서에서 TOML 링크 추가 | agent_rules.md, agent_rules_detail.md |
| 3 | 외부 에이전트 통합 테스트 | 대형 멀티 에이전트 워크플로우 |
| 4 | CI/CD 규칙 검증 자동화 | git hooks, pre-commit |
| 5 | MPA 템플릿 업데이트 | 모든 프로젝트 신규 초기화 시 config.toml 포함 |

---

## 예상 효과

- 🔄 **외부 에이전트 통합**: 다른 AI 시스템이 MPA 규칙을 자동으로 따를 수 있음
- 🤖 **자동화 강화**: 라우팅, 검증, 알림 등 자동화 도구 개발 가능
- 📦 **버전 관리**: `config.toml` 버전으로 MPA 진화 추적
- 🧪 **테스트 용이**: 규칙을 코드에서 쉽게 검증
- 📚 **문서화 개선**: 구조화된 형식으로 규칙이 자가 설명적
