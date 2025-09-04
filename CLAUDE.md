# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**카카오톡 템플릿 자동생성 서비스 (기업 프로젝트)**

이 프로젝트는 사용자가 카카오톡 템플릿을 AI를 활용해 자동으로 생성하는 서비스입니다.
- 사용자가 메시지 서비스에서 전송할 인원을 등록하고 메시지 내용을 입력
- AI가 메시지 내용만 분석하여 적절한 카카오톡 템플릿을 자동으로 생성
- 알림톡 화이트리스트/블랙리스트를 확인하여 규정에 맞는 템플릿을 생성

### 알림톡 규정 참조
- **화이트리스트**: 아래 상세 내용 참조
- **블랙리스트**: 아래 상세 내용 참조

### 카카오 알림톡 화이트리스트 (발송 가능한 템플릿 유형)

**주요 카테고리:**
1. 회원가입 - 회원 가입 안내, 혜택 안내
2. 주문/배송 - 주문완료, 구매확정, 배송현황, 항공권/철도승차권
3. 예약/신청 - 홈쇼핑 방송예약, 게임 사전예약, 외부 서비스 알림, 대리운전, 직업소개/견적, 여행상품 예약 리마인드, 유료 정보서비스
4. 구매완료/만족도 조사 - 사용법 안내, 주의사항, 만족도 조사, 구매 감사 인사
5. 쿠폰/포인트/마일리지 - 포인트 적립/소멸, 이벤트 당첨, 호텔 쿠폰, 정책 변경
6. 안전/보안 - 보안 정보, OTP, 재난문자
7. 금융 - 은행 거래, 증권, 보험, 신용카드, 금융정보, 신용정보
8. 정당 - 원내 정당의 당원 관리 메시지
9. 알림톡 발송 안내 - 최초 수신 안내, 내용 정정
10. 기타 안내/알림 - 주정차단속, 렌트카, 사내업무, 민방위, 학사일정, 환경측정, 경매, 자격증, 계약 고지사항, 공공기관 의무사항, QnA, 법적 의무사항

**핵심 원칙:**
- 광고성 내용 금지, 정보성/안내성 내용만 가능
- 수신자가 요청했거나 관련 서비스를 이용하는 경우에만 발송
- 명확한 발송 근거와 목적 필요

### 카카오 알림톡 블랙리스트 (발송 불가 템플릿 유형)

**주요 금지 사항:**
1. **포인트/쿠폰 관련** - 명시적 동의 없는 포인트 적립/소멸, 빠른 소멸 쿠폰 안내
2. **무료 서비스** - 무료 뉴스레터, 무료 구독형 메시지
3. **일반 공지** - 계약 관계가 아닌 일반적인 공지 메시지
4. **변수 전용** - 변수만으로 구성된 메시지
5. **마케팅성** - 장바구니 안내, 특가 알림, 클릭 상품 안내, 앱 다운로드 유도
6. **인사성** - 생일 축하, 안부 문자, 통화 후 자동 발송
7. **채널 관련** - 카카오톡 채널 추가 확인, 수신동의 확인
8. **금융 유도** - 결제/송금/납부 유도 (특정 업체 제외), 이용하지 않는 대출 정보
9. **광고 연결** - 비광고성 메시지에 광고성 URL 포함
10. **연령 제한** - 청소년 이용불가 게임, 주류 등 유해 콘텐츠

**핵심 금지 원칙:**
- 광고성, 마케팅성 내용 포함 금지
- 수신자가 요청하지 않은 일방적 안내 금지
- 즉시성이 없는 단순 홍보성 메시지 금지
- 인사, 안부 등 감정적 접근 금지

### 템플릿 생성 프로세스
1. **사용자 메시지 전처리**
   - 질의 정제 (Query Refinement)
   - 의도 파악 (Intent Recognition) 
   - 임베딩 벡터 생성

2. **벡터 저장**
   - ChromaDB에 임베딩 벡터 저장

3. **템플릿 생성 로직**
   - 사용자 입력을 기반으로 카카오톡 템플릿 자동 생성
   - MySQL(RDB)에 저장된 예시 템플릿과 유사도 비교하여 참고용으로 활용
   - **유사도 높음**: 예시 템플릿을 참고하여 새로 생성
   - **유사도 낮음**: 완전히 새로운 템플릿 생성
   - **중요**: 기존 템플릿을 재사용하는 것이 아닌, 참고용으로만 활용

