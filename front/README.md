# Frontend (Vue 3)

## 기술 스택

- **Vue 3** - 프론트엔드 프레임워크
- **TypeScript** - 타입 안전성
- **Vite** - 빌드 도구
- **Vuetify** - UI 라이브러리
- **Pinia** - 상태 관리
- **Vue Router** - 라우팅
- **Axios** - HTTP 클라이언트
- **Vue Query** - 서버 상태 관리

## 설치 및 실행

### 1. 의존성 설치

```bash
# front 폴더로 이동
cd front

# 의존성 설치
npm install
```

### 2. 개발 서버 실행

```bash
# 개발 서버 실행 (포트 3000)
npm run dev

# 브라우저에서 확인
# http://localhost:3000
```

### 3. 빌드 및 배포

```bash
# 프로덕션 빌드
npm run build

# 빌드 미리보기
npm run preview

# 타입 체크
npm run type-check

# 린트 검사
npm run lint

# 코드 포맷팅
npm run format
```

## 프로젝트 구조

```
src/
├── api/          # API 관련 설정
├── components/   # 재사용 가능한 컴포넌트
├── router/       # 라우터 설정
├── stores/       # Pinia 스토어
├── views/        # 페이지 컴포넌트
├── App.vue       # 메인 앱 컴포넌트
└── main.ts       # 앱 진입점
```

## 개발 서버

- **포트**: 3000
- **프록시**: 
  - `/api` → `http://localhost:8080` (Spring Boot)
  - `/ai` → `http://localhost:8000` (FastAPI)

## 테스트 방법

### 1. 기본 테스트

```bash
# 개발 서버 실행
npm run dev

# 브라우저에서 http://localhost:3000 접속
# 홈페이지와 About 페이지 확인
```

### 2. API 연동 테스트

```bash
# Backend 서버가 실행 중인지 확인
# http://localhost:8080/api/health

# AI 서버가 실행 중인지 확인  
# http://localhost:8000/health

# 브라우저 개발자 도구에서 네트워크 탭 확인
# API 호출이 정상적으로 프록시되는지 확인
```

### 3. 컴포넌트 테스트

```bash
# 브라우저에서 다음 기능들 테스트:
# 1. 홈페이지 로딩
# 2. About 페이지 이동
# 3. Vuetify 컴포넌트 렌더링
# 4. 반응형 디자인 확인
```

## 주요 기능

### 1. 라우팅
- 홈페이지 (`/`)
- About 페이지 (`/about`)

### 2. 상태 관리
- Pinia 스토어 예시 (`src/stores/counter.ts`)

### 3. API 통신
- Axios 설정 (`src/api/index.ts`)
- 자동 토큰 관리
- 에러 핸들링

### 4. UI 컴포넌트
- Vuetify Material Design
- 반응형 레이아웃
- 아이콘 (Material Design Icons)

## 문제 해결

### 1. 의존성 설치 문제

```bash
# node_modules 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install
```

### 2. 포트 충돌 문제

```bash
# 다른 포트로 실행
npm run dev -- --port 3001
```

### 3. TypeScript 오류

```bash
# 타입 체크 실행
npm run type-check

# 타입 정의 파일 확인
# src/env.d.ts
```

### 4. 프록시 설정 문제

```bash
# vite.config.ts에서 프록시 설정 확인
# Backend와 AI 서버가 실행 중인지 확인
```

## 개발 팁

1. **Hot Reload**: 코드 변경 시 자동으로 브라우저가 새로고침됩니다.
2. **TypeScript**: 타입 안전성을 위해 TypeScript를 사용합니다.
3. **Vue DevTools**: 브라우저 확장 프로그램을 설치하여 Vue 컴포넌트를 디버깅할 수 있습니다.
4. **Vuetify**: Material Design 컴포넌트를 사용하여 일관된 UI를 제공합니다.

