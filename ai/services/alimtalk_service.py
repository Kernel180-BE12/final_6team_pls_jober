"""
알림톡 템플릿 검증 서비스
"""
import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Any, List

from .chromadb_service import ChromaDBService

try:
    from .openai_service import OpenAIService
    HAS_OPENAI_SERVICE = True
except ImportError:
    HAS_OPENAI_SERVICE = False
    print("Warning: OpenAI 서비스를 로드할 수 없습니다. Mock 모드로 실행됩니다.")
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.alimtalk_models import (
    ValidationRequest, ValidationResponse, ValidationResult, SystemStats
)
from validators.validator_pipeline import ValidationPipeline


class AlimtalkValidationService:
    """알림톡 검증 서비스"""
    
    def __init__(self):
        self.chromadb_service = ChromaDBService()
        
        if HAS_OPENAI_SERVICE:
            self.openai_service = OpenAIService()
        else:
            self.openai_service = None
            
        self.validation_pipeline = None
        self.is_initialized = False
        
    async def initialize(self):
        """
        알림톡 검증 서비스 초기화
        
        지연 초기화(Lazy Initialization) 패턴을 사용하여 서버 시작 시간을 단축하고,
        실제 검증 작업이 필요할 때만 무거운 초기화 작업을 수행합니다.
        
        초기화 과정:
        1. ChromaDB 서비스 초기화 - 벡터 데이터베이스 연결 및 컬렉션 준비
        2. 검증 파이프라인 구성 - 1차(제약) → 2차(의미적) 검증 순서 제어
        3. 의존성 주입 - 각 컴포넌트들을 연결하여 검증 워크플로우 구성
        
        중복 초기화 방지를 위해 is_initialized 플래그로 상태를 관리합니다.
        """
        if self.is_initialized:
            return
            
        try:
            # ChromaDB 초기화 - 정책 문서 및 승인된 템플릿 데이터 로드
            await self.chromadb_service.initialize()
            
            # 검증 파이프라인 초기화 - LLM 기반 제약 검증기와 의미적 검증기 연결
            from validators.constraint_validator import ConstraintValidator
            constraint_validator = ConstraintValidator()
            self.validation_pipeline = ValidationPipeline(
                chromadb_service=self.chromadb_service,
                constraint_validator=constraint_validator
            )
            
            self.is_initialized = True
            print(">>service<<")
            print(" 알림톡 검증 서비스 초기화 완료")
            
        except Exception as e:
            print(">>service<<")
            print(f" 알림톡 검증 서비스 초기화 실패: {e}")
            raise
    
    async def validate_template(self, request: ValidationRequest) -> ValidationResponse:
        """템플릿 검증 실행"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 검증 실행
            template_data = request.template.dict()
            result = self.validation_pipeline.validate(template_data)
            
            # 응답 생성
            if result['final_result'].is_valid:
                final_message = " 모든 검증을 통과했습니다. 발송 가능합니다."
                success = True
            else:
                error_count = len(result['final_result'].errors)
                warning_count = len(result['final_result'].warnings)
                final_message = f" 검증 실패: {error_count}개 오류, {warning_count}개 경고"
                success = False
            
            # 결과 필터링 (None이 아닌 것만)
            validation_results = []
            if result.get('constraint_result'):
                validation_results.append(result['constraint_result'])
            if result.get('semantic_result'):
                validation_results.append(result['semantic_result'])
            
            # validation_errors 생성
            validation_errors = []
            for result in validation_results:
                for error in result.errors:
                    validation_errors.append({
                        "rule_type": f"{result.stage}_validation",
                        "rule": "알림톡 승인 규칙",
                        "reason": error,
                        "suggestion": "AI에서 생성된 수정 제안을 참고해주세요",
                        "severity": "error",
                        "variable_name": None,
                        "stage": result.stage
                    })
            
            response = ValidationResponse(
                success=success,
                message=final_message,
                rejected_variables=[],
                validation_errors=validation_errors,
                alternatives={}
            )
            
            return response
            
        except Exception as e:
            return ValidationResponse(
                success=False,
                message=f"검증 중 오류가 발생했습니다: {str(e)}",
                rejected_variables=[],
                validation_errors=[],
                alternatives={}
            )

