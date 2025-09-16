# ===================================================================
#  AI 서비스 Dockerfile (단순화)
# ===================================================================
FROM python:3.10-slim
# 작업 디렉토리 설정
WORKDIR /app
# 시스템 패키지 설치 (한 번에)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip wheel setuptools
# requirements.txt 먼저 복사 (캐싱 활용)
COPY requirements.txt .
# 의존성 설치 (시간 단축 옵션)
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt
# 애플리케이션 코드 복사
COPY . .
# ChromaDB 디렉토리 생성
RUN mkdir -p /app/chroma_db
# 포트 노출
EXPOSE 8000
# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
# 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]