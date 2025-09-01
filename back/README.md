# Backend (Spring Boot)

## 기술 스택

- **Spring Boot 3.2.0** - 백엔드 프레임워크
- **Java 17** - 프로그래밍 언어
- **Gradle** - 빌드 도구
- **Spring Data JPA** - ORM
- **MySQL** - 데이터베이스
- **Redis** - 캐시/세션 저장소
- **Spring Security** - 보안
- **JWT** - 인증 토큰

## 환경 설정

### 데이터베이스 설정
1. MySQL 설치 및 실행
2. 데이터베이스 생성:
```sql
CREATE DATABASE final_project CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Redis 설정
1. Redis 설치 및 실행
2. 기본 포트: 6379

### 환경 변수 설정
`.env` 파일을 생성하고 다음 변수들을 설정하세요:
```
DB_USERNAME=your_db_username
DB_PASSWORD=your_db_password
REDIS_PASSWORD=your_redis_password
JWT_SECRET=your-jwt-secret-key-here-make-it-long-and-secure
```

## 실행 방법

### Gradle Wrapper 사용 (권장)

```bash
# Gradle Wrapper 권한 설정 (Linux/Mac)
chmod +x gradlew

# 프로젝트 빌드
./gradlew build

# 애플리케이션 실행
./gradlew bootRun

# 또는 Windows에서
gradlew.bat bootRun
```

### JAR 파일로 실행

```bash
# 빌드 후 JAR 파일 실행
./gradlew build
java -jar build/libs/back-0.0.1-SNAPSHOT.jar
```

### 테스트 실행

```bash
# 단위 테스트 실행
./gradlew test

# 통합 테스트 실행
./gradlew integrationTest
```

## API 엔드포인트

- **포트**: 8080
- **컨텍스트 패스**: `/api`

### 기본 엔드포인트
- `GET /api/` - 홈
- `GET /api/health` - 헬스 체크

### 사용자 관리
- `GET /api/users` - 모든 사용자 조회
- `GET /api/users/{id}` - 특정 사용자 조회
- `POST /api/users` - 사용자 생성
- `PUT /api/users/{id}` - 사용자 수정
- `DELETE /api/users/{id}` - 사용자 삭제

## API 테스트

### curl 명령어 예시

```bash
# 홈 페이지 테스트
curl http://localhost:8080/api/

# 헬스 체크
curl http://localhost:8080/api/health

# 사용자 목록 조회
curl http://localhost:8080/api/users

# 사용자 생성
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123",
    "email": "test@example.com"
  }'
```

## 프로젝트 구조

```
src/main/java/com/example/
├── BackApplication.java    # 메인 애플리케이션
├── config/                # 설정 클래스
├── controller/            # REST 컨트롤러
├── entity/               # JPA 엔티티
├── repository/           # 데이터 접근 계층
└── service/              # 비즈니스 로직
```

## 문제 해결

### Gradle Wrapper 관련 문제

1. **권한 오류 (Linux/Mac)**:
   ```bash
   chmod +x gradlew
   ```

2. **Gradle Wrapper JAR 파일 누락**:
   ```bash
   # gradle-wrapper.jar 파일을 다운로드
   curl -o gradle/wrapper/gradle-wrapper.jar \
     https://github.com/gradle/gradle/raw/master/gradle/wrapper/gradle-wrapper.jar
   ```

3. **Java 버전 문제**:
   ```bash
   # Java 버전 확인
   java -version
   
   # JAVA_HOME 설정 확인
   echo $JAVA_HOME
   ```

### 데이터베이스 연결 문제

1. **MySQL 서비스 확인**:
   ```bash
   # Linux/Mac
   sudo systemctl status mysql
   
   # Windows
   net start mysql
   ```

2. **Redis 서비스 확인**:
   ```bash
   # Linux/Mac
   sudo systemctl status redis
   
   # Windows
   net start redis
   ```

