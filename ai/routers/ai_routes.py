from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import re
from services.openai_service import OpenAIService
from services.chromadb_service import ChromaDBService
from templateEngine.prompts.message_analyzer_prompts import TemplateGenerationPromptBuilder, TemplateModificationPromptBuilder
from middleware.auth_middleware import get_current_user

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
    variables: List[Dict[str, str]]
    category: str
    model: str

class TemplateModificationRequest(BaseModel):
    current_template: str
    current_template_title: str
    userMessage: str
    chat_history: List[Dict[str, Any]] = []
    variableList: List[str] = []

class TemplateModificationResponse(BaseModel):
    modified_template: str
    template_title: str
    variables: List[str]
    explanation: str
    model: str


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
    """알림톡 템플릿 생성"""
    try:
        print(f"템플릿 생성 요청 받음: {request.userMessage}")

        # 기존 파이프라인을 사용하여 템플릿 생성
        from templateEngine.pipeline import run_template_generation_pipeline
        from core.constants import APPROVED_SUB_CATEGORIES
        
        print("템플릿 생성 파이프라인 실행 시작...")
        result = await run_template_generation_pipeline(
            userMessage=request.userMessage,
            category_sub_list=APPROVED_SUB_CATEGORIES,
            openai_service=openai_service,
            chromadb_service=chromadb_service
        )
        print("템플릿 생성 파이프라인 실행 완료")

        # 파이프라인 결과에서 데이터 추출
        template_content = result.get("template_text", "")
        category = result.get("category_sub", "기타")
        template_title = result.get("template_title", f"{category} 템플릿")
        
        # 변수 추출 및 변환
        variables = []
        raw_variables = result.get("variables", [])
        
        # 변수 추출 (#{변수명} 형태)
        variable_pattern = r'#\{([^}]+)\}'
        found_variables = re.findall(variable_pattern, template_content)

        # ✅ TemplateGenerationResponse 구조에 맞게 변수 변환
        variables_dto = []
        for var in set(found_variables):
            variables_dto.append({
                "name": var.strip(),
                "type": "string",
                "description": f"{var.strip()} 변수"
            })
        
        # 템플릿 제목 생성 (사용자 메시지 기반)
        template_title = f"{category} 템플릿 - {request.userMessage[:30]}..."
        
        print(f"템플릿 생성 완료: {len(variables_dto)}개 변수 추출")
        
        return TemplateGenerationResponse(
            template_content=template_content,
            template_title=template_title,
            variables=variables_dto,
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
                for msg in request.chat_history[-6:]  # 최근 6개 메시지만 사용
            ])

        # 프롬프트 빌더 사용
        prompt_builder = TemplateModificationPromptBuilder(
            current_template=request.current_template,
            user_message=request.userMessage,
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
        
        # 변수 추출 (#{변수명} 형태)
        variable_pattern = r'#\{([^}]+)\}'
        found_variables = re.findall(variable_pattern, modified_template)

        for var in set(found_variables):
            variables.append(var.strip())
        
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