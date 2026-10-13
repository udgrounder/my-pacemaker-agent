# 독립 코드 리뷰 — 2026-10-13

결론: **수정 필요 — P2 2건**. 정상·오류 처리 테스트는 통과하지만 외부 편집과 경합할 때 사용자 증빙을 잃거나 승인 이력 없이 새 해시만 저장한 뒤 성공으로 처리한다.

## 검토 기준과 범위

- 기준: 같은 폴더 `plan.md`의 현재 요구사항과 운영 계약. 계획에 명시된 저장 오류의 원복/복구 근거 유지 및 외부 편집 보존을 기준으로 검토했다.
- 미커밋 변경: `.mpa/runtime/hooks/plan_hash.py`, `.mpa/runtime/hooks/code_gate.py`, `tests/test_plan_hash.py`.
- AGENTS, MAP_PRODUCT_RULES, core 규칙과 코드 탐색 상세, `personas/code_reviewer.md`, engineering code-review skill을 확인했다.
- 기존 critique/review 파일, changelog 및 구현 대화를 읽지 않았다. 구현·테스트 파일을 수정하지 않았다.
- `dist/.mpa/runtime/hooks/plan_hash.py`, `code_gate.py`는 source와 바이트 일치만 확인했다.

## P2-1 — 검사와 실제 교체/원복 사이의 외부 편집을 덮어쓴다

**위치:** `/Users/kjkim/Study/my-pacemaker-agent/.mpa/runtime/hooks/plan_hash.py:259-262`.

`write_approval_pair`는 plan의 내용이 원본과 같은지 검사한 다음 `write_plan`을 호출하지만, `atomic_write`의 최종 `os.replace`는 대상의 예상 버전을 확인하지 않는다. 검사 이후 또는 임시 파일 작성 중에 외부 편집기가 저장하면 그 내용을 승인 갱신의 오래된 스냅샷으로 덮는다. changelog 최초 저장과 원복에도 같은 검사/교체 간격이 있다. 특히 원복의 `272-276`은 예상 작성본을 읽은 뒤 외부 편집이 들어와도 원본으로 덮고 journal을 삭제한다.

**발생 조건:** 새 배치 renew-spec 도중 검사와 교체 사이에 다른 writer가 plan/changelog를 저장한다. journal은 renew-spec끼리의 독점 생성만 제공하며 외부 편집기는 이 잠금에 참여하지 않는다.

**실제 영향:** 사용자 검증 실패 증빙 또는 이력 편집이 유실된다. 성공 경로는 성공 반환과 함께 journal을 없애며 audit도 정상이다. 원복 경로에서는 외부 변경을 잃었는데도 “기존 승인해시와 이력을 보존했습니다”라고 보고한다.

**재현 근거:** 임시 디렉터리의 실제 plan/changelog에 실제 `atomic_write`를 실행했다. `os.replace`의 호출 직전에 plan에 외부 검증 실패 증빙을 저장하도록 실행 순서만 제어한 뒤 원래 `os.replace`를 실행했다. 별도로 plan 저장을 OSError로 실패시키고 두 번째 `atomic_write`(changelog 원복) 직전에 외부 이력 편집을 저장했다.

구체적 삽입점은 정상 경로의 `259-262` 검사가 끝난 다음 `atomic_write` 내부 `188`의 plan replace 직전이며, 원복 경로는 `272`의 `current == new_history` 판단 이후 `276`의 원복 writer 진입점이다. 기대 결과는 외부 편집 보존과 충돌/복구 보고이고, 실제 결과는 편집 유실과 journal 삭제다. “외부 변경은 자동으로 덮지 않는다”는 `write_approval_pair`의 `235` 계약 및 기준 계획의 외부 편집 보존 설명과 직접 충돌한다.

```text
R1 plan external evidence preserved: False
R1 journal remains: False
R1 audit invalid: []
R3 error: 승인 갱신 실패; 기존 승인해시와 이력을 보존했습니다 (계획 저장 실패)
R3 external history preserved: False
R3 journal remains: False
```

