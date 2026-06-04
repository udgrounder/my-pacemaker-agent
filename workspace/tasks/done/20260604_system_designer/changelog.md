# Changelog — MPA 파일 수정 거버넌스 (문제 8)

## 신규 파일

### `dist/.mpa-workspace/personas/system_designer.md`
- MPA 설계자 페르소나 신규 생성
- Task Designer와의 차이 테이블 (코드 게이트 미적용, 영향 범위, 비평 방식)
- 변경 전/후 역할 규칙 정의
- LLM 편향 경고 (충돌 간과, 소스 코드와 혼동, 용어 임의 생성)

## 수정 파일

### `dist/.mpa-workspace/core/agent_rules.md`
- 라우팅 테이블: "MPA 파일 수정" 항목 신규 추가 (규칙 바꿔줘, inject 수정, 페르소나 수정 등)
- 라우팅 테이블: "체계 업데이트" → "MPA 업데이트" + "새 버전 설치"로 구체화
- "MPA 파일 수정 규칙" 섹션 신규 추가:
  - 소스 코드 수정과의 차이 테이블 (코드 게이트 미적용 명시)
  - 비평: 새 스레드 원칙 / 환경 미지원 시 같은 스레드 허용
  - 6단계 처리 흐름 (페르소나 로드 → 참조 파일 읽기 → plan → 비평 → 수정 → 동기화)
- 용어 통일: "체계 개선 후보" → "MPA 개선 후보", "체계 첫 적용" → "MPA 첫 적용"

### `dist/.mpa-workspace/inject/layer1_critique.md`
- "체계 개선 후보" → "MPA 개선 후보" 용어 통일

## 추가 수정 (파일명 변경)

- `personas/system_designer.md` → `personas/mpa_system_designer.md` (일반 시스템 설계자와 충돌 방지)
- `agent_rules.md` 참조 경로 동일하게 업데이트

## 추가 수정 (용어 재변경)

사용자 요청으로 "MPA" → "MPA 시스템" 전면 교체:
- `system_designer.md`: "MPA 설계자" → "MPA 시스템 설계자", "MPA 파일" → "MPA 시스템 파일"
- `agent_rules.md`: "MPA 개선 후보" → "MPA 시스템 개선 후보", "MPA 파일 수정 규칙" → "MPA 시스템 파일 수정 규칙" 등 전체
- `layer1_critique.md`: "MPA 개선 후보" → "MPA 시스템 개선 후보"
