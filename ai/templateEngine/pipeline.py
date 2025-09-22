# templateEngine/pipeline.py

import asyncio
from typing import Dict, List
from .state import TemplateGenerationState
from .nodes import (
    classify_message_type_node,
    parallel_title_category_node,
    search_templates_node,
    extract_fields_node,
    decide_generation_method,
    generate_with_reference_node,
    search_public_and_generate_node,
    finalize_result_node
)
from services.openai_service import OpenAIService
from services.chromadb_service import ChromaDBService
from langgraph.graph import StateGraph, END
import logging

logger = logging.getLogger(__name__)

async def create_pipeline() -> StateGraph:
    workflow = StateGraph(TemplateGenerationState)
    workflow.add_node("classify_type", classify_message_type_node)
    workflow.add_node("title_category_parallel", parallel_title_category_node)
    workflow.add_node("search_templates", search_templates_node)
    workflow.add_node("extract_fields", extract_fields_node)
    workflow.add_node("generate_with_reference", generate_with_reference_node)
    workflow.add_node("search_public_and_generate", search_public_and_generate_node)
    workflow.add_node("finalize_result", finalize_result_node)

    workflow.set_entry_point("classify_type")
    workflow.add_edge("classify_type", "title_category_parallel")
    workflow.add_edge("title_category_parallel", "search_templates")
    workflow.add_edge("search_templates", "extract_fields")
    workflow.add_conditional_edges(
        "extract_fields",
        decide_generation_method,
        {"with_reference": "generate_with_reference", "search_public": "search_public_and_generate"}
    )
    workflow.add_edge("generate_with_reference", "finalize_result")
    workflow.add_edge("search_public_and_generate", "finalize_result")
    workflow.add_edge("finalize_result", END)

    return workflow.compile()

async def run_template_generation_pipeline(
        userMessage: str,
        category_sub_list: List[str],
        openai_service: OpenAIService, # 👈 의존성 주입으로 받음
        chromadb_service: ChromaDBService # 👈 의존성 주입으로 받음
) -> Dict:
    """템플릿 생성 파이프라인 실행 및 예외 처리"""
    logger.info("=" * 80)
    logger.info("카카오 알림톡 템플릿 생성 파이프라인 시작")
    try:
        app = await create_pipeline()
        """
        initial_state
        - 파이프라인 처리용 내부 컨테이너
        - 파이프라인 각 단계에서 데이터가 오가고 누적되는 임시 컨테이너 역할
        - 최종적으로 사용자에게 반환할 데이터(GenerationResponse)보다 더 많은 정보가 들어있어도 문제 없음.
        """
        initial_state = {
            "userMessage": userMessage,
            "category_sub_list": category_sub_list,
            "openai_service": openai_service,
            "chromadb_service": chromadb_service,
            "message_type_result": None,
            "category_result": None,
            "generated_title": None,
            "similar_templates": [],
            "max_similarity": 0.0,
            "pulblic_templates": [],
            "generation_hint": None,
            "generated_template": "",
            "extracted_fields": {},
            "final_result": {}
        }
        logger.info("파이프라인 실행 시작")
        final_state = await app.ainvoke(initial_state)
        logger.info("=" * 80)
        logger.info("파이프라인 실행 완료!")
        return final_state.get("final_result", {})
    except Exception as e:
        logger.error(f"❌ 파이프라인 전체 실행 실패: {e}", exc_info=True)
        return {
            "pipeline_success": False,
            "error_message": f"파이프라인 실행 중 오류 발생: {str(e)}",
            "template_text": "", "template_title": "생성 실패", "variables": [],
            "generation_method": "error", "message_type": None, "category_sub": None,
            "category_analysis": None, "similarity_score": 0.0,
            "reference_templates": [], "pulblic_templates": [],
        }