**수정 방향:** 정상 저장과 원복 모두 실제 교체의 충돌 처리까지 설계해야 한다. 모든 지원 writer가 참여하는 잠금/버전 계약을 적용하거나 교체되는 이전 파일을 보존하여 충돌 시 복구할 수 있어야 한다. 읽기 비교만으로 임의 외부 writer와 무손실을 보장할 수 없으며, 외부 편집을 지원하지 않는 한계가 있다면 그 범위를 명시하고 복구 근거를 섣불리 삭제하지 않아야 한다.

## P2-2 — 최종 changelog 상태를 확인하지 않고 성공 처리한다

**위치:** `/Users/kjkim/Study/my-pacemaker-agent/.mpa/runtime/hooks/plan_hash.py:283-284`.

changelog 저장 후 plan을 저장하는 동안 changelog가 변경되더라도 성공 경로는 두 파일이 journal의 예상 작성본과 일치하는지 확인하지 않고 journal을 삭제한다. plan에는 새 승인해시가 기록되지만 changelog에는 해당 승인행이 없는 상태가 정상 성공으로 처리된다. 이는 P2-1의 외부 편집 덮어쓰기와 별개로, 외부 편집 자체를 보존해도 승인 쌍의 불일치를 탐지하지 못하는 문제다.

**발생 조건:** `atomic_write(history_path, new_history)`가 끝난 이후부터 journal 삭제 이전 사이에 외부 writer가 이전 스냅샷에 기반한 changelog를 저장하거나 승인행을 제거한다.

**실제 영향:** 새 승인해시의 이전/새 체크섬·변경 요약 추적이 끊어진다. journal이 없어 check/audit/gate의 복구 탐지가 작동하지 않는다. 새 hash만으로 구현이 진행될 수 있다.

**재현 근거:** 실제 changelog 저장은 그대로 실행했다. `write_plan` 직전에 외부 편집으로 changelog를 다른 내용으로 저장한 뒤 원래 `write_plan`을 실행했다. 외부 내용은 유지됐지만 승인행 없이 renew-spec이 성공했고 audit도 정상으로 반환했다.

삽입점은 `258` 이력 저장과 `259-261` plan 원본 검사 이후 `262`의 writer 진입점이다. 기대 결과는 두 파일 불일치 탐지·journal 보존·복구 필요 실패이며, 실제 결과는 성공 반환·승인행 부재·journal 삭제다. 계획 완료 기준의 “승인해시와 이력이 어긋나면 실패로 처리하고 원복하거나 복구 근거를 남긴다”를 위반한다.

```text
R2 returned success: True
R2 approval row preserved: False
R2 journal remains: False
R2 audit invalid: []
```

**수정 방향:** journal을 지우기 전에 plan/changelog를 예상 작성본과 대조하고, 차이가 있으면 외부 파일을 보존한 채 journal을 유지하며 복구 필요를 반환한다. 최종 확인과 삭제 사이의 경합 역시 P2-1의 writer 조정 계약을 따라야 한다.

## 확인 결과와 테스트 사각지대

- `python3 -m unittest discover -s tests -p test_plan_hash.py`: **43개 통과**.
- source/dist의 위 두 Runtime 파일: **바이트 일치**.
- 임시 재현 스크립트: `/private/tmp/mpa_independent_review_repro.py`. 실행: `python3 /private/tmp/mpa_independent_review_repro.py`. 입력은 유효한 reqspec-v1 기존 hash, 구현 중 상태, 새 요구사항 명세 및 기존 changelog이다. 구현 함수와 원자 교체는 실제 코드를 실행하고 외부 편집 타이밍만 mock으로 고정했다.
- 기존 테스트는 원복 전에 이미 달라진 changelog와 잠금 획득 전에 오래된 스냅샷을 검사한다. 마지막 검사 이후 실제 replace/원복 직전 편집, 이력 커밋 이후 plan 커밋 사이 편집은 검사하지 않는다.
- summary 공백·표 구분자/줄바꿈, hash 형식·상태, 중복/위치 오류, 새/기존 배치, 저장 실패·중단·journal 정리 실패 및 gate 연결을 검토했다. 위 재현 외에 새로운 actionable finding은 확정하지 않았다.
- 실제 전원 손실 및 파일시스템의 영속성 순서는 재현하지 않았다. 이 보고서는 프로세스 실행 중 실제 파일 저장과 결정적으로 제어한 경합에 한정한다.

정정 회고: 없음.
