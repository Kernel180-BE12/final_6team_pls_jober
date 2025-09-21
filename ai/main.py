from dotenv import load_dotenv
import os
# 환경 변수 로드 - 현재 폴더의 .env 파일 참조
load_dotenv()

from fastapi import FastAPI, HTTPException
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
        print("🔧 알림톡 검증 서비스 초기화 중...")
        logger.info("알림톡 검증 서비스 초기화 시작")
        await alimtalk_routes.validation_service.initialize()
        print("✅ 알림톡 검증 서비스 초기화 완료!")
        logger.info("알림톡 검증 서비스 초기화 완료")
    except Exception as e:
        print(f"❌ 알림톡 서비스 초기화 실패: {e}")
        logger.error(f"알림톡 서비스 초기화 실패: {e}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")
    
    yield
    
    # 종료 시 실행 (필요한 경우)
    print("🔄 서비스 종료 중...")

app = FastAPI(
    title="AI Service API",
    description="FastAPI + ChromaDB + OpenAI + Hugging Face AI 서비스\n\n포함된 서비스:\n- 기본 AI 서비스\n- 알림톡 템플릿 검증 시스템",
    version="1.0.0",
    lifespan=lifespan
)

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
    print("✅ 알림톡 검증 라우터 등록 완료")
    logger.info("알림톡 검증 라우터 등록 완료")
    logger.info(f"등록된 라우터 경로: {alimtalk_routes.router.prefix}")
    
except ImportError as e:
    print(">>main<<")
    print(f"⚠️ 알림톡 검증 라우터 로드 실패: {e}")
    logger.error(f"알림톡 검증 라우터 로드 실패: {e}")
except Exception as e:
    print(">>main<<")
    print(f"❌ 알림톡 검증 라우터 등록 실패: {e}")
    logger.error(f"알림톡 검증 라우터 등록 실패: {e}")
    import traceback
    logger.error(f"상세 오류: {traceback.format_exc()}")

# 템플릿 라우터 추가 (존재하지 않으므로 제거)
# from routers import template_routes
# app.include_router(template_routes.router)

# Pydantic 모델
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "gpt-4o-mini"

class ChatResponse(BaseModel):
    response: str
    model: str

class DocumentRequest(BaseModel):
    content: str
    metadata: Optional[dict] = None

class SearchRequest(BaseModel):
    query: str
    n_results: Optional[int] = 5

# 기본 라우트
@app.get("/")
async def root():
    return {"message": "AI Service is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 채팅 엔드포인트
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # OpenAI API 호출 (실제 구현에서는 OpenAI 클라이언트 사용)
        response = f"AI 응답: {request.message}"
        return ChatResponse(response=response, model=request.model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 문서 저장 엔드포인트
@app.post("/documents")
async def add_document(request: DocumentRequest):
    try:
        # ChromaDB에 문서 저장 (실제 구현에서는 ChromaDB 클라이언트 사용)
        return {"message": "Document added successfully", "content": request.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 검색 엔드포인트
@app.post("/search")
async def search_documents(request: SearchRequest):
    try:
        # ChromaDB에서 검색 (실제 구현에서는 ChromaDB 클라이언트 사용)
        results = [f"검색 결과 {i+1}: {request.query}" for i in range(request.n_results)]
        return {"query": request.query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
