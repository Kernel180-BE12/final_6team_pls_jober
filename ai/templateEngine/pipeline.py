# templateEngine/pipeline.py

import asyncio
from typing import Dict, List
from templateEngine.state import TemplateGenerationState
from templateEngine.nodes import (
    check_message_suitability_node,
    parallel_tasks_node,
    search_templates_node,
    decide_generation_method,
    generate_with_reference_node,
    search_public_and_generate_node,
    finalize_result_node
)
from services.openai_service import OpenAIService
from services.chromadb_service import ChromaDBService
from langgraph.graph import StateGraph, END
from .prompts.message_analyzer_prompts import UnsuitableMessageError
import logging
from core.database import SessionLocal
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

async def create_pipeline() -> StateGraph:
    workflow = StateGraph(TemplateGenerationState)
    
    # 노드 등록
    workflow.add_node("check_suitability", check_message_suitability_node)
    workflow.add_node("parallel_tasks", parallel_tasks_node)
    workflow.add_node("search_templates", search_templates_node)
    workflow.add_node("generate_with_reference", generate_with_reference_node)
    workflow.add_node("search_public_and_generate", search_public_and_generate_node)
    workflow.add_node("finalize_result", finalize_result_node)

    # 워크플로우 흐름 구성
    workflow.set_entry_point("check_suitability")
    workflow.add_edge("check_suitability", "parallel_tasks")
    workflow.add_edge("parallel_tasks", "search_templates")
    workflow.add_conditional_edges(
        "search_templates",
        decide_generation_method,
        {
            "with_reference": "generate_with_reference",
            "search_public": "search_public_and_generate"
        }
    )
    workflow.add_edge("generate_with_reference", "finalize_result")
    workflow.add_edge("search_public_and_generate", "finalize_result")
    workflow.add_edge("finalize_result", END)

    return workflow.compile()

async def run_template_generation_pipeline(
        userMessage: str,
        openai_service: OpenAIService, # 👈 의존성 주입으로 받음
        chromadb_service: ChromaDBService, # 👈 의존성 주입으로 받음
        db_session: Session # [수정] Depends(get_db)는 라우터에서 처리하므로 여기서는 Session 타입만 명시
) -> Dict:
    """DB 연동된 템플릿 생성 파이프라인"""
    logger.info("=" * 80)
    logger.info("DB 연동 카카오 알림톡 템플릿 생성 파이프라인 시작")
    try:
        # [수정] CategoryService(DB 카데고리 관리) 관련 로직은 이제 노드 내부로 이동했으므로 삭제합니다.
        # category_service = CategoryService(db_session)
        # current_categories = await category_service.get_all_categories()

        initial_state = {
            "userMessage": userMessage,
            "db_session": db_session,
            "openai_service": openai_service,
            "chromadb_service": chromadb_service,
            "suitability_check_result": None,
            "message_type_result": None,
            "category_result": None,
            "generated_title": None,
            "similar_templates": [],
            "max_similarity": 0.0,
            "public_templates": [],
            "generation_hint": None,
            "generated_template": "",
            "extracted_fields": {},
            "final_result": {}
        }

        app = await create_pipeline()  # 기존 파이프라인 또는 최적화된 파이프라인
        final_state = await app.ainvoke(initial_state)

        logger.info("=" * 80)
        logger.info("DB 연동 파이프라인 실행 완료!")
        return final_state.get("final_result", {})
    except UnsuitableMessageError as e:
        # API 레벨에서 직접 처리해야 할 특정 예외는 그대로 다시 발생시킵니다.
        logger.warning(f"파이프라인 실행 중 제어된 예외 발생(부적합 메시지): {e}")
        raise e
    except Exception as e:
        logger.error(f"❌ DB 연동 파이프라인 실행 실패: {e}", exc_info=True)
        return {
            "pipeline_success": False,
            "error_message": f"파이프라인 실행 중 오류 발생: {str(e)}",
            "template_text": "", "template_title": "생성 실패", "variables": [],
            "generation_method": "error", "message_type": None, "category_sub": None,
            "category_analysis": None, "similarity_score": 0.0,
            "reference_templates": [], "public_templates": [],
        }
