# api/routes/template_routes.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from core.constants import APPROVED_SUB_CATEGORIES
from services.dependencies import get_openai_service, get_chromadb_service
from services.openai_service import OpenAIService
from services.chromadb_service import ChromaDBService
from templateEngine.pipeline import run_template_generation_pipeline
from templateEngine.prompts.message_analyzer_prompts import PromptDefense, UnsuitableMessageError

router = APIRouter(prefix="/template", tags=["Template Generation"])

# --- Pydantic 모델 ---
class GenerationRequest(BaseModel):
    userMessage: str

class GenerationResponse(BaseModel):
    template_content: str
    variables: List[Dict[str, str]]
    category: str
    model: str
    template_title: str
    generation_method: str
    similarity_score: float

# --- 최종 API 엔드포인트 ---
@router.post("/generate", response_model=GenerationResponse)
async def generate_template_endpoint(
        request: GenerationRequest,
        openai_service: OpenAIService = Depends(get_openai_service),
        chromadb_service: ChromaDBService = Depends(get_chromadb_service)
):
    """
    LangGraph 기반의 지능형 템플릿 생성 파이프라인을 실행합니다.
    """
    try:
        sanitize_userMessage = PromptDefense.sanitize_user_input(request.userMessage)

        result = await run_template_generation_pipeline(
            userMessage=sanitize_userMessage,
            category_sub_list=APPROVED_SUB_CATEGORIES,
            openai_service=openai_service,
            chromadb_service=chromadb_service
        )

        if not result.get("pipeline_success", False):
            # 파이프라인 내부에서 정상적으로 종료되었지만 실패한 경우
            raise HTTPException(status_code=400, detail=result.get("error_message", "템플릿 생성에 실패했습니다."))

        # 프론트엔드 형식에 맞게 변환
        response_data = {
            "template_content": result.get("template_text", ""),
            "variables": [
                {"name": var, "type": "string", "description": f"변수: {var}"}
                for var in result.get("variables", [])
            ],
            "category": result.get("category_sub", "기타"),
            "model": "gpt-4o-mini",
            "template_title": result.get("template_title", ""),
            "generation_method": result.get("generation_method", ""),
            "similarity_score": result.get("similarity_score", 0.0)
        }
        
        return GenerationResponse(**response_data)
    
    except UnsuitableMessageError as e:
        # 적합성 검사 실패 시, 400 에러와 함께 명확한 메시지 반환
        raise HTTPException(status_code=400, detail=str(e))
 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API 엔드포인트 오류: {str(e)}")


