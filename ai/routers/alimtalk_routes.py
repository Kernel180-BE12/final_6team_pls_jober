"""
알림톡 템플릿 검증 라우터
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
import traceback
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.alimtalk_service import AlimtalkValidationService
from models.alimtalk_models import ValidationRequest, ValidationResponse

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["알림톡 검증"])

# 전역 서비스 인스턴스
validation_service = AlimtalkValidationService()


@router.post("/template/validate")
async def validate_template(backend_request: Dict[str, Any]):
    """
    알림톡 템플릿 검증
    
    2단계 검증을 순차적으로 수행:
    1. 제약 검증 (규칙/리스트/정적 룰)
    2. 의미적 검증 (RAG 기반)
    
    백엔드가 기대하는 형식으로 응답을 변환하여 반환합니다.
    """
    try:
        logger.info(f"검증 요청 받음: {backend_request}")
        
        # 백엔드 요청을 ValidationRequest로 변환
        request = ValidationRequest.from_backend_request(backend_request)
        
        logger.info(f"변환된 요청: user_input={request.user_input[:50]}..., template_content={request.template.template_content[:50]}...")
        
        # 검증 실행
        result = await validation_service.validate_template(request)
        
        logger.info(f"검증 완료: {'성공' if result.success else '실패'}")
        logger.info(f"응답 데이터: success={result.success}, problem_areas={len(result.problem_areas)}, total_errors={result.total_errors}, total_warnings={result.total_warnings}")
        
        # ValidationResponse가 이미 백엔드 구조와 일치하므로 직접 반환
        return result
        
    except Exception as e:
        logger.error(f"검증 중 오류: {e}")
        logger.error(traceback.format_exc())
        
        # 오류 발생 시 문제 영역 기반 오류 응답 반환
        return {
            "success": False,
            "message": f"검증 중 내부 오류가 발생했습니다: {str(e)}",
            "problem_areas": [],
            "validation_stage": "오류",
            "total_errors": 0,
            "total_warnings": 0
        }