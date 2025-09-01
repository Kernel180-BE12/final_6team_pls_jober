# AI Service (FastAPI)

## 기술 스택

- **FastAPI** - Python 웹 프레임워크
- **Uvicorn** - ASGI 서버
- **ChromaDB** - 벡터 데이터베이스
- **OpenAI** - AI 모델 API
- **Hugging Face** - 오픈소스 AI 모델
- **Pydantic** - 데이터 검증
- **Python-dotenv** - 환경 변수 관리

## 설치 및 실행

### 1. 가상환경 생성 및 활성화

```bash
# ai 폴더로 이동
cd ai

# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (Linux/Mac)
source venv/bin/activate
```

### 2. 의존성 설치

```bash
# 의존성 설치
pip install -r requirements.txt
```

### 3. 환경 변수 설정

```bash
# 환경 변수 예시 파일 복사
cp env.example .env

# .env 파일 편집하여 API 키 설정
# OPENAI_API_KEY=your_openai_api_key_here
# HF_TOKEN=your_huggingface_token_here
```

### 4. 서버 실행

```bash
# 개발 서버 실행 (포트 8000)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 또는 Python으로 직접 실행
python main.py
```

## API 엔드포인트

- **포트**: 8000
- **API 문서**: `http://localhost:8000/docs`

### 기본 엔드포인트
- `GET /` - 홈
- `GET /health` - 헬스 체크

### OpenAI 서비스
- `POST /ai/openai/chat` - OpenAI 채팅
- `POST /ai/openai/embeddings` - OpenAI 임베딩

### ChromaDB 서비스
- `POST /ai/chromadb/documents` - 문서 추가
- `POST /ai/chromadb/search` - 문서 검색
- `GET /ai/chromadb/info` - 컬렉션 정보
- `GET /ai/chromadb/documents/{id}` - 문서 조회

### Hugging Face 서비스
- `POST /ai/huggingface/generate` - 텍스트 생성
- `POST /ai/huggingface/sentiment` - 감정 분석
- `POST /ai/huggingface/embeddings` - 임베딩 생성
- `POST /ai/huggingface/qa` - 질문-답변
- `GET /ai/huggingface/models` - 사용 가능한 모델 목록

## 테스트 방법

### 1. 기본 서버 테스트

```bash
# 서버 실행
uvicorn main:app --reload

# 브라우저에서 API 문서 확인
# http://localhost:8000/docs

# 기본 엔드포인트 테스트
curl http://localhost:8000/
curl http://localhost:8000/health
```

### 2. OpenAI API 테스트

```bash
# OpenAI 채팅 테스트
curl -X POST "http://localhost:8000/ai/openai/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "안녕하세요!", "model": "gpt-3.5-turbo"}'

# OpenAI 임베딩 테스트
curl -X POST "http://localhost:8000/ai/openai/embeddings" \
     -H "Content-Type: application/json" \
     -d '"Hello, world!"'
```

### 3. ChromaDB 테스트

```bash
# 문서 추가 테스트
curl -X POST "http://localhost:8000/ai/chromadb/documents" \
     -H "Content-Type: application/json" \
     -d '{"content": "샘플 문서 내용", "metadata": {"source": "test"}}'

# 문서 검색 테스트
curl -X POST "http://localhost:8000/ai/chromadb/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "샘플", "n_results": 5}'

# 컬렉션 정보 조회
curl http://localhost:8000/ai/chromadb/info
```

### 4. Hugging Face 테스트

```bash
# 감정 분석 테스트
curl -X POST "http://localhost:8000/ai/huggingface/sentiment" \
     -H "Content-Type: application/json" \
     -d '{"text": "오늘은 정말 좋은 날씨입니다!", "model": "cardiffnlp/twitter-roberta-base-sentiment"}'

# 텍스트 생성 테스트
curl -X POST "http://localhost:8000/ai/huggingface/generate" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "The future of AI is", "model": "gpt2", "max_length": 50}'

# 사용 가능한 모델 목록 조회
curl http://localhost:8000/ai/huggingface/models
```

### 5. Python 스크립트로 테스트

```python
import requests
import json

# 기본 테스트
response = requests.get("http://localhost:8000/")
print(response.json())

# OpenAI 채팅 테스트
chat_data = {
    "message": "안녕하세요!",
    "model": "gpt-3.5-turbo"
}
response = requests.post("http://localhost:8000/ai/openai/chat", json=chat_data)
print(response.json())

# ChromaDB 문서 추가 테스트
doc_data = {
    "content": "Python으로 테스트하는 문서입니다.",
    "metadata": {"source": "python_test"}
}
response = requests.post("http://localhost:8000/ai/chromadb/documents", json=doc_data)
print(response.json())
```

## 프로젝트 구조

```
ai/
├── main.py                 # 메인 애플리케이션
├── requirements.txt        # Python 의존성
├── env.example            # 환경 변수 예시
├── README.md              # 프로젝트 문서
├── services/              # 서비스 클래스들
│   ├── openai_service.py  # OpenAI 서비스
│   ├── chromadb_service.py # ChromaDB 서비스
│   └── huggingface_service.py # Hugging Face 서비스
└── routers/               # API 라우터
    └── ai_routes.py       # AI 관련 라우트
```

## 문제 해결

### 1. 가상환경 문제

```bash
# 가상환경이 활성화되지 않은 경우
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 가상환경 확인
which python
pip list
```

### 2. 의존성 설치 문제

```bash
# pip 업그레이드
pip install --upgrade pip

# 캐시 삭제 후 재설치
pip cache purge
pip install -r requirements.txt
```

### 3. API 키 설정 문제

```bash
# .env 파일 확인
cat .env

# 환경 변수 확인
echo $OPENAI_API_KEY

# Python에서 확인
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

### 4. 포트 충돌 문제

```bash
# 다른 포트로 실행
uvicorn main:app --reload --port 8001

# 포트 사용 확인
# Linux/Mac
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

### 5. 모델 다운로드 문제

```bash
# Hugging Face 모델 캐시 확인
# ~/.cache/huggingface/

# 모델 캐시 삭제 (필요시)
rm -rf ~/.cache/huggingface/

# 인터넷 연결 확인
curl -I https://huggingface.co
```

## 성능 최적화

### 1. GPU 사용 (선택사항)

```bash
# CUDA 설치 확인
python -c "import torch; print(torch.cuda.is_available())"

# GPU 메모리 확인
nvidia-smi
```

### 2. 모델 캐싱

```bash
# Hugging Face 모델 캐시 디렉토리 설정
export HF_HOME=/path/to/cache
export TRANSFORMERS_CACHE=/path/to/cache
```

### 3. ChromaDB 최적화

```bash
# ChromaDB 설정 확인
# ./chroma_db 디렉토리 권한 확인
ls -la ./chroma_db
```

## 주의사항

1. **API 키 설정**: OpenAI API 키를 `.env` 파일에 설정해야 합니다.
2. **모델 다운로드**: Hugging Face 모델은 첫 사용 시 자동으로 다운로드됩니다.
3. **GPU 사용**: CUDA가 설치된 환경에서는 GPU를 자동으로 사용합니다.
4. **ChromaDB 저장소**: `./chroma_db` 디렉토리에 데이터가 저장됩니다.
5. **메모리 사용량**: Hugging Face 모델은 상당한 메모리를 사용할 수 있습니다.
