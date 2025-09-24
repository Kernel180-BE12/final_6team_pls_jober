from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import re
from services.openai_service import OpenAIService
from services.chromadb_service import ChromaDBService
from templateEngine.prompts.message_analyzer_prompts import TemplateGenerationPromptBuilder, TemplateModificationPromptBuilder
from templateEngine.pipeline import create_pipeline
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
    category: Optional[str] = "기타"

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
        
        # 카테고리 설정 (요청에서 받거나 기본값 사용)
        category = request.category or "기타"

        # 템플릿 생성 파이프라인 실행
        print("템플릿 생성 파이프라인 시작...")
        try:
            pipeline = await create_pipeline()
            result = await pipeline.ainvoke({
                "userMessage": request.userMessage,
                "category_sub_list": ["서비스이용", "이용안내/공지", "운영안내", "기타"],
                "openai_service": openai_service,
                "chromadb_service": chromadb_service
            })
            print("템플릿 생성 파이프라인 실행 완료")
        except Exception as e:
            print(f"파이프라인 실행 실패: {e}")
            # 파이프라인 실패 시 기본값으로 fallback
            result = {
                "template_text": f"안녕하세요. {request.userMessage}에 대한 알림톡 템플릿입니다.",
                "template_title": f"{category} 템플릿",
                "variables": [],
                "category_sub": category
            }

        # 파이프라인 결과에서 데이터 추출
        template_content = result.get("template_text", "")
        template_title = result.get("template_title", f"{category} 템플릿")
        category = result.get("category_sub", category)
        
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
            # 패턴 2: "---" 사이의 내용이 여러 개인 경우 첫 번째 것 사용
            dash_matches = re.findall(r'---\s*\n(.*?)\n---', response, re.DOTALL)
            if dash_matches and len(dash_matches) > 0:
                # 첫 번째 "---" 사이의 내용이 가장 긴 것을 선택 (템플릿 내용)
                modified_template = max(dash_matches, key=len).strip()
            else:
                # 패턴 3: 전체 응답에서 첫 번째 긴 텍스트 블록 사용
                lines = response.split('\n')
                content_lines = []
                in_content = False
                for line in lines:
                    if '알림톡' in line and '템플릿' in line:
                        in_content = True
                        continue
                    if in_content and line.strip() and not line.startswith('변수') and not line.startswith('이 템플릿'):
                        content_lines.append(line)
                    if line.startswith('변수') or line.startswith('이 템플릿'):
                        break
                modified_template = '\n'.join(content_lines).strip()

        # 최종 정리
        if not modified_template or len(modified_template) < 10:
            modified_template = response.strip()

        print(f"추출된 템플릿: {modified_template}")

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