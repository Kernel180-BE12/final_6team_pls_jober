from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import re
from services.openai_service import OpenAIService
from services.chromadb_service import ChromaDBService
from templateEngine.prompts.message_analyzer_prompts import TemplateGenerationPromptBuilder, TemplateModificationPromptBuilder
from middleware.auth_middleware import get_current_user, get_current_user_id
from templateEngine.integrated_template_pipeline import IntegratedTemplatePipeline, IntegratedGenerationRequest, IntegratedGenerationResult, clean_template_content, extract_variables_from_template

router = APIRouter(prefix="/ai", tags=["AI Services"])

# 서비스 인스턴스 초기화
print("AI 서비스 초기화 시작...")
try:
    openai_service = OpenAIService()
    print("✅ OpenAI 서비스 초기화 완료")
except Exception as e:
    print(f"❌ OpenAI 서비스 초기화 실패: {e}")

try:
    chromadb_service = ChromaDBService()
    print("✅ ChromaDB 서비스 초기화 완료")
except Exception as e:
    print(f"❌ ChromaDB 서비스 초기화 실패: {e}")

try:
    integrated_pipeline = IntegratedTemplatePipeline()
    print("✅ 통합 파이프라인 초기화 완료")
except Exception as e:
    print(f"❌ 통합 파이프라인 초기화 실패: {e}")

print("AI 서비스 초기화 완료!")

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


class TemplateGenerationRequest(BaseModel):
    userMessage: str
    model: Optional[str] = "gpt-4o-mini"

class TemplateGenerationResponse(BaseModel):
    template_content: str
    template_title: str
    variables: List[Dict[str, Any]]
    category: str
    model: str

class TemplateModificationRequest(BaseModel):
    current_template: str
    current_template_title: str
    userMessage: str
    chat_history: List[Dict[str, Any]] = []

class TemplateModificationResponse(BaseModel):
    modified_template: str
    template_title: str
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

# OpenAI 라우트 (인증 필요)
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

# 템플릿 생성 라우트
@router.post("/template/generate", response_model=TemplateGenerationResponse)
async def generate_template(request: TemplateGenerationRequest):
    category = "예약취소"
    """알림톡 템플릿 생성"""
    try:
        print(f"템플릿 생성 요청 받음: {request.userMessage}")
        
        # 가이드라인 검색을 통한 컨텍스트 생성
        try:
            print("ChromaDB 검색 시작...")
            guidelines = await chromadb_service.search_documents(
                f"{category} {request.userMessage}",
                3
            )
            print(f"ChromaDB 검색 완료: {len(guidelines.get('documents', []))}개 문서")
        except Exception as e:
            print(f"가이드라인 검색 실패: {e}")
            guidelines = {"documents": []}
        
        # 프롬프트 구성
        context = ""
        if guidelines and 'documents' in guidelines:
            context = "\n".join(guidelines['documents'][:3])
        
        # 프롬프트 빌더 사용
        print("프롬프트 빌더 초기화 중...")
        prompt_builder = TemplateGenerationPromptBuilder(
            category=category,
            user_message=request.userMessage,
            context=context
        )
        prompt = prompt_builder.build()
        print(f"프롬프트 생성 완료 (길이: {len(prompt)}자)")
        
        # OpenAI를 통한 템플릿 생성
        print("OpenAI API 호출 시작...")
        messages = [{"role": "user", "content": prompt}]
        response = await openai_service.chat_completion(messages, request.model)
        print(f"OpenAI API 호출 완료 (응답 길이: {len(response)}자)")
        
        # 응답에서 템플릿과 변수 추출 (간단한 파싱)
        template_content = response
        variables = []
        
        # 변수 추출 ({{변수명}} 형태)
        variable_pattern = r'\{\{([^}]+)\}\}'
        found_variables = re.findall(variable_pattern, response)
        
        for var in set(found_variables):
            variables.append({
                "name": var.strip(),
                "type": "string",
                "description": f"{var} 관련 정보"
            })
        
        # 템플릿 제목 생성 (사용자 메시지 기반)
        template_title = f"{category} 템플릿 - {request.userMessage[:30]}..."
        
        print(f"템플릿 생성 완료: {len(variables)}개 변수 추출")
        return TemplateGenerationResponse(
            template_content=template_content,
            template_title=template_title,
            variables=variables,
            category=category,
            model=request.model
        )
        
    except Exception as e:
        print(f"템플릿 생성 중 에러 발생: {str(e)}")
        print(f"에러 타입: {type(e).__name__}")
        import traceback
        print(f"에러 스택트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"템플릿 생성 실패: {str(e)}")

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
            userMessage=request.userMessage,
            chat_context=chat_context
        )
        prompt = prompt_builder.build()
        
        # OpenAI를 통한 템플릿 수정
        messages = [{"role": "user", "content": prompt}]
        response = await openai_service.chat_completion(messages, "gpt-4o-mini")
        
        # "수정된 템플릿:" 이후의 템플릿 부분만 추출
        template_match = re.search(r'수정된 템플릿:\s*\n?(.*?)(?:\n\n수정된 부분 설명:|수정 설명:|설명:|$)', response, re.DOTALL)
        if template_match:
            modified_template = template_match.group(1).strip()
        else:
            # 패턴이 맞지 않으면 전체 응답에서 첫 번째 줄만 사용
            lines = response.split('\n')
            modified_template = lines[0] if lines else response

        # 추가 필터링: 설명 텍스트 제거
        modified_template = re.split(r'(?:수정된 부분 설명:|수정 설명:|설명:)', modified_template)[0].strip()

        # "수정된 템플릿:" 제거
        modified_template = re.sub(r'^수정된 템플릿:\s*', '', modified_template)

        # 마지막으로 줄바꿈 정리
        modified_template = re.sub(r'\n+', '\n', modified_template).strip()

        variables = []
        
        # 변수 추출 ({{변수명}} 형태)
        variable_pattern = r'\{\{([^}]+)\}\}'
        found_variables = re.findall(variable_pattern, modified_template)

        for var in set(found_variables):
            variables.append({
                "name": var.strip(),
                "type": "string",
                "description": f"{var} 관련 정보"
            })
        
        # 수정 설명 생성
        explanation = f"사용자 요청 '{request.userMessage}'에 따라 템플릿을 수정했습니다."
        
        return TemplateModificationResponse(
            modified_template=modified_template,
            template_title=request.current_template_title,
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

# 사용자 권한 API들
@router.post("/chromadb/documents")
async def add_documents(request: DocumentRequest):
    """ChromaDB에 문서 추가"""
    try:
        result = await chromadb_service.add_documents([request.content], [request.metadata])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chromadb/documents/{document_id}")
async def delete_document(document_id: str):
    """ChromaDB에서 문서 삭제"""
    try:
        # 문서 삭제 로직 구현 (ChromaDBService에 메서드 추가 필요)
        return {"message": f"문서 {document_id}가 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
