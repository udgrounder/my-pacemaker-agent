# changelog — critique_isolation

## 수정 파일

### `.mpa-workspace/inject/layer1_critique.md`
- **변경:** "스레드 선택" 섹션 → "실행 방법 선택" 섹션으로 재구성
  - 1순위: 서브에이전트 (기본 경로, 완전 격리)
  - 2순위: 새 스레드
  - 3순위: 같은 스레드 선언 방식 (독립성 미보장 명시)
- **추가:** 서브에이전트 프롬프트 템플릿 (전달할 파일 목록 + 비평 지시 + 산출물 형식)
- **추가:** 같은 스레드 진행 시 독립성 미보장 경고 명시

### `.mpa-workspace/core/agent_rules.md`
- **변경:** "비평 필요 여부 자동 평가" 권장 메시지 — "새 스레드" → "서브에이전트" (미지원 환경 fallback 명시)
- **변경:** 독립 비평 주의사항 — 새 스레드 강제 → 서브에이전트 우선, 같은 스레드는 최후 수단으로 격하

### `dist/.mpa-workspace/` 동기화
- `inject/layer1_critique.md`, `core/agent_rules.md` 동기화 완료
