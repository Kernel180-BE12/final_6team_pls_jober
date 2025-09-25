from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
from api.routes import template_routes
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from exceptions import validation_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager
import os
from routers import ai_routes
# 로깅 활성화 - 디버깅용
import logging

logging.basicConfig(
    level=logging.INFO,  # INFO 레벨로 설정
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    try:
        from routers import alimtalk_routes
        print(">>main<<")
        print("알림톡 검증 서비스 초기화 중...")
        logger.info("알림톡 검증 서비스 초기화 시작")
        await alimtalk_routes.validation_service.initialize()
        print("알림톡 검증 서비스 초기화 완료!")
        logger.info("알림톡 검증 서비스 초기화 완료")
    except Exception as e:
        print(f"알림톡 서비스 초기화 실패: {e}")
        logger.error(f"알림톡 서비스 초기화 실패: {e}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")
    
    yield
    
    # 종료 시 실행 (필요한 경우)
    print("서비스 종료 중...")

app = FastAPI(
    title="AI Service API",
    description="FastAPI + ChromaDB + OpenAI + Hugging Face AI 서비스\n\n포함된 서비스:\n- 기본 AI 서비스\n- 알림톡 템플릿 검증 시스템",
    version="1.0.0",
    lifespan=lifespan
)
#@TODO: 생성 쪽 FastAPI 서버 등록
# app = FastAPI(title="AI Template Generation API")
#@TODO: 생성 쪽 예외처리 핸들러 등록
app.add_exception_handler(RequestValidationError, validation_exception_handler)

#@TODO: 생성 쪽 template_routes 라우터의 모든 경로는 /ai 로 시작하도록 설정.
app.include_router(template_routes.router, prefix="/ai")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(ai_routes.router)

# 알림톡 검증 라우터 추가
try:
    from routers import alimtalk_routes
    logger.info("알림톡 라우터 모듈 로드 완료")
    app.include_router(alimtalk_routes.router)
    print(">>main<<")
    print("[SUCCESS] 알림톡 검증 라우터 등록 완료")
    logger.info("알림톡 검증 라우터 등록 완료")
    logger.info(f"등록된 라우터 경로: {alimtalk_routes.router.prefix}")
    
except ImportError as e:
    print(">>main<<")
    print(f"[WARNING] 알림톡 검증 라우터 로드 실패: {e}")
    logger.error(f"알림톡 검증 라우터 로드 실패: {e}")
except Exception as e:
    print(">>main<<")
    print(f"[ERROR] 알림톡 검증 라우터 등록 실패: {e}")
    logger.error(f"알림톡 검증 라우터 등록 실패: {e}")
    import traceback
    logger.error(f"상세 오류: {traceback.format_exc()}")

# 템플릿 라우터 추가 (존재하지 않으므로 제거)
# from routers import template_routes
# app.include_router(template_routes.router)



# 사용하지 않는 startup 이벤트 제거됨


# 기본 라우트
@app.get("/")
async def root():
    return {"message": "AI Service is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
