from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from services.openai_service import OpenAIService
from services.chromadb_service import ChromaDBService
from services.huggingface_service import HuggingFaceService
from templateEngine.prompts.message_analyzer_prompts import TemplateGenerationPromptBuilder, TemplateModificationPromptBuilder
from templateEngine.integrated_template_pipeline import IntegratedTemplatePipeline, IntegratedGenerationRequest, IntegratedGenerationResult

router = APIRouter(prefix="/ai", tags=["AI Services"])

# 서비스 인스턴스 초기화
openai_service = OpenAIService()
chromadb_service = ChromaDBService()
huggingface_service = HuggingFaceService()
integrated_pipeline = IntegratedTemplatePipeline()

# Pydantic 모델들
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "gpt-4o-mini"

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

class TemplateGenerationRequest(BaseModel):
    category: str
    user_message: str
    model: Optional[str] = "gpt-4o-mini"

class TemplateGenerationResponse(BaseModel):
    template_content: str
    variables: List[Dict[str, Any]]
    category: str
    model: str

class TemplateModificationRequest(BaseModel):
    current_template: str
    user_message: str
    chat_history: List[Dict[str, Any]] = []

class TemplateModificationResponse(BaseModel):
    modified_template: str
    variables: List[Dict[str, Any]]
    explanation: str
    model: str

class IntegratedTemplateRequest(BaseModel):
    user_text: str
    category_main: str
    category_sub_list: List[str]
    model: Optional[str] = "gpt-4o-mini"

class IntegratedTemplateResponse(BaseModel):
    template_text: str
    template_title: str
    generation_method: str
    reference_templates: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

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

# 템플릿 생성 라우트
@router.post("/template/generate", response_model=TemplateGenerationResponse)
async def generate_template(request: TemplateGenerationRequest):
    """알림톡 템플릿 생성"""
    try:
        # 가이드라인 검색을 통한 컨텍스트 생성
        try:
            guidelines = await chromadb_service.search_documents(
                f"{request.category} {request.user_message}", 
                3
            )
        except Exception as e:
            print(f"가이드라인 검색 실패: {e}")
            guidelines = {"documents": []}
        
        # 프롬프트 구성
        context = ""
        if guidelines and 'documents' in guidelines:
            context = "\n".join(guidelines['documents'][:3])
        
        # 프롬프트 빌더 사용
        prompt_builder = TemplateGenerationPromptBuilder(
            category=request.category,
            user_message=request.user_message,
            context=context
        )
        prompt = prompt_builder.build()
        
        # OpenAI를 통한 템플릿 생성
        messages = [{"role": "user", "content": prompt}]
        response = await openai_service.chat_completion(messages, request.model)
        
        # 응답에서 템플릿과 변수 추출 (간단한 파싱)
        template_content = response
        variables = []
        
        # 변수 추출 ({{변수명}} 형태)
        import re
        variable_pattern = r'\{\{([^}]+)\}\}'
        found_variables = re.findall(variable_pattern, response)
        
        for var in set(found_variables):
            variables.append({
                "name": var.strip(),
                "type": "string",
                "description": f"{var} 관련 정보"
            })
        
        return TemplateGenerationResponse(
            template_content=template_content,
            variables=variables,
            category=request.category,
            model=request.model
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 템플릿 수정 라우트
@router.post("/template/modify", response_model=TemplateModificationResponse)
async def modify_template(request: TemplateModificationRequest):
    """채팅을 통한 템플릿 수정"""
    try:
        # 채팅 히스토리를 포함한 프롬프트 구성
        chat_context = ""
        if request.chat_history:
            chat_context = "\n".join([
                f"{msg.get('type', 'user')}: {msg.get('content', '')}" 
                for msg in request.chat_history[-5:]  # 최근 5개 메시지만 사용
            ])
        
        # 프롬프트 빌더 사용
        prompt_builder = TemplateModificationPromptBuilder(
            current_template=request.current_template,
            user_message=request.user_message,
            chat_context=chat_context
        )
        prompt = prompt_builder.build()
        
        # OpenAI를 통한 템플릿 수정
        messages = [{"role": "user", "content": prompt}]
        response = await openai_service.chat_completion(messages, "gpt-4o-mini")
        
        # 응답에서 템플릿과 변수 추출
        modified_template = response
        variables = []
        
        # 변수 추출 ({{변수명}} 형태)
        import re
        variable_pattern = r'\{\{([^}]+)\}\}'
        found_variables = re.findall(variable_pattern, response)
        
        for var in set(found_variables):
            variables.append({
                "name": var.strip(),
                "type": "string",
                "description": f"{var} 관련 정보"
            })
        
        # 수정 설명 생성
        explanation = f"사용자 요청 '{request.user_message}'에 따라 템플릿을 수정했습니다."
        
        return TemplateModificationResponse(
            modified_template=modified_template,
            variables=variables,
            explanation=explanation,
            model="gpt-4o-mini"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 통합 템플릿 생성 라우트 (요구사항에 맞는 4단계 흐름)
@router.post("/template/integrated-generate", response_model=IntegratedTemplateResponse)
async def integrated_generate_template(request: IntegratedTemplateRequest):
    """통합된 4단계 템플릿 생성 API"""
    try:
        # 통합 파이프라인 초기화
        await integrated_pipeline.initialize()
        
        # 통합 생성 요청 객체 생성
        generation_request = IntegratedGenerationRequest(
            user_text=request.user_text,
            category_main=request.category_main,
            category_sub_list=request.category_sub_list,
            model=request.model
        )
        
        # 통합 파이프라인 실행
        result = await integrated_pipeline.generate_template(generation_request)
        
        return IntegratedTemplateResponse(
            template_text=result.template_text,
            template_title=result.template_title,
            generation_method=result.generation_method,
            reference_templates=result.reference_templates,
            metadata=result.metadata,
            success=result.success,
            error_message=result.error_message
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
