# templateEngine/pipeline.py

import asyncio
from typing import Dict, List
from templateEngine.state import TemplateGenerationState
# [수정] 새로운 노드들을 임포트
from templateEngine.nodes import (
    initial_analysis_node,
    generate_template_node,
    extract_blocks_node,
    finalize_node
)
from services.openai_service import OpenAIService
from services.chromadb_service import ChromaDBService
from langgraph.graph import StateGraph, END
from .prompts.message_analyzer_prompts import UnsuitableMessageError
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

async def create_pipeline() -> StateGraph:
    """
    [최종 수정] '생성 후 추출' 아키텍처에 맞는 파이프라인 구성
    """
    workflow = StateGraph(TemplateGenerationState)

    # 4개의 핵심 노드 등록
    workflow.add_node("initial_analysis", initial_analysis_node)
    workflow.add_node("generate_template", generate_template_node)
    workflow.add_node("extract_blocks", extract_blocks_node)
    workflow.add_node("finalize", finalize_node)

    # 파이프라인 순서 정의
    workflow.set_entry_point("initial_analysis")
    workflow.add_edge("initial_analysis", "generate_template")
    workflow.add_edge("generate_template", "extract_blocks")
    workflow.add_edge("extract_blocks", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile()

async def run_template_generation_pipeline(
        userMessage: str,
        openai_service: OpenAIService,
        chromadb_service: ChromaDBService,
        db_session: Session
) -> Dict:
    """
    '생성 후 추출' 파이프라인 실행 함수
    """
    logger.info("=" * 80)
    logger.info("'생성 후 추출' 파이프라인 시작")
    try:
        initial_state = {
            "userMessage": userMessage,
            "db_session": db_session,
            "openai_service": openai_service,
            "chromadb_service": chromadb_service,
            "generated_template": "",
            "extracted_fields": {},
            "final_result": {}
            # ... 기타 초기 상태값
        }

        app = await create_pipeline()
        final_state = await app.ainvoke(initial_state)

        logger.info("=" * 80)
        logger.info("파이프라인 실행 완료!")
        return final_state.get("final_result", {})
    except UnsuitableMessageError as e:
        # API 레벨에서 직접 처리해야 할 특정 예외는 그대로 다시 발생시킵니다.
        logger.warning(f"파이프라인 실행 중 제어된 예외 발생(부적합 메시지): {e}")
        raise e
    except Exception as e:
        logger.error(f"❌ 파이프라인 전체 실행 실패: {e}", exc_info=True)
        # ... (에러 처리 로직)
        return {}
