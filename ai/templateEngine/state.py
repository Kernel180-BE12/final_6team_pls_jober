# state.py
from typing import TypedDict, List, Literal, Optional, Dict, Any
from services.chromadb_service import ChromaDBService
from services.openai_service import OpenAIService
from services.category_service import CategoryService
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class TemplateGenerationState(TypedDict):
    # 입력
    userMessage: str
    category_sub_list: List[str]  # 이제 더 이상 하드코딩 리스트가 아님

    # 서비스 객체
    openai_service: OpenAIService
    chromadb_service: ChromaDBService
    db_session: Session  # 👈 DB 세션 추가

    # 처리 결과
    suitability_check_result: Optional[Dict]
    message_type_result: Optional[Dict]
    category_result: Optional[Dict]  # category_id도 포함됨
    generated_title: Optional[str]
    similar_templates: List[Dict]
    max_similarity: float
    public_templates: List[Dict]
    generation_hint: Optional[str]
    generated_template: str
    extracted_fields: Optional[Dict[str, Any]]

    # 최종 결과
    final_result: Dict


# 파이프라인 호출 시 DB 세션 전달 예시
# templateEngine/pipeline_with_db.py

async def run_template_generation_pipeline_with_db(
        userMessage: str,
        openai_service: OpenAIService,
        chromadb_service: ChromaDBService,
        db_session: Session  # 👈 DB 세션 추가
) -> Dict:
    """DB 연동된 템플릿 생성 파이프라인"""
    logger.info("=" * 80)
    logger.info("DB 연동 카카오 알림톡 템플릿 생성 파이프라인 시작")

    try:
        # CategoryService로 현재 카테고리 목록 조회 (더 이상 하드코딩 불필요)
        category_service = CategoryService(db_session)
        current_categories = await category_service.get_all_categories()

        initial_state = {
            "userMessage": userMessage,
            "category_sub_list": current_categories,  # DB에서 조회한 최신 목록
            "openai_service": openai_service,
            "chromadb_service": chromadb_service,
            "db_session": db_session,  # 👈 DB 세션 전달
            # ... 기타 초기값들
        }

        # 순환 import 방지를 위해 함수 내에서 동적 import
        from .pipeline import create_pipeline
        app = await create_pipeline()  # 기존 파이프라인 또는 최적화된 파이프라인
        final_state = await app.ainvoke(initial_state)

        logger.info("=" * 80)
        logger.info("DB 연동 파이프라인 실행 완료!")
        return final_state.get("final_result", {})

    except Exception as e:
        logger.error(f"❌ DB 연동 파이프라인 실행 실패: {e}", exc_info=True)
        return {
            "pipeline_success": False,
            "error_message": f"파이프라인 실행 중 오류 발생: {str(e)}",
            # ... 기타 에러 응답
        }