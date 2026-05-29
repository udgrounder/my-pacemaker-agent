# 스킬: Node.js / TypeScript

> Node.js + TypeScript 기반 프로젝트에서 agent가 올바른 패턴을 사용하도록 가이드  
> 사용 시점: Backend/Fullstack 구현/검토 세션

---

## 버전 / 환경

<!-- 사용 버전 명시. 예: Node.js 20 LTS, TypeScript 5.x, Express / Fastify / NestJS -->

---

## 타입 안전성

```typescript
// ✅ 명시적 타입 선언
interface User {
  id: string;
  email: string;
  createdAt: Date;
}

async function getUser(id: string): Promise<User | null> { }

// ❌ any 사용 금지
function process(data: any) { }  // 금지

// ❌ as 타입 단언 남용 금지 (타입 오류를 숨김)
const user = data as User;  // 검증 없이 단언 금지
```

---

## 비동기 처리

```typescript
// ✅ async/await 일관 사용
async function createUser(dto: CreateUserDto): Promise<User> {
  const user = await userRepository.save(dto);
  return user;
}

// ❌ Promise 체이닝과 async/await 혼용 금지
async function bad() {
  return getUserById(id).then(user => {  // 혼용 금지
    return user;
  });
}

// ✅ 에러는 try/catch 또는 중앙 핸들러
async function handler(req, res) {
  try {
    const result = await service.execute();
    res.json(result);
  } catch (error) {
    next(error);  // 중앙 에러 핸들러로 위임
  }
}
```

---

## 모듈 구조

```
// ✅ 책임 분리
controller.ts   → 요청/응답 변환
service.ts      → 비즈니스 로직
repository.ts   → 데이터 접근
types.ts        → 타입 정의 (공유)

// ❌ 한 파일에 모든 로직 금지
// ❌ 파일 간 순환 참조 금지
```

---

## 환경변수

```typescript
// ✅ 환경변수 중앙 관리 + 검증
// config.ts
export const config = {
  dbUrl: process.env.DATABASE_URL ?? (() => { throw new Error('DATABASE_URL required') })(),
  port: Number(process.env.PORT ?? 3000),
};

// ❌ 코드 곳곳에서 직접 접근 금지
const url = process.env.DATABASE_URL;  // 분산 금지
```

---

## 에러 처리

```typescript
// ✅ 커스텀 에러 클래스
class AppError extends Error {
  constructor(public statusCode: number, message: string) {
    super(message);
  }
}

// ✅ 중앙 에러 핸들러 (Express 기준)
app.use((err: Error, req, res, next) => {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({ error: err.message });
  }
  res.status(500).json({ error: 'Internal Server Error' });
  // 상세 에러는 외부 노출 금지
});
```

**모르면 먼저 물어볼 것:**
- 에러 응답 포맷이 결정되어 있는가?
- 로깅 전략은 무엇인가? (console.log vs 전용 라이브러리)

---

## 절대 금지

- `any` 타입 사용 (타입 검증 우회)
- `process.env.*` 코드 곳곳에서 직접 접근 (중앙 config 사용)
- 비동기 에러를 catch 없이 방치 (unhandled rejection)
- 민감 정보 (비밀번호, 토큰) 로그 출력

---

## 함께 쓰는 페르소나

- `personas/implementer.md` — 구현 세션
- `personas/code_reviewer.md` — 검토 세션
