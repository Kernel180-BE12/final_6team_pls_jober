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
            self.validation_pipeline = ValidationPipeline(
                vector_db_manager=self.chromadb_service
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
    
    # async def validate_single_step(self, template_data: Dict[str, Any], step: int) -> ValidationResult:
    #     """특정 단계만 검증"""
    #     if not self.is_initialized:
    #         await self.initialize()
    #
    #     return self.validation_pipeline.validate_single_step(template_data, step)
    #
    # async def search_guidelines(self, query: str, limit: int = 10) -> List[GuidelineSearchResult]:
    #     """가이드라인 검색"""
    #     if not self.is_initialized:
    #         await self.initialize()
    #
    #     try:
    #         results = self.chromadb_service.search_similar(query, n_results=limit)
    #
    #         return [
    #             GuidelineSearchResult(
    #                 id=result['id'],
    #                 content=result['content'],
    #                 metadata=result['metadata'],
    #                 similarity=result['similarity']
    #             )
    #             for result in results
    #         ]
    #
    #     except Exception as e:
    #         print(f"가이드라인 검색 중 오류: {e}")
    #         return []

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

    async def get_stats(self) -> SystemStats:
        """시스템 통계 정보"""
        if not self.is_initialized:
            await self.initialize()

        try:
            chromadb_stats = self.chromadb_service.get_collection_stats()

            return SystemStats(
                vector_db=chromadb_stats,
                validation_pipeline={
                    "stages": ["constraint", "semantic"],
                    "total_stages": 2
                },
                service_status="running" if self.is_initialized else "stopped"
            )

        except Exception as e:
            return SystemStats(
                vector_db={"error": str(e)},
                validation_pipeline={"error": str(e)},
                service_status="error"
            )

    async def get_template_examples(self) -> Dict[str, Any]:
        """템플릿 예시 반환 (ChromaDB 컬렉션에서 조회)"""
        try:
            if not self.is_initialized:
                await self.initialize()

            # 각 컬렉션에서 템플릿 조회
            blacklist_templates = self.chromadb_service.get_blacklist_templates()
            whitelist_templates = self.chromadb_service.get_whitelist_templates()
            approved_templates = self.chromadb_service.get_approved_templates()

            return {
                "blacklist": blacklist_templates,
                "whitelist": whitelist_templates,
                "approved": approved_templates,
                "summary": {
                    "blacklist_count": len(blacklist_templates),
                    "whitelist_count": len(whitelist_templates),
                    "approved_count": len(approved_templates)
                }
            }

        except Exception as e:
            print(f"템플릿 예시 로드 중 오류: {e}")
            return self._get_default_examples()

    async def _load_initial_guidelines(self):
        """초기 가이드라인 로드 (이제 ChromaDB에서 직접 로드)"""
        try:
            # ChromaDB에서 가이드라인 로드
            await self.chromadb_service.load_initial_guidelines()
            print("✅ 가이드라인 로드 완료")

        except Exception as e:
            print(f"❌ 가이드라인 로드 실패: {e}")

    def add_template_to_collection(self, collection_name: str, template_data: Dict[str, Any]):
        """특정 컬렉션에 템플릿 추가"""
        return self.chromadb_service.add_template_to_collection(collection_name, template_data)

    def search_templates_in_collection(self, collection_name: str, query: str, n_results: int = 5):
        """특정 컬렉션에서 템플릿 검색"""
        return self.chromadb_service.search_templates_in_collection(collection_name, query, n_results)

    def _get_default_examples(self) -> Dict[str, Any]:
        """기본 예시 템플릿"""
        return {
            "valid_transaction_template": {
                "template_pk": "TPL_TRANS_001",
                "channel": "alimtalk",
                "title": "주문 배송 완료 안내",
                "body": "안녕하세요 #{customer_name}님,\n\n주문하신 상품이 배송 완료되었습니다.\n\n감사합니다.",
                "variables": {
                    "customer_name": "홍길동"
                },
                "category": "transaction"
            },
            "valid_marketing_template": {
                "template_pk": "TPL_MARKET_001",
                "channel": "alimtalk",
                "title": "(광고) 신상품 특가 이벤트",
                "body": "(광고) 안녕하세요!\n\n신상품 출시 기념 특별 할인 이벤트를 진행합니다.\n\n* 수신거부: 080-000-0000",
                "category": "marketing"
            }
        }
