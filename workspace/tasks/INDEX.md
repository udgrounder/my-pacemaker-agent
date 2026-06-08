# Tasks INDEX

| 태스크명 | 타입 | 상태 | 요약 | 생성일 | 점검 |
|---------|------|------|------|--------|------|
| 20260604_failure_cost_grade | minor | done | 실패 비용 등급 critical/major/minor 도입 — plan.md 필드, 구현 단계별 행동, 결정 이력 섹션 | 2026-06-04 | ✅ |
| 20260604_critique_file_output | minor | done | 독립 비평 결과 파일 직접 저장 — 메인 에이전트 경유 차단으로 completion bias 제거 | 2026-06-04 | ✅ |
| 20260604_context_routing | minor | done | 태스크 맥락 기반 라우팅(B) + 2단계 진단 질문(C) — 발화 패턴 매칭 의존도 감소 | 2026-06-04 | ✅ |
| 20260604_context_loading | minor | done | 2단계 컨텍스트 선택 로딩 — 태스크 확정 후 필요 파일만 읽도록 I/O 최적화 | 2026-06-04 | ✅ |
| 20260604_mpa_improvements | major | done | MPA 비평 반영 — 게이트/규칙/비평 세션 8개 항목 개선 | 2026-06-04 | ✅ |
| 20260604_zone_differentiation | minor | done | 사용자 개입 등급 Zone 1/2/3 차별화 — 체크포인트 피로 감소 | 2026-06-04 | ✅ |
| 20260604_code_gate_scope | minor | done | 코드 게이트 태스크 범위 강화 — .approved 경로 명시 시 범위 이탈 경고 | 2026-06-04 | ✅ |
| 20260604_critique_isolation | minor | done | 독립 비평 기술적 격리 — 서브에이전트 기본 경로로 격상 | 2026-06-04 | ✅ |
| 20260604_value_decision_criteria | minor | done | 가치 결정 판별 기준 추가 — 2개 판별 질문 + 패턴 예시 | 2026-06-04 | ✅ |
| 20260605_approval-gate-redesign | major | done | .approved 마커 → YAML 프론트매터 + 해시 기반 7단계 게이트 모델로 교체 | 2026-06-05 | ✅ |
| 20260605_install-replace-fix | minor | done | _replace_mpa_section 문자 단위 범위 교체로 재작성 — 섹션 외부 내용 보존 보장 | 2026-06-05 | - |
| 20260605_install-config-verify | minor | done | install.py 업그레이드 시 CLAUDE.md MPA 섹션 내용 비교·자동 갱신 추가 | 2026-06-05 | - |
| 20260605_mpa-system-improvements | major | done | MPA 시스템 평가 기반 14개 항목 개선 — 게이트 강화, minor 경량 흐름, dist/ 자동화 등 | 2026-06-05 | ✅ |
| 20260605_mpa-flow-hardening | major | done | 승인해시 복구 플로우, minor 단순화, 검증 결과 전달 대안 개선 | 2026-06-05 | - |
| 20260605_minor-plan-format | minor | done | minor plan.md에 사용자 결정/에이전트 가정 섹션 추가, 필수 판단 질문 허용 | 2026-06-05 | - |
| 20260605_minor-plan-request-section | minor | done | minor plan.md에 요청 사항·핵심 기능 섹션 추가, 구현 항목 개수 제한 제거 | 2026-06-05 | - |
| 20260605_readme-update | minor | done | README.md 불일치 3개 수정 — approve 원자적 처리, .mpa-workspace 수정 정책, 빠른 참조 표 | 2026-06-05 | - |
| 20260608_guidebook-revision | major | done | guidebook.md 오류 4개 수정·개선 5개 반영 + layer1_critique 고위험 기준 2개 추가 + .approved 파일 삭제 | 2026-06-08 | - |
| 20260608_team-collab-improvements | major | done | inject 우선순위 공통 파일 생성 + .codex hooks 버그 수정 + 가이드북 팀 협업 11장 추가 | 2026-06-08 | - |
| 20260608_workflow-and-planmd-cleanup | major | done | workflows/ 에이전트 라우팅 통합 + 구형 plan.md 20개 YAML 프론트매터 마이그레이션 | 2026-06-08 | - |
| 20260608_minor-major-calibration | major | done | minor 판단 기준 강화(불확실하면 major) + minor 계획서 검토 요청 단계 추가 | 2026-06-08 | - |
| 20260608_routing-notice-improvement | minor | done | 라우팅 고지 형식 개선 — 로드한 파일 전체 명시로 사용자 확인 가능 | 2026-06-08 | - |
| 20260608_codegate-team-limit-doc | minor | done | 가이드북 11.5 추가 — code_gate 팀 협업 한계 및 PR 리뷰가 실제 방어선임을 명시 | 2026-06-08 | - |
| 20260608_team-approval-guideline | minor | done | 가이드북 11.6 추가 — 팀 환경 GATE 1 승인 가이드라인 (major는 타인 검토 권장) | 2026-06-08 | - |
| 20260608_template-readme-update | minor | done | plan_template.md 암묵적 결정 섹션 추가·필수화, minor_plan_template.md 통합, README.md 현행화 | 2026-06-08 | - |
| 20260608_layer1design-template-link | minor | done | layer1_design.md 인라인 계획 형식 제거 → plan_template.md Read 지시로 교체, 에이전트 보고 섹션 신규 필드 반영 | 2026-06-08 | - |
| 20260608_changelog-template-link | minor | done | layer1_implement.md 세션 종료 시 changelog_template.md Read 지시 추가 — 템플릿 단일 소스 원칙 적용 | 2026-06-08 | - |
| 20260608_minor-plan-filepath | minor | done | minor 계획서 제시 형식에 plan.md 파일 경로 추가, 제시 단계 생략 불가 명시 | 2026-06-08 | - |
| 20260608_taskfolder-date-prefix | minor | done | approve·done 이동 경로 예시 yyyymmdd_ 접두사 누락 6곳 일괄 수정 | 2026-06-08 | - |
| 20260608_minor-flow-reorder | minor | done | minor 경량 흐름 순서 수정 — 채팅 계획 제시·승인 후 plan.md 작성으로 변경 | 2026-06-08 | - |
| 20260608_minor-completion-gate | minor | done | minor 자동 완료 제거 — 구현 보고 후 사용자 확인 받아 done 처리로 변경 | 2026-06-08 | - |
| 20260608_plan-review-surface | minor | done | 계획서 제시 형식에 조용한 결정·반례 항목 추가 — GATE 1 전 사용자 명시적 검토 | 2026-06-08 | - |
| 20260608_counterarg-solution-routing | minor | done | 반례 해결책 유무 구분 — 있으면 구현 항목 추가·고지, 없으면 사용자 논의 | 2026-06-08 | - |

| 20260608_agent-rules-refinement | major | done | 실패 비용 추정 단일 소스화 + Layer 2 트리거 명확화 + agent_rules.md detail 이동 경량화 | 2026-06-08 | - |

[Layer 2 완료] 2026-06-04
[Layer 2 완료] 2026-06-05
