# 도메인 지식 라이브러리

여러 프로젝트에서 검증된 도메인 지식을 모아두는 공간이다.  
프로젝트별 규칙(`workspace/memory/domains/`)과 달리 특정 프로젝트에 종속되지 않는다.

---

## 이 폴더에 올라오는 기준

여기에 도달하기까지의 단방향 흐름:

```
1. 발견 시       → workspace/memory/domains/[도메인]/rules.md  (항상)
2. Layer 2 시    → .mpa-workspace/upgrade-candidates/          (후보 평가)
3. 사용자 승인   → .mpa-workspace/knowledge/[도메인].md         (이 폴더)
```

**이 폴더에 있다는 것 = 검증된 범용 도메인 지식이다.** 다른 프로젝트에서 import 가능한 신뢰 등급.

**올라오지 않는 것:**
- 이 프로젝트 코드베이스에만 해당하는 규칙 → `workspace/memory/domains/`
- 기술 스택 관련 지식 → `skills/tech/`
- 미검증 후보 → `.mpa-workspace/upgrade-candidates/` 단계에 머무름

---

## 주의: 이 폴더는 읽기 전용

`.mpa-workspace/`는 업그레이드 시 전체 교체된다. 이 폴더에 직접 파일을 추가하거나 수정하면 다음 업그레이드 때 사라진다.

**승격 흐름:**

1. **발견 시:** 경계 판단 없이 `workspace/memory/domains/[도메인]/rules.md`에 기록
2. **Layer 2 체크포인트:** `domains/` 항목 중 "다른 프로젝트의 의사결정도 바꾸는가?" 통과 항목을 `.mpa-workspace/upgrade-candidates/`에 export
3. **사용자 검토 + 승인:** MPA 시스템 관리자가 검토 후 MPA 시스템의 `dist/.mpa-workspace/knowledge/`에 반영
4. **배포:** 다음 업그레이드 시 모든 프로젝트에 배포

---

## 파일 명명

```
knowledge/
├── payment.md       ← 결제 도메인
├── auth.md          ← 인증/인가 도메인
├── notification.md  ← 알림 도메인
└── ...
```
