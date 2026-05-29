# 스킬: Python (FastAPI / Django)

> Python 기반 백엔드 프로젝트에서 agent가 올바른 패턴을 사용하도록 가이드하는 기술 스킬  
> 사용 시점: Backend 구현/검토 세션

---

## 버전 / 환경

<!-- 사용 버전 명시. 예: Python 3.11+, FastAPI 0.100+, SQLAlchemy 2.x -->

---

## FastAPI 패턴

### 의존성 주입

```python
# ✅ Depends로 의존성 주입
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

@router.get("/items")
async def get_items(db: AsyncSession = Depends(get_db)):
    ...

# ❌ 전역 세션 사용 금지
db = SessionLocal()  # 금지
```

### 요청/응답 스키마

```python
# ✅ Pydantic 모델로 요청/응답 분리
class ItemCreate(BaseModel):   # 요청
    name: str
    price: float

class ItemResponse(BaseModel): # 응답
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

# ❌ ORM 모델 직접 반환 금지
@router.get("/items")
async def get_items() -> list[Item]:  # SQLAlchemy 모델 직접 반환 금지
```

---

## 예외 처리

```python
# ✅ HTTPException 또는 커스텀 예외 + 핸들러
@app.exception_handler(BusinessException)
async def business_exception_handler(request, exc: BusinessException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.message})

# ❌ 각 엔드포인트마다 try-except 금지 (공통 처리 우선)
```

**모르면 물어볼 것:**
- 에러 응답 형식이 결정되어 있는가?
- HTTP 상태코드 매핑 기준이 있는가?

---

## 비동기 처리

```python
# ✅ I/O 바운드 작업은 async
async def fetch_user(user_id: int) -> User:
    return await db.get(User, user_id)

# ✅ CPU 바운드 작업은 별도 스레드풀
import asyncio
result = await asyncio.to_thread(cpu_intensive_task, data)

# ❌ async 함수 안에서 blocking 호출 금지
async def bad():
    time.sleep(1)         # 금지 — await asyncio.sleep(1) 사용
    requests.get(url)     # 금지 — httpx.AsyncClient 사용
```

---

## 타입 힌트

```python
# ✅ 모든 함수에 타입 힌트 필수
def create_user(name: str, age: int) -> User:
    ...

# ✅ Optional 대신 X | None (Python 3.10+)
def get_user(user_id: int) -> User | None:
    ...
```

---

## 모르면 먼저 물어볼 것

- 동기/비동기 중 어떤 방식을 쓰는가?
- ORM: SQLAlchemy / Tortoise ORM / 기타?
- 소프트 삭제 여부

---

## 함께 쓰는 페르소나

- `personas/implementer.md` — 구현 세션
- `personas/code_reviewer.md` — 검토 세션
