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
        """서비스 초기화"""
        if self.is_initialized:
            return
            
        try:
            # ChromaDB 초기화
            await self.chromadb_service.initialize()
            
            # 가이드라인 로드
            await self._load_initial_guidelines()
            
            # 검증 파이프라인 초기화
            from validators.constraint_validator import ConstraintValidator
            constraint_validator = ConstraintValidator()
            self.validation_pipeline = ValidationPipeline(
                chromadb_service=self.chromadb_service,
                constraint_validator=constraint_validator
            )
            
            self.is_initialized = True
            print(">>service<<")
            print("✅ 알림톡 검증 서비스 초기화 완료")
            
        except Exception as e:
            print(">>service<<")
            print(f"❌ 알림톡 검증 서비스 초기화 실패: {e}")
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
                final_message = "✅ 모든 검증을 통과했습니다. 발송 가능합니다."
                success = True
            else:
                error_count = len(result['final_result'].errors)
                warning_count = len(result['final_result'].warnings)
                final_message = f"❌ 검증 실패: {error_count}개 오류, {warning_count}개 경고"
                success = False
            
            # 결과 필터링 (None이 아닌 것만)
            validation_results = []
            if result.get('constraint_result'):
                validation_results.append(result['constraint_result'])
            if result.get('semantic_result'):
                validation_results.append(result['semantic_result'])
            
            response = ValidationResponse(
                success=success,
                template=request.template if success else None,
                validation_results=validation_results,
                final_message=final_message
            )
            
            return response
            
        except Exception as e:
            return ValidationResponse(
                success=False,
                template=None,
                validation_results=[],
                final_message=f"검증 중 오류가 발생했습니다: {str(e)}"
            )


    async def get_health_status(self) -> Dict[str, Any]:
        """헬스 상태 확인"""
        try:
            if not self.is_initialized:
                return {
                    "status": "not_initialized",
                    "message": "서비스가 초기화되지 않았습니다."
                }

            # ChromaDB 상태 확인
            chromadb_stats = self.chromadb_service.get_collection_stats()

            return {
                "status": "healthy",
                "vector_db": chromadb_stats,
                "pipeline_ready": self.validation_pipeline is not None,
                "services": {
                    "chromadb": "healthy" if chromadb_stats else "unhealthy",
                    "openai": "healthy" if self.openai_service else "not_configured"
                }
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }



    async def _load_initial_guidelines(self):
        """초기 가이드라인 로드 (이제 ChromaDB에서 직접 로드)"""
        try:
            # ChromaDB에서 가이드라인 로드
            await self.chromadb_service.load_initial_guidelines()
            print("✅ 가이드라인 로드 완료")

        except Exception as e:
            print(f"❌ 가이드라인 로드 실패: {e}")


