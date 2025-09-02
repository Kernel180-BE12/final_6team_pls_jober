from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sys
import os

# services 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from template_service import TemplateValidationService, initialize_example_templates

router = APIRouter(prefix="/template", tags=["template"])

# Request/Response 모델 정의
class TemplateRequest(BaseModel):
    user_message: str
    similarity_threshold: Optional[float] = 0.7
    template_type: Optional[str] = None  # 템플릿 유형 (주문/배송, 예약/신청 등)
    
class ValidationRequest(BaseModel):
    template_text: str
    expected_category: Optional[str] = None  # 예상 카테고리
    
class BatchValidationRequest(BaseModel):
    templates: List[ValidationRequest]
    
class TemplateAnalysisRequest(BaseModel):
    user_message: str
    generate_template: Optional[bool] = False  # 템플릿 생성 여부

# 글로벌 서비스 인스턴스
template_service = TemplateValidationService()

@router.post("/search-similar")
async def search_similar_templates(request: TemplateRequest):
    """
    유사한 템플릿 검색
    """
    try:
        result = await template_service.search_similar_templates(
            user_message=request.user_message,
            similarity_threshold=request.similarity_threshold
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"템플릿 검색 실패: {str(e)}")

@router.post("/validate")
async def validate_template(request: ValidationRequest):
    """
    템플릿 내용 검증 (화이트리스트/블랙리스트)
    """
    try:
        result = await template_service.validate_template_content(request.template_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"템플릿 검증 실패: {str(e)}")

@router.post("/process")
async def process_template_request(request: TemplateRequest):
    """
    전체 템플릿 처리 프로세스
    1. 유사 템플릿 검색
    2. 검증 수행
    """
    try:
        result = await template_service.process_template_request(request.user_message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"템플릿 처리 실패: {str(e)}")

@router.get("/guidelines/status")
async def get_guideline_status():
    """
    현재 로드된 카카오 가이드라인 상태 확인
    """
    try:
        result = template_service.get_guideline_status()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"가이드라인 상태 확인 실패: {str(e)}")

@router.post("/initialize")
async def initialize_templates():
    """
    예시 템플릿 초기화 (개발/테스트용)
    """
    try:
        result = await initialize_example_templates()
        return {
            "message": "예시 템플릿이 초기화되었습니다.",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"템플릿 초기화 실패: {str(e)}")

@router.get("/test/event-invitation")
async def test_event_invitation():
    """
    행사 요청 알림톡 테스트 (예시)
    """
    test_message = "회사 워크샵을 다음 주 금요일 오후 2시에 강남 회의실에서 진행합니다. 참석 부탁드립니다."
    
    try:
        result = await template_service.process_template_request(test_message)
        return {
            "test_message": test_message,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"테스트 실패: {str(e)}")

@router.get("/test/samples")
async def test_various_samples():
    """
    다양한 샘플 메시지 테스트
    """
    test_samples = {
        "valid_order": "주문하신 상품이 배송 완료되었습니다. 구매확정 부탁드립니다.",
        "valid_reservation": "예약하신 #{상품명}이 확정되었습니다. 예약일시: #{일시}",
        "invalid_marketing": "특가 세일! 지금 구매하시면 50% 할인 혜택을 받으실 수 있습니다!",
        "invalid_birthday": "생일을 축하드립니다! 특별한 쿠폰을 준비했어요.",
        "invalid_cart": "장바구니에 담은 상품을 잊지 않으셨나요? 지금 구매하세요!"
    }
    
    results = {}
    for test_name, message in test_samples.items():
        try:
            validation_result = await template_service.validate_template_content(message)
            results[test_name] = {
                "message": message,
                "validation": validation_result
            }
        except Exception as e:
            results[test_name] = {
                "message": message,
                "error": str(e)
            }
    
    return results

@router.post("/batch-validate")
async def batch_validate_templates(request: BatchValidationRequest):
    """
    여러 템플릿 일괄 검증
    """
    try:
        results = []
        for i, template_req in enumerate(request.templates):
            validation_result = await template_service.validate_template_content(
                template_req.template_text
            )
            results.append({
                "index": i,
                "template_text": template_req.template_text,
                "expected_category": template_req.expected_category,
                "validation": validation_result
            })
        
        return {
            "total_templates": len(request.templates),
            "results": results,
            "summary": {
                "valid_count": sum(1 for r in results if r["validation"]["is_valid"]),
                "invalid_count": sum(1 for r in results if not r["validation"]["is_valid"])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"일괄 검증 실패: {str(e)}")

@router.post("/analyze")
async def analyze_user_message(request: TemplateAnalysisRequest):
    """
    사용자 메시지 분석 및 템플릿 추천
    """
    try:
        # 1. 유사 템플릿 검색
        similar_templates = await template_service.search_similar_templates(
            request.user_message, 
            similarity_threshold=0.6
        )
        
        # 2. 메시지 검증
        validation = await template_service.validate_template_content(request.user_message)
        
        # 3. 카테고리 분석
        category_analysis = template_service._analyze_message_category(request.user_message)
        
        result = {
            "user_message": request.user_message,
            "similar_templates": similar_templates,
            "validation": validation,
            "category_analysis": category_analysis,
            "recommendations": []
        }
        
        # 4. 추천사항 생성
        if validation["is_valid"]:
            result["recommendations"].append("적합한 알림톡 템플릿으로 판단됩니다.")
            if validation["whitelist_categories"]:
                result["recommendations"].append(
                    f"적용 가능한 카테고리: {', '.join(validation['whitelist_categories'])}"
                )
        else:
            result["recommendations"].extend(validation["recommendations"])
            result["recommendations"].append("블랙리스트 규정을 확인하여 수정이 필요합니다.")
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메시지 분석 실패: {str(e)}")

@router.get("/categories/whitelist")
async def get_whitelist_categories():
    """
    화이트리스트 카테고리 목록 조회
    """
    try:
        return {
            "categories": list(template_service.whitelist_patterns.keys()),
            "patterns": template_service.whitelist_patterns,
            "total_keywords": len(template_service.whitelist_keywords)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"화이트리스트 조회 실패: {str(e)}")

@router.get("/categories/blacklist")
async def get_blacklist_categories():
    """
    블랙리스트 카테고리 목록 조회
    """
    try:
        return {
            "categories": list(template_service.blacklist_patterns.keys()),
            "patterns": template_service.blacklist_patterns,
            "total_keywords": len(template_service.blacklist_keywords)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"블랙리스트 조회 실패: {str(e)}")