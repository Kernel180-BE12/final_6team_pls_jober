"""
알림톡 템플릿 검증 라우터
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
import traceback
import logging

try:
    from ..services.alimtalk_service import AlimtalkValidationService
    from ..models.alimtalk_models import ValidationRequest, ValidationResponse
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from services.alimtalk_service import AlimtalkValidationService
    from models.alimtalk_models import ValidationRequest, ValidationResponse

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alimtalk", tags=["알림톡 검증"])

# 전역 서비스 인스턴스
validation_service = AlimtalkValidationService()

# 초기화는 메인 앱에서 처리하므로 제거
# @router.on_event("startup") # Deprecated in FastAPI

@router.get("/")
async def get_alimtalk_info():
    """알림톡 검증 서비스 정보"""
    return {
        "service": "알림톡 템플릿 검증 시스템",
        "version": "1.0.0",
        "description": "AI 기반 2단계 알림톡 템플릿 검증 서비스",
        "stages": ["1차: 제약 검증", "2차: 의미적 검증 (RAG)"]
    }

@router.get("/health")
async def health_check():
    """알림톡 서비스 헬스 체크"""
    try:
        health_status = await validation_service.get_health_status()
        return health_status
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.post("/validate", response_model=ValidationResponse)
async def validate_template(request: ValidationRequest):
    """
    알림톡 템플릿 검증
    
    2단계 검증을 순차적으로 수행:
    1. 제약 검증 (규칙/리스트/정적 룰)
    2. 의미적 검증 (RAG 기반)
    """
    try:
        logger.info(f"검증 요청 받음: {request.user_input[:50]}...")
        
        # 검증 실행
        result = await validation_service.validate_template(request)
        
        logger.info(f"검증 완료: {'성공' if result.success else '실패'}")
        return result
        
    except Exception as e:
        logger.error(f"검증 중 오류: {e}")
        logger.error(traceback.format_exc())
        
        raise HTTPException(
            status_code=500,
            detail=f"검증 중 내부 오류가 발생했습니다: {str(e)}"
        )

@router.post("/validate/step/{step}")
async def validate_step(step: int, template_data: Dict[str, Any]):
    """
    특정 단계만 검증
    
    Args:
        step: 검증 단계 (1: 제약, 2: 의미적)
        template_data: 템플릿 데이터
    """
    try:
        if step < 1 or step > 2:
            raise HTTPException(status_code=400, detail="검증 단계는 1-2 사이여야 합니다")
        
        result = await validation_service.validate_single_step(template_data, step)
        
        step_names = {1: "제약", 2: "의미적"}
        return {
            "step": step,
            "step_name": step_names[step],
            "result": result
        }
        
    except Exception as e:
        logger.error(f"단계별 검증 중 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"검증 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/guidelines/search")
async def search_guidelines(query: str, limit: int = 10):
    """
    가이드라인 검색
    
    Args:
        query: 검색 쿼리
        limit: 결과 개수 제한
    """
    try:
        results = await validation_service.search_guidelines(query, limit)
        
        return {
            "query": query,
            "results": results,
            "total": len(results)
        }
        
    except Exception as e:
        logger.error(f"가이드라인 검색 중 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"검색 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/stats")
async def get_stats():
    """알림톡 검증 시스템 통계 정보"""
    try:
        stats = await validation_service.get_stats()
        return stats
        
    except Exception as e:
        logger.error(f"통계 조회 중 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/examples")
async def get_examples():
    """알림톡 템플릿 예시"""
    try:
        examples = await validation_service.get_template_examples()
        return examples
        
    except Exception as e:
        logger.error(f"예시 조회 중 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"예시 조회 중 오류가 발생했습니다: {str(e)}"
        )
