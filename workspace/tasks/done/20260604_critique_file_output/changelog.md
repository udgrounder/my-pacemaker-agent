# Changelog

## 수정된 파일

### `.mpa-workspace/inject/layer1_critique.md`
- 서브에이전트 프롬프트 템플릿 끝에 "저장 지시" 블록 추가
  - 비평 결과를 채팅이 아닌 critique.md에 Write 도구로 직접 저장
  - 반환값: "저장 완료: [경로]" 또는 "저장 실패: [오류]"
- "세션 종료 시" 수정
  - 기존: 비평 결과를 사용자에게 제시
  - 변경: critique.md 저장 + 메인 에이전트에 경로만 반환

### `.mpa-workspace/core/agent_rules.md`
- "비평 필요 여부 자동 평가" 섹션에 "비평 완료 후 메인 에이전트 처리" 블록 추가
  - 메인 에이전트는 critique.md를 읽거나 요약하지 않음 (completion bias 차단)
  - 사용자에게 파일 경로만 안내
  - 저장 실패 시에만 예외적으로 내용 전달

### `dist/` 동기화
- 위 2개 파일 동기화 완료