4. **템플릿 검증**
   - 생성된 템플릿을 화이트리스트/블랙리스트와 비교하여 규정 준수 검증
   - 부적합한 경우 재생성 또는 수정 제안

### 카카오톡 템플릿 생성 가이드

**템플릿 구성 요소:**
- **변수 표기법**: `#{변수명}` 형태로 표현
- **필수 정보**: 발송 목적과 근거를 명시
- **버튼/링크**: `#{버튼명}` 또는 `#{url}` 형태로 표기
- **주의사항**: 템플릿 하단에 발송 근거 명시 (`*` 표시로 시작)

**생성 예시:**
```
[OO카드] 카카오톡 명세서
#{고객명} 회원님! #{결제월}월 결제금액에 대한 명세서입니다.
■ 당월 결제금액
#{청구금액}원
■ 모바일 명세서로 보기
#{url}

카카오톡 명세서 수신 고객 대상으로 OO이벤트가 진행 중입니다.
아래 버튼을 누르시면 이벤트 페이지로 이동합니다.
#{이벤트 페이지 이동 버튼}
```

### 예시 템플릿 DB 구조 (MySQL)
```
텍스트: 안녕하세요 #{수신자명}님, 요청하신 서비스 소개서가 발송되었습니다. 아래 버튼을 클릭하시면 자세한 내용을 확인하실 수 있습니다. *서비스 소개서를 요청하신 분들께 발송되는 메시지입니다.
분류 1차: 서비스이용
분류 2차: 이용안내/공지
자동생성제목: 서비스 소개서 발송
템플릿코드: Introduction25042902
공용or전용: 공용
업종분류: 서비스업
목적분류: 공지/안내
```

### 벡터 검색 로직
- 예시 템플릿들도 ChromaDB에 임베딩되어 저장
- 사용자 메시지와 예시 템플릿 간 유사도 검색
- 유사한 예시가 있어도 **무조건 새로 생성**, 단지 **참고용**으로만 활용

### Architecture
- **Frontend**: Vue 3 + TypeScript (port 3000) - 사용자 인터페이스
- **Backend**: Spring Boot + Java 17 (port 8080) - 비즈니스 로직 및 데이터 관리
- **AI Service**: FastAPI + Python (port 8000) - 템플릿 자동생성 AI 엔진

## Development Commands

### Frontend (Vue 3)
```bash
cd front
npm install                 # Install dependencies
npm run dev                # Run development server
npm run build              # Build for production
npm run type-check         # Type checking
npm run lint               # Lint code
npm run format             # Format code
```

### Backend (Spring Boot)
```bash
cd back
./gradlew build            # Build project
./gradlew bootRun          # Run application
./gradlew test             # Run tests
# Windows: use gradlew.bat instead of ./gradlew
```

### AI Service (FastAPI)
```bash
cd ai
python -m venv venv        # Create virtual environment
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Project Structure

### Frontend (`/front`)
- Vue 3 + TypeScript + Vite
- Vuetify for UI components
- Pinia for state management
- Vue Router for routing
- Proxy configured: `/api` → Backend, `/ai` → AI Service

### Backend (`/back`)
- Spring Boot 3.2.0 + Java 17
- Spring Data JPA + MySQL
- Spring Security + JWT
- Redis for caching
- Package structure: `com.example.*`

### AI Service (`/ai`)
- FastAPI framework
- ChromaDB for vector storage
- OpenAI API integration
- Hugging Face transformers
- Service-based architecture

## Key Configuration Files

- `front/vite.config.ts` - Frontend build config with proxy settings
- `back/build.gradle` - Backend dependencies and build config
- `ai/requirements.txt` - Python dependencies
- `front/package.json` - Node.js dependencies and scripts

## Running the Full Stack

1. Start Backend: `cd back && ./gradlew bootRun`
2. Start AI Service: `cd ai && uvicorn main:app --reload`
3. Start Frontend: `cd front && npm run dev`
4. Access at: http://localhost:3000

## Prerequisites

- Java 17+
- Node.js 18+
- Python 3.8+
- MySQL and Redis running
- OpenAI API key (for AI service)

## Important Notes

- Frontend proxies API calls to avoid CORS issues
- Backend uses context path `/api`
- AI service exposes Swagger docs at `/docs`
- Environment variables needed for database connections and API keys