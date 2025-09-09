# ===================================================================
#  Stage 1: Build a fat JAR (빌드 전용 스테이지)
# ===================================================================
# JDK 17 이미지를 빌드 환경으로 사용합니다.
FROM eclipse-temurin:17-jdk-jammy as builder

# 작업 디렉토리를 설정합니다.
WORKDIR /workspace/app

# 먼저 빌드에 필요한 파일들만 복사하여 Docker 캐시를 활용합니다.
COPY gradlew .
COPY gradle ./gradle
COPY build.gradle .
COPY settings.gradle .

# 소스 코드를 복사합니다.
COPY src ./src

# gradlew 스크립트에 실행 권한을 부여합니다.
RUN chmod +x ./gradlew

# Gradle을 사용하여 애플리케이션을 빌드합니다. (테스트는 생략하여 빌드 속도 향상)
RUN ./gradlew build -x test
# ===================================================================
#  Stage 2: Create the final runtime image (실행 전용 스테이지)
# ===================================================================
# 실제 실행에 필요한 JRE만 포함된 가벼운 이미지를 사용합니다.
FROM eclipse-temurin:17-jre-jammy

# 빌드 단계에서 생성된 JAR 파일을 복사합니다.
COPY --from=builder /workspace/app/build/libs/*.jar app.jar

# 애플리케이션이 8080 포트를 사용함을 명시합니다.
EXPOSE 8080

# 컨테이너가 시작될 때 애플리케이션을 실행합니다.
ENTRYPOINT ["java", "-jar", "app.jar"]