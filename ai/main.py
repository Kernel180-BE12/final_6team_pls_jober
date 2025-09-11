from dotenv import load_dotenv
# 환경 변수 로드
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from routers import ai_routes
# 로깅 안되서 넣음
# import logging
#
# logging.basicConfig(
#     level=logging.DEBUG,  # 또는 INFO
#     format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S"
# )
#
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

app = FastAPI(
    title="AI Service API",
    description="FastAPI + ChromaDB + OpenAI + Hugging Face AI 서비스\n\n포함된 서비스:\n- 기본 AI 서비스\n- 알림톡 템플릿 검증 시스템",
    version="1.0.0"
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
    app.include_router(alimtalk_routes.router)
    print("✅ 알림톡 검증 라우터 등록 완료")
    
    # 알림톡 서비스 초기화
    @app.on_event("startup")
    async def initialize_alimtalk():
        """알림톡 서비스 초기화"""
        try:
            print("🔧 알림톡 검증 서비스 초기화 중...")
            await alimtalk_routes.validation_service.initialize()
            print("✅ 알림톡 검증 서비스 초기화 완료!")
        except Exception as e:
            print(f"❌ 알림톡 서비스 초기화 실패: {e}")
            
except ImportError as e:
    print(f"⚠️ 알림톡 검증 라우터 로드 실패: {e}")
except Exception as e:
    print(f"❌ 알림톡 검증 라우터 등록 실패: {e}")

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
