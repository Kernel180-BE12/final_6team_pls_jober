from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from services.openai_service import OpenAIService
from services.chromadb_service import ChromaDBService
from services.huggingface_service import HuggingFaceService

router = APIRouter(prefix="/ai", tags=["AI Services"])

# 서비스 인스턴스 초기화
openai_service = OpenAIService()
chromadb_service = ChromaDBService()
huggingface_service = HuggingFaceService()

# Pydantic 모델들
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "gpt-3.5-turbo"

class ChatResponse(BaseModel):
    response: str
    model: str

class DocumentRequest(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None

class SearchRequest(BaseModel):
    query: str
    n_results: Optional[int] = 5

class TextGenerationRequest(BaseModel):
    prompt: str
    model: Optional[str] = "gpt2"
    max_length: Optional[int] = 100

class SentimentRequest(BaseModel):
    text: str
    model: Optional[str] = "cardiffnlp/twitter-roberta-base-sentiment"

class QuestionAnswerRequest(BaseModel):
    question: str
    context: str
    model: Optional[str] = "deepset/roberta-base-squad2"

# OpenAI 라우트
@router.post("/openai/chat", response_model=ChatResponse)
async def openai_chat(request: ChatRequest):
    """OpenAI 채팅 API"""
    try:
        messages = [{"role": "user", "content": request.message}]
        response = await openai_service.chat_completion(messages, request.model)
        return ChatResponse(response=response, model=request.model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/openai/embeddings")
async def openai_embeddings(text: str):
    """OpenAI 임베딩 API"""
    try:
        embeddings = await openai_service.embeddings(text)
        return {"embeddings": embeddings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ChromaDB 라우트
@router.post("/chromadb/documents")
async def add_documents(request: DocumentRequest):
    """ChromaDB에 문서 추가"""
    try:
        result = await chromadb_service.add_documents([request.content], [request.metadata])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chromadb/search")
async def search_documents(request: SearchRequest):
    """ChromaDB에서 문서 검색"""
    try:
        result = await chromadb_service.search_documents(request.query, request.n_results)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chromadb/info")
async def get_collection_info():
    """컬렉션 정보 조회"""
    try:
        result = await chromadb_service.get_collection_info()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chromadb/documents/{document_id}")
async def get_document(document_id: str):
    """ID로 문서 조회"""
    try:
        result = await chromadb_service.get_document_by_id(document_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Document not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Hugging Face 라우트
@router.post("/huggingface/generate")
async def generate_text(request: TextGenerationRequest):
    """Hugging Face 텍스트 생성"""
    try:
        result = await huggingface_service.generate_text(
            request.prompt, 
            request.model, 
            request.max_length
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/huggingface/sentiment")
async def analyze_sentiment(request: SentimentRequest):
    """Hugging Face 감정 분석"""
    try:
        result = await huggingface_service.analyze_sentiment(request.text, request.model)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/huggingface/embeddings")
async def get_embeddings(texts: List[str], model: str = "sentence-transformers/all-MiniLM-L6-v2"):
    """Hugging Face 임베딩"""
    try:
        result = await huggingface_service.get_embeddings(texts, model)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/huggingface/qa")
async def question_answering(request: QuestionAnswerRequest):
    """Hugging Face 질문-답변"""
    try:
        result = await huggingface_service.answer_question(
            request.question, 
            request.context, 
            request.model
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/huggingface/models")
async def get_available_models():
    """사용 가능한 모델 목록"""
    try:
        result = await huggingface_service.get_available_models()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
