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
            rejected_vars = set()
            validation_errors = []
            
            # 각 검증 결과에서 오류 정보 수집
            for result in validation_result.validation_results:
                for error in result.errors:
                    # 변수명 추출 (있는 경우)
                    variable_name = extract_variable_name_from_error(error)
                    if variable_name:
                        rejected_vars.add(variable_name)
                    
                    # 검증 오류 상세 정보 추가 (변수가 없어도 템플릿 전체 오류로 처리)
                    validation_errors.append({
                        "rule_type": f"{result.stage}_validation",
                        "rule": "알림톡 승인 규칙",
                        "reason": error,
                        "suggestion": generate_suggestion_for_error(error),
                        "severity": "error",
                        "variable_name": variable_name,
                        "stage": convert_stage_to_korean(result.stage)
                    })
            
            response["rejected_variables"] = list(rejected_vars)
            response["validation_errors"] = validation_errors
            
            # LLM 기반 대안 추천 생성
            if rejected_vars:
                response["alternatives"] = generate_alternatives(list(rejected_vars), request)
        
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


def convert_stage_to_korean(stage: str) -> str:
    """검증 단계를 한국어로 변환"""
    stage_map = {
        "constraint": "1차 검증",
        "semantic": "2차 검증", 
        "final": "최종 검증"
    }
    return stage_map.get(stage, "알 수 없음")

def generate_suggestion_for_error(error_message: str) -> str:
    """오류 메시지에 따른 수정 제안 생성"""
    if "변수" in error_message and "사용되지 않음" in error_message:
        return "템플릿에 #{변수명} 형식으로 변수를 추가해주세요"
    elif "제목" in error_message and "내용" in error_message and "비어" in error_message:
        return "템플릿에 명확한 제목과 내용을 작성해주세요"
    elif "광고성" in error_message:
        return "광고성 문구를 제거하고 정보 전달 목적의 내용으로 수정해주세요"
    elif "정형화" in error_message:
        return "일정한 구조를 가진 템플릿으로 작성해주세요"
    else:
        return "알림톡 승인 가이드라인에 맞게 내용을 수정해주세요"

def extract_variable_name_from_error(error_message: str) -> str:
    """오류 메시지에서 변수명 추출"""
    # "변수 '변수명'" 패턴 찾기
    if "변수 '" in error_message and "'" in error_message:
        start = error_message.find("변수 '") + 3
        end = error_message.find("'", start)
        if start != -1 and end != -1 and end > start:
            return error_message[start:end]
    
    # "{변수명}" 패턴 찾기
    if "{" in error_message and "}" in error_message:
        start = error_message.find("{")
        end = error_message.find("}", start)
        if start != -1 and end != -1 and end > start:
            return error_message[start + 1:end]
    
    return None


def generate_alternatives(rejected_variables: List[str], request: ValidationRequest) -> Dict[str, List[str]]:
    """검증 실패 시 LLM 기반 대안 추천 생성"""
    alternatives = {}
    
    # 템플릿에서 감지된 변수들
    template_variables = request.template.variables_detected or {}
    
    for variable in rejected_variables:
        suggestions = []
        
        # 변수별 맞춤형 대안 제안
        if variable in ["예약일시", "reservation_datetime", "예약시간"]:
            suggestions = [
                "예약 시간: 2024년 12월 25일 오후 2시",
                "상담 일정: 12월 25일(화) 14:00",
                "예약 일시: 2024.12.25 14:00"
            ]
        elif variable in ["위치", "location", "장소"]:
            suggestions = [
                "상담 장소: 본사 회의실",
                "위치: 서울시 강남구 테헤란로 123",
                "장소: 온라인 화상회의"
            ]
        elif variable in ["문의처", "contact", "연락처"]:
            suggestions = [
                "문의: 02-1234-5678",
                "연락처: 1588-1234",
                "고객센터: 080-123-4567"
            ]
        elif variable in ["고객명", "customer_name", "수신자"]:
            suggestions = [
                "고객님",
                "회원님",
                "고객"
            ]
        elif variable in ["발신자", "sender", "회사명"]:
            suggestions = [
                "저희 회사",
                "저희 팀",
                "운영팀"
            ]
        else:
            # 일반적인 대안
            suggestions = [
                "더 명확한 표현으로 수정해주세요",
                "구체적인 정보를 포함해주세요",
                "이해하기 쉬운 문구로 변경해주세요"
            ]
        
        alternatives[variable] = suggestions
    
    # 전체적인 메시지 대안도 추가
    alternatives["message"] = [
        "템플릿 내용을 더 명확하게 수정해주세요",
        "변수 값들을 구체적으로 입력해주세요",
        "알림톡 가이드라인에 맞게 수정해주세요"
    ]
    
    return alternatives
