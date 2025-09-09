# Final Project

## 프로젝트 구조

```
final_project/
├── back/          # Spring Boot 백엔드
├── front/         # Vue 3 프론트엔드
├── ai/            # FastAPI AI 서비스
└── README.md
```

## 기술 스택

### Frontend (Vue 3)
- Vue 3 + TypeScript
- Vite (빌드 도구)
- Vuetify (UI 라이브러리)
- Axios + Vue Query (서버 통신)
- Pinia (상태 관리)
- Vue Router (라우팅)

### Backend (Spring Boot)
- Spring Boot
- Redis
- MySQL + JPA
- Gradle

### AI Service (FastAPI)
- FastAPI
- ChromaDB
- OpenAI
- Hugging Face

## 실행 방법

### 1. Frontend (Vue 3) 테스트

```bash
# front 폴더로 이동
cd front

# 의존성 설치
npm install

# 개발 서버 실행 (포트 3000)
npm run dev

# 브라우저에서 확인
# http://localhost:3000
```

### 2. Backend (Spring Boot) 테스트

```bash
# back 폴더로 이동
cd back

# Gradle Wrapper 권한 설정 (Linux/Mac)
chmod +x gradlew

# 애플리케이션 실행 (포트 8080)
./gradlew bootRun

# 또는 Windows에서
gradlew.bat bootRun

# API 테스트
curl http://localhost:8080/api/
curl http://localhost:8080/api/health
```

### 3. AI Service (FastAPI) 테스트

```bash
# ai 폴더로 이동
cd ai

# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (Linux/Mac)
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env .env
# .env 파일을 편집하여 OpenAI API 키 등 설정

# 서버 실행 (포트 8000)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# API 문서 확인
# http://localhost:8000/docs

# API 테스트
curl http://localhost:8000/
curl http://localhost:8000/health
```

## 전체 시스템 테스트

1. **Backend 실행**: `cd back && ./gradlew bootRun`
2. **AI Service 실행**: `cd ai && uvicorn main:app --reload`
3. **Frontend 실행**: `cd front && npm run dev`
4. **브라우저에서 확인**: `http://localhost:3000`

## 포트 정보

- **Frontend**: 3000 (http://localhost:3000)
- **Backend**: 8080 (http://localhost:8080/api)
- **AI Service**: 8000 (http://localhost:8000)

## 주의사항

1. **Java 17 이상**이 설치되어 있어야 합니다.
2. **Node.js 18 이상**이 설치되어 있어야 합니다.
3. **Python 3.8 이상**이 설치되어 있어야 합니다.
4. **MySQL**과 **Redis**가 실행 중이어야 합니다.
5. **OpenAI API 키**가 필요합니다 (AI 서비스 사용 시).

각 폴더의 README.md를 참조하세요.

