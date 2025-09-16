# ===================================================================
#  AI 서비스 Multi-stage Dockerfile (최적화)
# ===================================================================

# Stage 1: 의존성 빌드 및 설치
FROM python:3.10-slim as builder

# 빌드 도구 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# pip 업그레이드 및 캐시 설정
RUN pip install --upgrade pip wheel setuptools

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 먼저 복사 (Docker layer 캐싱 활용)
COPY requirements.txt .

# 의존성을 /opt/venv에 설치 (가상환경 사용)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 의존성 설치 (캐시 최적화)
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: 런타임 이미지
FROM python:3.10-slim as runtime

# 런타임 필요 패키지만 설치
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 가상환경 복사
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 작업 디렉토리 설정
WORKDIR /app

# 애플리케이션 소스 코드만 복사
COPY --chown=1000:1000 . .

# ChromaDB 데이터 디렉토리 생성
RUN mkdir -p /app/chroma_db && chown -R 1000:1000 /app

# 비루트 사용자로 실행
USER 1000

# 포트 노출
EXPOSE 8000

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
