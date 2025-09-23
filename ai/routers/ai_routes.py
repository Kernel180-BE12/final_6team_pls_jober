from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import re
from services.openai_service import OpenAIService
from templateEngine.prompts.message_analyzer_prompts import TemplateModificationPromptBuilder
from middleware.auth_middleware import get_current_user, get_current_user_id

router = APIRouter(prefix="/ai", tags=["AI Services"])

# 서비스 인스턴스 초기화
print("AI 서비스 초기화 시작...")
try:
    openai_service = OpenAIService()
    print("✅ OpenAI 서비스 초기화 완료")
except Exception as e:
    print(f"❌ OpenAI 서비스 초기화 실패: {e}")

print("AI 서비스 초기화 완료!")

# Pydantic 모델들
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "gpt-4o-mini"

class ChatResponse(BaseModel):
    response: str
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

