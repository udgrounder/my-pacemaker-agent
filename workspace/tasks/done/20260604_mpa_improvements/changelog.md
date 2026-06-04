# Changelog — MPA 시스템 비평 반영 개선

## 수정 파일

### `.mpa-workspace/hooks/session_start.py`
- `build_message()`: active 태스크가 2개 이상일 때 분기 추가
  - 단일 태스크: 기존 동작 유지
  - 다중 태스크: 태스크 수 표시 + "작업할 태스크를 선택해 주세요" 안내 + 선택 후 흐름 안내

### `.mpa-workspace/core/agent_rules.md`
- **세션 시작 루틴 §1:** `active/` 폴더를 primary source로 명시, INDEX.md를 cache로 명시
  - INDEX.md 동기화 원칙 추가: 전체 재동기화 금지, 누락 탐지만, 업데이트 시점 명시
- **라우팅 표:** 패턴 추가 및 보완
  - 버그: "~작동 안 해" 추가
  - 리팩터링: "~더 낫게" 추가
  - 성능 패턴 신규: "느려", "성능", "느린데", "응답이 오래 걸려" → 케이스 α-성능
- **케이스 α-성능 신규:** 성능·느림 발화 전용 분기 질문 추가

### `.mpa-workspace/inject/layer1_critique.md`
- 도입부 "새 스레드 필수" 단언 → "스레드 선택" 표로 교체
  - 새 스레드 가능 시: 기존대로 새 스레드
  - 새 스레드 불가 시: 같은 스레드 허용 + 3가지 제약 명시 (선언, plan.md만 읽기, 이유 무시)
  - 왜 새 스레드인지 이유 명시 (completion bias)

### `workspace/project_rules.md` (이 프로젝트 전용)
- **upgrade-candidates 처리 워크플로우 섹션 신규 추가**
  - 타입 A(방법론): MPA 시스템 파일 수정 태스크로 등록
  - 타입 B(도메인 지식): knowledge/ 직접 반영
  - 완료 후 해당 파일 삭제 + dist/ 동기화

## dist/ 동기화 완료
- `dist/.mpa-workspace/hooks/session_start.py`
- `dist/.mpa-workspace/core/agent_rules.md`
- `dist/.mpa-workspace/inject/layer1_critique.md`
