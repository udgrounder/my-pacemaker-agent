# 스킬: Spring Boot

> Spring Boot 프로젝트에서 agent가 올바른 패턴을 사용하도록 가이드하는 기술 스킬  
> 사용 시점: Backend 구현/검토 세션

---

## 버전 / 환경

- **Spring Boot 3.x** (Java 17+ LTS)
- 빌드: Gradle

> 버전 미명시 기술 스킬은 불완전하다 — 버전별 API·기본값 차이가 크기 때문이다.
> 위는 예시 baseline이며, 실제 프로젝트에서는 사용하는 정확한 버전(예: 3.4.1)으로 고정한다.

---

## 레이어 책임 원칙

```
Controller  →  요청/응답 변환만. 비즈니스 로직 금지
Service     →  비즈니스 로직. 트랜잭션 경계
Repository  →  DB 접근만. 쿼리 로직 포함 가능
```

**절대 금지:**
- Controller에서 `@Transactional` 사용
- Service에서 직접 DB 접근 (Repository 우회)
- Repository에서 다른 Repository 호출

---

## 트랜잭션 관리

```java
// ✅ Service 레이어에서만
@Service
public class OrderService {
    @Transactional
    public void createOrder(...) { }

    @Transactional(readOnly = true)  // 조회는 readOnly
    public Order getOrder(...) { }
}

// ❌ Controller에서 금지
@RestController
public class OrderController {
    @Transactional  // 금지
    public ResponseEntity<?> createOrder(...) { }
}
```

---

## 예외 처리

```java
// ✅ GlobalExceptionHandler 중앙화
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<?> handleBusinessException(BusinessException e) { }
}

// ❌ Controller마다 try-catch 금지
```

**모르면 물어볼 것:**
- 이 예외를 클라이언트에 노출해도 되는가?
- HTTP 상태코드 매핑이 정의되어 있는가?

---

## DTO / Entity 분리

```
Entity      →  DB 매핑 전용. API 응답에 직접 사용 금지
DTO         →  API 요청/응답 전용
Mapper      →  Entity ↔ DTO 변환
```

**절대 금지:**
- Entity를 Controller 응답으로 직접 반환 (순환 참조, 필드 노출 위험)
- DTO에 `@Entity` 혼용

---

## JPA 주의사항

**N+1 문제:**
```java
// ❌ N+1 발생
List<Order> orders = orderRepository.findAll();
orders.forEach(o -> o.getItems().size()); // lazy loading N번

// ✅ fetch join 사용
@Query("SELECT o FROM Order o JOIN FETCH o.items")
List<Order> findAllWithItems();
```

**모르면 물어볼 것:**
- 연관관계 로딩 전략이 결정되어 있는가? (Lazy/Eager)
- 소프트 삭제 여부 (deleted_at 컬럼 사용 여부)

---

## 테스트

```
@SpringBootTest    →  통합 테스트 (느림, 필요한 경우만)
@WebMvcTest        →  Controller 단위 테스트
@DataJpaTest       →  Repository 테스트
단위 테스트 (Mockito) →  Service 로직 테스트 (기본)
```

---

## 함께 쓰는 페르소나

- `personas/implementer.md` — 구현 세션
- `personas/code_reviewer.md` — 검토 세션
