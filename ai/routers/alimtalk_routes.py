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

@router.post("/validate")
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
        
        # 백엔드가 기대하는 형식으로 응답 변환
        backend_response = convert_to_backend_format(result, request)
        
        return backend_response
        
    except Exception as e:
        logger.error(f"검증 중 오류: {e}")
        logger.error(traceback.format_exc())
        
        # 오류 발생 시 백엔드 형식으로 오류 응답 반환
        return {
            "success": False,
            "message": f"검증 중 내부 오류가 발생했습니다: {str(e)}",
            "rejected_variables": [],
            "validation_errors": [],
            "alternatives": {
                "message": ["시스템 오류가 발생했습니다. 다시 시도해주세요."]
            }
        }

def convert_to_backend_format(validation_result: ValidationResponse, request: ValidationRequest) -> Dict[str, Any]:
    """
    AI 서버의 ValidationResponse를 백엔드가 기대하는 형식으로 변환
    
    백엔드가 기대하는 형식:
    {
        "success": bool,
        "message": str,
        "rejected_variables": List[str],
        "validation_errors": List[Dict],
        "alternatives": Dict[str, List[str]]
    }
    """
    try:
        # 기본 응답 구조
        response = {
            "success": validation_result.success,
            "message": validation_result.final_message,
            "rejected_variables": [],
            "validation_errors": [],
            "alternatives": {}
        }
        
        if not validation_result.success:
            # 검증 실패 시 상세 정보 추출
            validation_errors = []
            
            # 각 검증 결과에서 오류 정보 수집
            for result in validation_result.validation_results:
                for error in result.errors:
                    # 검증 오류 상세 정보 추가
                    validation_errors.append({
                        "rule_type": f"{result.stage}_validation",
                        "rule": "알림톡 승인 규칙",
                        "reason": error,
                        "suggestion": "AI에서 생성된 수정 제안을 참고해주세요",
                        "severity": "error",
                        "variable_name": None,
                        "stage": result.stage
                    })
            
            response["rejected_variables"] = []
            response["validation_errors"] = validation_errors
            
            # 대안 추천은 AI에서 생성하므로 여기서는 빈 객체로 설정
            response["alternatives"] = {}
        
        # 백엔드가 기대하는 validation_results 필드도 추가
        if not validation_result.success:
            response["validation_results"] = [{
                "is_valid": False,
                "validator_name": "constraint_validator",
                "stage": "constraint",
                "errors": [error["reason"] for error in validation_errors],
                "details": {
                    "validation_details": validation_errors
                }
            }]
        
        return response
        
    except Exception as e:
        logger.error(f"응답 변환 중 오류: {e}")
        return {
            "success": False,
            "message": f"응답 변환 중 오류가 발생했습니다: {str(e)}",
            "rejected_variables": [],
            "validation_errors": [],
            "alternatives": {
                "message": ["시스템 오류가 발생했습니다. 다시 시도해주세요."]
            }
        }




