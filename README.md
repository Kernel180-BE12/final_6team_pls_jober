# Final Project

## 📁 프로젝트 구조

```
final_project/
├── back/          # Spring Boot 백엔드 (포트 8080)
├── front/         # Vue 3 프론트엔드 (포트 3000)gdgdgdgd
├── ai/            # FastAPI AI 서비스 (포트 8000)
└── README.md
```

## 🛠️ 기술 스택

### Frontend (Vue 3)
- **Vue 3** + TypeScript
- **Vite** (빌드 도구)
- **Vuetify** (UI 라이브러리)
- **Axios** + **@tanstack/vue-query** (서버 통신)
- **Pinia** (상태 관리)
- **Vue Router** (라우팅)

### Backend (Spring Boot)
- **Spring Boot 3.2.0**
- **Java 17**
- **MySQL** + **JPA**
- **Redis** (캐시/세션)
- **Spring Security** + **JWT**
- **Gradle**

### AI Service (FastAPI)
- **FastAPI**
- **ChromaDB** (벡터 데이터베이스)
- **OpenAI** (GPT 모델)
- **Hugging Face** (임베딩 모델)
- **Python 3.8+**

## 🚀 실행 방법

### 1️⃣ 필요한 서버들 실행

**전체 시스템을 동작시키려면 다음 3개 서버를 모두 실행해야 합니다:**

#### 1. Backend 서버 (Spring Boot)
```bash
cd back
./gradlew bootRun
# 또는 Windows: gradlew.bat bootRun
```
- **포트**: 8080
- **확인**: http://localhost:8080/api/health

#### 2. AI 서비스 (FastAPI)
```bash
cd ai
# 가상환경 활성화
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- **포트**: 8000
- **확인**: http://localhost:8000/docs

#### 3. Frontend 서버 (Vue 3)
```bash
cd front
npm install
npm run dev
```
- **포트**: 3000
- **확인**: http://localhost:3000

### 2️⃣ 동작 확인

1. **3개 서버 모두 실행** 후 브라우저에서 `http://localhost:3000` 접속
2. **카카오톡 템플릿 생성 기능** 사용 가능
3. **AI 서비스**를 통한 템플릿 검증 및 생성

## 📋 사전 요구사항

- **Java 17 이상**
- **Node.js 18 이상**
- **Python 3.8 이상**
- **MySQL** (데이터베이스)
- **Redis** (캐시 서버)
- **OpenAI API 키** (AI 기능 사용 시)

## 🔧 환경 설정

각 폴더의 README.md를 참조하여 상세한 설정 방법을 확인하세요.

