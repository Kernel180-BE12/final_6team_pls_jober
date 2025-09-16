# JWT 인증 시스템 문제 해결 및 구현 상세

## 📋 발생한 문제들

### 1. .env 파일 JWT_SECRET 중복 키 문제
**문제**: `back/.env` 파일에서 `JWT_SECRET=JWT_SECRET=beb305030e21a9a32e1b77bc685749ac` 형태로 키가 중복 정의됨
**증상**: 환경변수가 제대로 로드되지 않아 JWT 토큰 생성 시 기본값 사용

### 2. JWT 라이브러리 API 호환성 문제
**문제**: `JwtUtil.java`에서 JWT Claims 객체를 immutable 상태에서 수정하려 시도
**증상**: 
```
java.lang.UnsupportedOperationException: JWT Claims instance is immutable and may not be modified.
at com.example.util.JwtUtil.createAccessToken(JwtUtil.java:32)
```

### 3. Spring Security 필터 설정 문제
**문제**: JWT 필터가 `/api/auth/login` 경로에도 적용되어 로그인 자체가 차단됨
**증상**: 로그인 요청 시 "인증이 필요합니다" 오류 발생

## 🔧 해결 과정

### 1단계: .env 파일 수정
```bash
# 수정 전
JWT_SECRET=JWT_SECRET=beb305030e21a9a32e1b77bc685749ac

# 수정 후  
JWT_SECRET=beb305030e21a9a32e1b77bc685749ac
```

### 2단계: JWT 토큰 생성 API 수정
**기존 코드 (문제 있던 버전):**
```java
public String createAccessToken(String email, String role, Long accountId) {
    Claims claims = Jwts.claims().subject(email).build(); // immutable 객체 생성
    claims.put("role", role);                             // 수정 시도 -> 오류!
    claims.put("accountId", accountId);
    // ...
}
```

**수정된 코드:**
```java
public String createAccessToken(String email, String role, Long accountId) {
    Date now = new Date();
    Date validity = new Date(now.getTime() + accessTokenValidityInMilliseconds);

    return Jwts.builder()
            .subject(email)                    // 빌더 패턴 사용
            .claim("role", role)               // 체이닝으로 클레임 추가
            .claim("accountId", accountId)
            .issuedAt(now)
            .expiration(validity)
            .signWith(secretKey, Jwts.SIG.HS256)
            .compact();
}
```

### 3단계: Security 필터 체인 확인
`JwtAuthenticationFilter`의 `shouldSkipFilter` 메서드가 정상 작동하는지 확인:
```java
private boolean shouldSkipFilter(String requestURI) {
    return requestURI.startsWith("/api/auth/") ||    // 인증 관련 경로 제외
           requestURI.equals("/api/") ||
           requestURI.equals("/api/health") ||
           requestURI.startsWith("/api/public/") ||
           requestURI.startsWith("/actuator/") ||
           requestURI.startsWith("/error");
}
```

## 🏗️ 현재 JWT 인증 시스템 아키텍처

### 전체 인증 플로우
```
1. 클라이언트 ──POST /api/auth/signup──> 백엔드 (회원가입)
                                          │
                                          ▼
                                      MySQL DB 저장
                                          │
2. 클라이언트 ──POST /api/auth/login───> 백엔드 (로그인)
                                          │
                                          ▼
                                    사용자 인증 확인
                                          │
                                          ▼
                                   JWT 토큰 생성 및 반환
                                          │
3. 클라이언트 ──API 요청 (Bearer Token)──> 백엔드
                                          │
                                          ▼
                                   JwtAuthenticationFilter
                                          │
                                          ▼
                                      토큰 검증
                                          │
                                          ▼
                                      API 처리
```

### 주요 컴포넌트

#### 1. AuthController.java
- **역할**: 인증 관련 REST API 엔드포인트 제공
- **주요 메서드**:
  - `POST /api/auth/signup`: 회원가입
  - `POST /api/auth/login`: 로그인 및 JWT 토큰 발급
  - `POST /api/auth/refresh`: 토큰 갱신
  - `GET /api/auth/me`: 현재 사용자 정보 조회

#### 2. AuthService.java
- **역할**: 인증 비즈니스 로직 처리
- **주요 기능**:
  - 사용자 등록 (비밀번호 암호화)
  - 로그인 검증 및 JWT 토큰 생성
  - 토큰 갱신

#### 3. JwtUtil.java
- **역할**: JWT 토큰 생성/검증/파싱
- **주요 메서드**:
  - `createAccessToken()`: Access Token 생성 (1시간)
  - `createRefreshToken()`: Refresh Token 생성 (7일)
  - `isTokenValid()`: 토큰 유효성 검증
  - `getEmailFromToken()`: 토큰에서 이메일 추출
  - `getRoleFromToken()`: 토큰에서 역할 추출

