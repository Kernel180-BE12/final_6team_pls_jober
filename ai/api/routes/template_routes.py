# api/routes/template_routes.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from core.constants import APPROVED_SUB_CATEGORIES
from services.dependencies import get_openai_service, get_chromadb_service
from services.openai_service import OpenAIService
from services.chromadb_service import ChromaDBService
from templateEngine.pipeline import run_template_generation_pipeline

router = APIRouter(prefix="/template", tags=["Template Generation"])

# --- Pydantic 모델 ---
class GenerationRequest(BaseModel):
    userMessage: str

class VariableInfo(BaseModel):
    name: str
    original_value: str  # 원본에서 추출된 실제 값
    type: str
    description: str

class GenerationResponse(BaseModel):
    template_content: str
    variables: List[VariableInfo]
    variable_mapping: Dict[str, str]  # 변수명: 원본값 매핑
    category: str
    model: str
    template_title: str
    generation_method: str
    similarity_score: float

@router.post("/generate", response_model=GenerationResponse)
async def generate_template_endpoint(
        request: GenerationRequest,
        openai_service: OpenAIService = Depends(get_openai_service),
        chromadb_service: ChromaDBService = Depends(get_chromadb_service)
):
    try:
        result = await run_template_generation_pipeline(
            userMessage=request.userMessage,
            category_sub_list=APPROVED_SUB_CATEGORIES,
            openai_service=openai_service,
            chromadb_service=chromadb_service
        )

        # 추출된 필드를 더 실용적으로 구성
        extracted_fields = result.get("extracted_fields", {})
        variables = []
        variable_mapping = {}

        for var_name, original_value in extracted_fields.items():
            var_info = {
                "name": var_name,
                "original_value": original_value,
                "type": _determine_variable_type(var_name),
                "description": _generate_variable_description(var_name)
            }
            variables.append(var_info)
            variable_mapping[var_name] = original_value

        response_data = {
            "template_content": result.get("template_text", ""),
            "variables": variables,
            "variable_mapping": variable_mapping,
            "category": result.get("category_sub", "기타"),
            "model": "gpt-4o-mini",
            "template_title": result.get("template_title", ""),
            "generation_method": result.get("generation_method", ""),
            "similarity_score": result.get("similarity_score", 0.0)
        }

        return GenerationResponse(**response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API 엔드포인트 오류: {str(e)}")

def _determine_variable_type(var_name: str) -> str:
    """변수명 기반 타입 추론"""
    if 'phone' in var_name or 'contact' in var_name:
        return "contact"
    elif 'amount' in var_name or 'price' in var_name:
        return "currency"
    elif 'date' in var_name or 'time' in var_name:
        return "datetime"
    elif 'name' in var_name or 'title' in var_name:
        return "personal"
    elif 'company' in var_name or 'brand' in var_name:
        return "business"
    else:
        return "string"

def _generate_variable_description(var_name: str) -> str:
    """변수명 기반 설명 생성"""
    descriptions = {
        'customer_name': '고객 이름',
        'customer_title': '고객 호칭 (고객님, 회원님 등)',
        'company_name': '회사명/브랜드명',
        'service_name': '서비스/제품명',
        'phone_number': '연락처 번호',
        'contact_info': '연락처 관련 전체 문구',
        'main_message': '핵심 안내 메시지',
        'seasonal_context': '계절/시기 관련 내용',
        'detail_info': '상세 설명 부분'
    }
    return descriptions.get(var_name, f'{var_name.replace("_", " ").title()} 정보')