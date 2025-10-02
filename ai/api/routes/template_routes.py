# api/routes/template_routes.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from core.database import get_db
from sqlalchemy.orm import Session
from core.database import get_db
import logging

from services.dependencies import get_openai_service, get_chromadb_service
from services.openai_service import OpenAIService
from services.category_service import CategoryService
from services.chromadb_service import ChromaDBService
from templateEngine.pipeline import run_template_generation_pipeline
from core.database import SessionLocal
from templateEngine.prompts.message_analyzer_prompts import PromptDefense, UnsuitableMessageError
from templateEngine.prompts.builders import SuitabilityCheckPromptBuilder

router = APIRouter(prefix="/template", tags=["Template Generation"])
logger = logging.getLogger(__name__)

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
        db_session: Session = Depends(get_db), # db 세션 Depends로 주입
        openai_service: OpenAIService = Depends(get_openai_service),
        chromadb_service: ChromaDBService = Depends(get_chromadb_service)
):
    """
    LangGraph 기반의 지능형 템플릿 생성 파이프라인을 실행합니다.
    """
    # [삭제] CategoryService를 여기서 직접 호출할 필요가 없습니다.
    # category_service = CategoryService(db_session)
    # category_sub_list= await category_service.get_all_categories()
    try:
        sanitize_userMessage = PromptDefense.sanitize_user_input(request.userMessage)

        # 적합성 검사 수행
        suitability_builder = SuitabilityCheckPromptBuilder(sanitize_userMessage)
        suitability_messages = suitability_builder.build()
        suitability_result = await openai_service.chat_completion(suitability_messages)
        
        # JSON 파싱하여 적합성 확인
        import json
        try:
            suitability_data = json.loads(suitability_result)
            if not suitability_data.get("is_suitable", True):
                # 부적합한 메시지인 경우 에러 반환
                reason = suitability_data.get("reason", "메시지가 알림톡 템플릿 생성에 적합하지 않습니다.")
                raise HTTPException(status_code=400, detail=f"부적합한 메시지: {reason}")
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 로그만 남기고 계속 진행
            logger.warning(f"적합성 검사 응답 파싱 실패: {suitability_result}")

        result = await run_template_generation_pipeline(
            userMessage=sanitize_userMessage,
            openai_service=openai_service,
            chromadb_service=chromadb_service,
            db_session=db_session  # <--- db_session을 전달합니다.
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
            "category": result.get("category_sub") or "기타",
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
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"API 엔드포인트 오류: {str(e)}")


