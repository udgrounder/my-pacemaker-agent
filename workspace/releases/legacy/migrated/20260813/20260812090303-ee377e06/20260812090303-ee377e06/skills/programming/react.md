# 스킬: React

> React 프로젝트에서 agent가 올바른 패턴을 사용하도록 가이드하는 기술 스킬  
> 사용 시점: Frontend 구현/검토 세션

---

## 버전 / 환경

<!-- 사용 버전 명시. 예: React 18+, TypeScript 5.x, Next.js 14 (App Router) -->

---

## 컴포넌트 설계 원칙

```
UI 컴포넌트   →  표시만. 비즈니스 로직 금지. props로 데이터 받음
컨테이너      →  데이터 페칭 + 상태 관리. UI 최소화
훅            →  로직 재사용 단위. 컴포넌트에서 분리
```

**절대 금지:**
- 컴포넌트 안에서 직접 API 호출 (커스텀 훅 또는 상태 관리 레이어 분리)
- props drilling 3단계 이상 (Context 또는 상태 관리 라이브러리 사용)

---

## 상태 관리

**판단 기준:**
```
로컬 상태 (useState)   →  한 컴포넌트 안에서만 사용
Context               →  트리 내 공유, 자주 바뀌지 않는 것 (테마, 인증 정보)
전역 상태 라이브러리   →  자주 바뀌는 전역 데이터, 복잡한 상태
서버 상태 (React Query) →  API 데이터 (캐싱, 동기화 필요)
```

**모르면 물어볼 것:**
- 이 데이터가 여러 컴포넌트에서 사용되는가?
- 서버 데이터인가, 클라이언트 전용인가?

---

## 훅 규칙

```tsx
// ✅ 커스텀 훅으로 로직 분리
function useUserData(userId: string) {
  const [user, setUser] = useState<User | null>(null);
  // 페칭 로직
  return { user, isLoading, error };
}

// ✅ 컴포넌트는 UI에만 집중
function UserProfile({ userId }: { userId: string }) {
  const { user, isLoading } = useUserData(userId);
  if (isLoading) return <Skeleton />;
  return <div>{user?.name}</div>;
}

// ❌ 컴포넌트 안에서 직접 fetch 금지
function UserProfile({ userId }: { userId: string }) {
  useEffect(() => {
    fetch(`/api/users/${userId}`).then(...); // 금지
  }, []);
}
```

---

## 타입 안전성

```tsx
// ✅ props 타입 명시
interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}

// ❌ any 사용 금지
function process(data: any) { }  // 금지
```

---

## 에러/로딩 처리 방식

```tsx
// ✅ 일관된 에러/로딩 패턴
if (isLoading) return <LoadingSpinner />;
if (error) return <ErrorMessage message={error.message} />;
return <Content data={data} />;
```

**모르면 물어볼 것:**
- 에러 바운더리가 어느 레벨에 있는가?
- 로딩 UI 패턴이 결정되어 있는가? (Skeleton / Spinner)

---

## 함께 쓰는 페르소나

- `personas/implementer.md` — 구현 세션
- `personas/code_reviewer.md` — 검토 세션
