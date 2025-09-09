"""
알림톡 템플릿 데이터 모델 정의
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ButtonType(str, Enum):
    """버튼 타입 열거형"""
    WEBLINK = "WL"  # 웹링크 (가장 일반적)
    APPLINK = "AL"  # 앱링크
    DELIVERY = "DS"  # 배송조회


class ChannelType(str, Enum):
    """채널 타입 열거형"""
    ALIMTALK = "alimtalk"
    FRIENDTALK = "friendtalk"


class CategoryType(str, Enum):
    """알림톡 분류 열거형"""
    TRANSACTION = "transaction"  # 거래성
    MARKETING = "marketing"      # 마케팅
    MIXED = "mixed"             # 혼합
    REVIEW = "review"           # 검토 필요


class ValidationResult(BaseModel):
    """검증 결과 모델"""
    is_valid: bool
    stage: str  # "constraint", "semantic", "final"
    errors: List[str] = []
    warnings: List[str] = []
    details: Optional[Dict[str, Any]] = None


class Button(BaseModel):
    """버튼 모델"""
    name: str = Field(..., min_length=1, max_length=14, description="버튼명")
    type: ButtonType = Field(..., description="버튼 타입")
    url_mobile: Optional[str] = Field(None, description="모바일 URL")
    url_pc: Optional[str] = Field(None, description="PC URL")
    scheme_android: Optional[str] = Field(None, description="안드로이드 스킴")
    scheme_ios: Optional[str] = Field(None, description="iOS 스킴")
    
    @field_validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("버튼명은 빈 값일 수 없습니다")
        return v.strip()


class AlimtalkTemplate(BaseModel):
    """알림톡 템플릿 모델"""
    template_pk: Optional[str] = Field(None, description="템플릿 Primary Key")
    channel: ChannelType = Field(..., description="채널 타입")
    title: Optional[str] = Field(None, max_length=50, description="제목")
    body: str = Field(..., min_length=1, max_length=1000, description="본문")
    buttons: Optional[List[Button]] = Field(None, max_items=5, description="버튼 목록")
    variables: Optional[Dict[str, str]] = Field(None, description="변수 목록")
    category: Optional[CategoryType] = Field(None, description="분류")
    
    @field_validator('body')
    def validate_body(cls, v):
        if not v or not v.strip():
            raise ValueError("본문은 빈 값일 수 없습니다")
        return v
    
    @field_validator('buttons')
    def validate_buttons(cls, v):
        if v and len(v) > 5:
            raise ValueError("버튼은 최대 5개까지 가능합니다")
        return v


class ValidationRequest(BaseModel):
    """검증 요청 모델"""
    template: AlimtalkTemplate
    user_input: str = Field(..., description="사용자 입력 내용")
    

class ValidationResponse(BaseModel):
    """검증 응답 모델"""
    success: bool
    template: Optional[AlimtalkTemplate] = None
    validation_results: List[ValidationResult] = []
    final_message: str


class GuidelineSearchResult(BaseModel):
    """가이드라인 검색 결과 모델"""
    id: str
    content: str
    metadata: Dict[str, Any]
    similarity: float


class SystemStats(BaseModel):
    """시스템 통계 모델"""
    vector_db: Dict[str, Any]
    validation_pipeline: Dict[str, Any]
    service_status: str



