"""
알림톡 템플릿 데이터 모델 정의
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator
from enum import Enum



class ProblemArea(BaseModel):
    """문제 영역 모델"""
    area_id: str  # 고유 식별자
    area_type: str  # "specific_text", "paragraph", "entire_template"
    location: str  # "1-3줄", "제목", "전체", "A/S 안내 문단"
    problem_text: str  # 문제가 되는 실제 텍스트
    start_position: Optional[int] = None  # 텍스트 시작 위치
    end_position: Optional[int] = None  # 텍스트 끝 위치
    error_type: str  # "informational_message", "standardized_template" 등
    severity: str  # "error", "warning"
    reason: str  # 문제 사유
    suggestion: str  # 개선 방안
    alternatives: List[str] = []  # 대안 목록

class ValidationResult(BaseModel):
    """검증 결과 모델"""
    is_valid: bool
    stage: str  # "constraint", "semantic", "final"
    errors: List[str] = []
    warnings: List[str] = []
    problem_areas: List[ProblemArea] = []  # 문제 영역 목록
    details: Optional[Dict[str, Any]] = None

class Button(BaseModel):
    """버튼 모델"""
    name: str = Field(..., min_length=1, max_length=14, description="버튼명")
    type: str = Field(..., description="버튼 타입")
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
    # template_pk: Optional[int] = Field(None, description="템플릿 Primary Key")
    template_content: Optional[str] = Field(None, description="생성된 카카오톡 알림톡 템플릿 전체 내용")
    template_title: Optional[str] = Field(None, max_length=200, description="제목")
    variables: Optional[List[Dict[str, str]]] = Field(None, description="변수 리스트")
    buttons: Optional[List[Button]] = Field(None, max_items=5, description="버튼 목록")
    category: Optional[str] = Field(None, description="분류")

    @field_validator('template_content')
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
    
    @classmethod
    def from_backend_request(cls, backend_data: Dict[str, Any]) -> "ValidationRequest":
        """백엔드 요청 데이터로부터 ValidationRequest 생성"""
        
        # TemplateGenerationResponse 구조인지 확인
        if "template_content" in backend_data:
            # TemplateGenerationResponse 구조
            alimtalk_template = AlimtalkTemplate(
                template_content=backend_data.get("template_content", ""),
                template_title=backend_data.get("template_title", "알림톡 템플릿"),
                variables=backend_data.get("variables", []),
                category=backend_data.get("category"),
                buttons=[]
            )
            
            return cls(
                template=alimtalk_template,
                user_input=""  # TemplateGenerationResponse에는 user_input이 없음
            )
        elif "template" in backend_data:
            # 중첩된 template 구조 처리
            template_data = backend_data["template"]
            variables = []
            if template_data.get("variables"):
                for v in template_data["variables"]:
                    if isinstance(v, dict) and v.get("name"):
                        variables.append({
                            "name": v.get("name"),
                            "type": v.get("type", "string"),
                            "description": v.get("description", "")
                        })
            
            alimtalk_template = AlimtalkTemplate(
                template_content=template_data.get("template_content", ""),
                template_title=template_data.get("template_title", "알림톡 템플릿"),
                variables=variables,
                category=template_data.get("category"),
                buttons=[]
            )
            
            return cls(
                template=alimtalk_template,
                user_input=backend_data.get("user_input", "")
            )
        else:
            # 기존 백엔드 요청 구조 - variables_detected를 variables로 변환
            variables = []
            if backend_data.get("variableList"):
                for v in backend_data["variableList"]:
                    if v.get("variableKey"):
                        variable_key = v.get("variableKey")
                        # variableKey가 딕셔너리인 경우 name 필드 추출
                        if isinstance(variable_key, dict):
                            name = variable_key.get("name", "")
                            var_type = variable_key.get("type", "string")
                            description = variable_key.get("description", "")
                        else:
                            # 문자열인 경우
                            name = str(variable_key)
                            var_type = "string"
                            description = v.get("variableValue", "")
                        
                        variables.append({
                            "name": name,
                            "type": var_type,
                            "description": description
                        })
            
            alimtalk_template = AlimtalkTemplate(
                template_content=backend_data.get("templateContent", ""),
                template_title=backend_data.get("templateTitle", "알림톡 템플릿"),
                variables=variables,
                category=backend_data.get("category"),
                buttons=[]
            )
            
            return cls(
                template=alimtalk_template,
                user_input=backend_data.get("userMessage", "")
            )

class ValidationResponse(BaseModel):
    """검증 응답 모델 - 문제 영역 기반"""
    success: bool
    message: str
    problem_areas: List[ProblemArea] = []  # 문제 영역 목록
    validation_stage: str = "1차 검증"  # 검증 단계
    total_errors: int = 0
    total_warnings: int = 0
    
    class Config:
        # JSON 직렬화 시 필드명을 그대로 유지
        alias_generator = None
        validate_by_name = True
    
    def dict(self, **kwargs):
        """JSON 직렬화를 위한 dict 메서드 오버라이드"""
        return {
            "success": self.success,
            "message": self.message,
            "problem_areas": [area.dict() for area in self.problem_areas],
            "validation_stage": self.validation_stage,
            "total_errors": self.total_errors,
            "total_warnings": self.total_warnings
        }


# AI 서비스 관련 모델들
class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    message: str
    model: Optional[str] = "gpt-4o-mini"

class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    response: str
    model: str

class TemplateModificationRequest(BaseModel):
    """템플릿 수정 요청 모델"""
    current_template: str
    current_template_title: str
    userMessage: str
    chat_history: List[Dict[str, Any]] = []
    variableList: List[Dict[str, str]] = []

class TemplateModificationResponse(BaseModel):
    """템플릿 수정 응답 모델"""
    modified_template: str
    template_title: str
    variables: List[str]
    explanation: str
    model: str

