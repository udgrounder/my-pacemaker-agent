# 태스크 완료 문서 기본 저장 위치를 workspace/docs/ → docs/로 변경

**타입**: 방법론 개선
**발견 상황**: 사용자 요청으로 `workspace/docs/`(MPA 태스크 완료 시 생성된 운영매뉴얼 4개 + INDEX.md)를 프로젝트 최상위 `docs/`로 통합하는 작업 중 발견. 최상위 `docs/`는 이 프로젝트에 이미 존재하던 별도의 문서 저장소(01-standards/, 02-spec/, sql/, brainstorming/, interviews/, workspace/)이고, MPA 방법론은 이를 모른 채 `workspace/docs/`를 독자적인 기본 위치로 가정하고 있었음. 그 결과 프로젝트 문서가 두 곳으로 분산됨.
**적용 범위**: 이 프로젝트 (campingtalk-proj) — 프로젝트마다 기존 docs 관례가 다를 수 있어 "모든 프로젝트" 일반화는 보류.

## 현재 방식

`.mpa-workspace/templates/docs_template.md`, `core/agent_rules.md`, `inject/layer1_design.md`, `inject/layer1_implement.md`, `inject/layer2_checkpoint.md`가 모두 태스크 완료 문서의 저장 위치를 `workspace/docs/[경로]/[파일명].md` + `workspace/docs/INDEX.md` 등록으로 하드코딩하고 있음. 이번에 4개 운영매뉴얼 파일과 INDEX.md 내용을 `docs/운영매뉴얼/`, `docs/INDEX.md`로 수동 이전했지만, 방법론 파일 자체는 손대지 않아 다음 태스크 완료 시 다시 `workspace/docs/`에 새 문서를 생성하게 됨 — 분산이 재발할 것.

## 개선 방안

이 프로젝트에서는 문서 기본 위치를 최상위 `docs/`로 변경한다 (기존 `docs/`가 이미 프로젝트의 문서 저장소로 쓰이고 있으므로). 구체적으로:
- `docs_template.md`의 "복사 위치: workspace/docs/..." → "docs/..."로 변경
- `core/agent_rules.md`, `inject/layer1_design.md`, `inject/layer1_implement.md`, `inject/layer2_checkpoint.md` 내 `workspace/docs` 언급을 `docs`로 일괄 변경
- MPA 태스크 완료 문서는 최상위 `docs/INDEX.md`의 "운영매뉴얼/ (운영 가이드 — MPA 태스크 완료 문서)" 섹션에 등록하도록 안내 문구 조정
- 처리 절차는 "MPA 파일 수정 세부"(agent_rules_detail.md) 절차를 따른다 — mpa_system_designer 페르소나로 plan.md 작성·승인 후 적용하고, `prepare-release`가 dist 동기화와 단일 release ID 생성을 처리한다.

## 적용 대상 파일

- `.mpa-workspace/templates/docs_template.md`
- `.mpa-workspace/core/agent_rules.md`
- `.mpa-workspace/inject/layer1_design.md`
- `.mpa-workspace/inject/layer1_implement.md`
- `.mpa-workspace/inject/layer2_checkpoint.md`
