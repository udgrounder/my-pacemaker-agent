# 에이전트 위임과 모델 상한

MPA는 읽기 전용 탐색·검토처럼 분리할 이익이 있는 작업을 위임 후보로 삼는다. 구현은 기존 승인 뒤 전체 작업을 한 수정자에게 순차 인계한다. 자세한 판단과 기존 독립 검토의 실패 처리는 Runtime의 `inject/agent_delegation.md`와 `inject/_agent_execution_priority.md`를 따른다.

## 설치별 정책

선택 파일은 프로젝트의 `.mpa/config/agent_policy.json`이다. 설치와 Runtime 동기화는 이 파일을 생성하거나 수정하지 않는다. 아래 값은 형식 예시이며 이 설치의 실제 모델이나 허용 관계를 나타내지 않는다.

```json
{
  "schema_version": 1,
  "host": "codex",
  "allowed_lower_models": {
    "example-main": {
      "models": ["example-lower"],
      "approval_source": "user",
      "basis": "이 설치에서 사용자가 명시 승인한 관계",
      "confirmed_at": "2026-11-23T09:00:00+09:00"
    }
  }
}
```

`approval_source`는 `user` 또는 `approved_project_policy`다. 관계는 기준 모델에서 직접 허용된 목록만 사용한다. 자기 포함·순환·중복·지원하지 않는 스키마는 거부한다. 정책이 없으면 안전이 확인된 동일 모델 상속이나 메인 직접 처리만 사용한다.

## 판단 도구

`python3 .mpa/runtime/hooks/agent_policy.py inspect`는 표준 입력 JSON의 `host`, `policy`(없으면 null)를 검사한다. `resolve`는 다음 입력으로 한 호출을 판단한다.

| 입력 | 확인할 내용 |
|---|---|
| `context` | `host`, `session`, 호출 대상 `role`, 최초 `initial_revision`, `started_at`, 현재 설정 `revision`, `revision_since`, `as_of`. 설정·역할 또는 모델이 바뀌면 기존 증거를 다시 확인한다. |
| `evidence` | `initial`, `current`, `available`, `resolution` 확인 기록. 각 기록은 `source`, `observed_at`, `host`, `session`, `role`, `revision`, `value`를 담는다. 모든 시각에는 시간대를 포함한다. |
| `policy` | 위 로컬 정책의 내용 또는 null. 도구는 설치 파일을 자동으로 읽거나 작성하지 않는다. |
| `call` | `kind`는 `critique`, `review`, `read`, `design`, `implement` 중 하나. `mode`는 `explicit` 또는 `inherit`. `requested`는 명시 모델 ID 또는 상속 시 null. `permitted`와 `by_main`은 확인된 권한이며, 해당하는 경우 `isolated`, `independent`, `worthwhile`, `sole_writer`, `simple`, `recovery`를 참/거짓으로 전달한다. 명시한 추론 수준은 `reasoning_effort`에 담는다. |
| `budget` | 트리의 `active_optional`, 실제 `free_slots`, 논리 작업의 이미 사용한 `retries_used`. 복구 호출도 회수와 증거 확인 뒤에 판단한다. |
| `running` | 선택 입력. 실행 중 각 호출의 `id`와 실제 `model`을 전달한다. 실제 모델을 확인할 수 없으면 null을 사용한다. |

`initial`과 `current`는 역할 `main`의 모델 ID이며 출처는 `host_session` 또는 `user_window`다. 메인은 최초 모델·확인 시각·세션·최초 revision을 첫 기록에 고정한다. 현재 값으로 그 기록을 교체하지 않는다. 현재 revision의 효력 시각 이후 다시 수집한 증거만 현재 판단에 사용하며 미래 시점의 관계 확인은 거부한다. `available`은 현재 호출 역할의 모델 ID 목록이며 `host_inventory` 또는 `tool_inventory` 증거를 사용한다. `resolution`은 `effective_host_config` 또는 `guaranteed_inheritance` 증거다. 값은 `mode`, `requested`, 해석된 `model`, `settings_supported`, `within_main_effort`와 요청에 해당하면 `reasoning_effort`다. 호출의 추론 설정과 확인 기록이 일치해야 한다. 상속 보장은 상속 경로에만 사용할 수 있다. 문서 예시와 추정한 모델은 확인 기록으로 쓰지 않는다.

결과는 허용 교집합 `allowed`, 가용 교집합 `candidates`, 선호 순서 `preferred`, 실제 입력으로 선택 가능 판정한 `selected`, 이유와 미확인 항목을 담는다. `action`은 `select`, `inherit`, `direct`, `wait` 또는 필수 비평·검증의 기존 실패 경로다. 입력 오류는 종료 코드 2와 `invalid` 결과를 반환한다. `stop_and_mark_unconfirmed`에 나온 실행은 상한을 다시 확인하거나 중단하고 결과를 미확인으로 남긴다.

도구는 전달된 증거의 형식과 일관성을 검사한다. 현재 호스트 모델, 사용자 승인, 설정 우선순위, 동시 실행 수를 직접 확인하거나 호출을 차단하는 기능은 호스트에 있다. 호스트가 반환한 실제 모델 기록이 없으면 모델 실행 결과는 미확인으로 둔다. 도구와 지침 검증 결과만으로 비용·속도 개선이나 하위 모델 운용을 확정하지 않는다.
