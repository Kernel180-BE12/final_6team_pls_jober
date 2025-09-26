from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
import re
from services.openai_service import OpenAIService
from services.chromadb_service import ChromaDBService
from templateEngine.prompts.message_analyzer_prompts import TemplateGenerationPromptBuilder, TemplateModificationPromptBuilder
from templateEngine.pipeline import create_pipeline
from middleware.auth_middleware import get_current_user
from services.dependencies import get_openai_service
from models.alimtalk_models import (
    ChatRequest, ChatResponse, 
    TemplateModificationRequest, TemplateModificationResponse
)

router = APIRouter(prefix="/ai", tags=["AI Services"])

# OpenAI 라우트 (의존성 주입 사용)
@router.post("/openai/chat", response_model=ChatResponse)
async def openai_chat(
    request: ChatRequest,
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """OpenAI 채팅 API"""
    try:
        messages = [{"role": "user", "content": request.message}]
        response = await openai_service.chat_completion(messages, request.model)
        return ChatResponse(response=response, model=request.model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 템플릿 수정 라우트
@router.post("/template/modify", response_model=TemplateModificationResponse)
async def modify_template(
    request: TemplateModificationRequest,
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """채팅을 통한 템플릿 수정"""
    try:
        # 채팅 히스토리를 포함한 프롬프트 구성
        chat_context = ""
        if request.chat_history:
            chat_context = "\n".join([
                f"[{msg.get('type', 'user')}] {msg.get('content', '')}"
                for msg in request.chat_history[-6:]  # 최근 6개 메시지만 사용
            ])
            print(f"채팅 히스토리 ({len(request.chat_history)}개 메시지): {chat_context}")
        else:
            print("채팅 히스토리가 없습니다.")

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