#### 4. JwtAuthenticationFilter.java
- **역할**: HTTP 요청 시 JWT 토큰 검증
- **동작 방식**:
  1. Authorization 헤더에서 Bearer 토큰 추출
  2. 인증 제외 경로(`/api/auth/`) 체크
  3. 토큰 유효성 및 만료 확인
  4. SecurityContext에 인증 정보 설정

#### 5. SecurityConfig.java
- **역할**: Spring Security 보안 설정
- **주요 설정**:
  - CSRF 비활성화 (JWT 사용으로 불필요)
  - 세션 정책: STATELESS
  - 권한 설정: `/api/auth/**` 경로는 인증 없이 접근 가능
  - JWT 필터를 UsernamePasswordAuthenticationFilter 전에 등록

### JWT 토큰 구조

#### Access Token
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user@example.com",      // 사용자 이메일
    "role": "USER",                 // 사용자 역할
    "accountId": 13,                // 계정 ID
    "iat": 1757642552,              // 발행 시간
    "exp": 1757646152               // 만료 시간 (1시간 후)
  },
  "signature": "..."
}
```

#### Refresh Token
```json
{
  "header": {
    "alg": "HS256", 
    "typ": "JWT"
  },
  "payload": {
    "sub": "user@example.com",      // 사용자 이메일
    "iat": 1757642552,              // 발행 시간
    "exp": 1758247352               // 만료 시간 (7일 후)
  },
  "signature": "..."
}
```

## 🔒 보안 설정

### 환경변수 설정 (back/.env)
```env
# Database Configuration
DB_URL=jdbc:mysql://134.185.106.160:3306/final_project
DB_USERNAME=user
DB_PASSWORD=1234
DB_DRIVER=com.mysql.cj.jdbc.Driver

# Redis Configuration  
REDIS_PASSWORD=

# JWT Configuration
JWT_SECRET=beb305030e21a9a32e1b77bc685749ac
```

### Spring 설정 (application.yml)
```yaml
jwt:
  secret: ${JWT_SECRET:my-super-secret-jwt-key-that-is-at-least-64-characters-long}
  access-expiration: 3600000     # 1시간 (ms)
  refresh-expiration: 604800000  # 7일 (ms)
```

## 📊 데이터베이스 연동

### MySQL 연결
- **서버**: 134.185.106.160:3306
- **데이터베이스**: final_project
- **테이블**: account (사용자 정보 저장)

### Redis 연결
- **용도**: JWT 토큰 캐싱 (향후 확장 가능)
- **연결**: Docker 컨테이너 (localhost:6379)

## ✅ 테스트 결과

### 회원가입 테스트
```bash
curl -X POST http://localhost:8080/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"password123"}'
```
**응답**:
```json
{
  "message": "회원가입 성공",
  "username": "testuser", 
  "email": "test@test.com"
}
```

### 로그인 테스트
```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123"}'
```
**응답**:
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0QHRlc3QuY29tIiwicm9sZSI6IlVTRVIiLCJhY2NvdW50SWQiOjEzLCJpYXQiOjE3NTc2NDI1NTIsImV4cCI6MTc1NzY0NjE1Mn0...",
  "refreshToken": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0QHRlc3QuY29tIiwiaWF0IjoxNzU3NjQyNTUyLCJleHAiOjE3NTgyNDczNTJ9...",
  "userId": "13",
  "email": "test@test.com",
  "username": "testuser"
}
```

## 🚀 현재 시스템 상태

- ✅ **프론트엔드**: http://localhost:3000 (Vue 3 + Vite)
- ✅ **백엔드**: http://localhost:8080 (Spring Boot)
- ✅ **데이터베이스**: MySQL 원격 서버 연결
- ✅ **캐시**: Redis Docker 컨테이너 실행
- ✅ **인증**: JWT 토큰 기반 완전 구현
- ✅ **보안**: Spring Security + CORS 설정 완료

## 📈 향후 개선 사항

1. **토큰 블랙리스트**: 로그아웃 시 토큰 무효화
2. **Redis 활용**: JWT 토큰 세션 관리
3. **토큰 자동 갱신**: Access Token 만료 시 자동 갱신
4. **권한 기반 접근 제어**: 역할별 세분화된 권한 관리
5. **로그 시스템**: 인증 관련 보안 로깅

---
*문제 해결 완료일: 2025-09-12*
*작성자: Claude Code Assistant*