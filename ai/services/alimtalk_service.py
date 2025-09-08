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
try:
    from ..models.alimtalk_models import (
        ValidationRequest, ValidationResponse, ValidationResult, 
        AlimtalkTemplate, GuidelineSearchResult, SystemStats
    )
    from ..validators.validator_pipeline import ValidationPipeline
except ImportError:
    # 절대 import로 시도
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from models.alimtalk_models import (
        ValidationRequest, ValidationResponse, ValidationResult, 
        AlimtalkTemplate, GuidelineSearchResult, SystemStats
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
            print("✅ 알림톡 검증 서비스 초기화 완료")
            
        except Exception as e:
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
    
    async def validate_single_step(self, template_data: Dict[str, Any], step: int) -> ValidationResult:
        """특정 단계만 검증"""
        if not self.is_initialized:
            await self.initialize()
        
        return self.validation_pipeline.validate_single_step(template_data, step)
    
    async def search_guidelines(self, query: str, limit: int = 10) -> List[GuidelineSearchResult]:
        """가이드라인 검색"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            results = self.chromadb_service.search_similar(query, n_results=limit)
            
            return [
                GuidelineSearchResult(
                    id=result['id'],
                    content=result['content'],
                    metadata=result['metadata'],
                    similarity=result['similarity']
                )
                for result in results
            ]
            
        except Exception as e:
            print(f"가이드라인 검색 중 오류: {e}")
            return []
    
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
        """템플릿 예시 반환"""
        examples_file = Path(__file__).parent.parent / "data" / "example_templates.json"
        
        try:
            if examples_file.exists():
                with open(examples_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._get_default_examples()
                
        except Exception as e:
            print(f"예시 로드 중 오류: {e}")
            return self._get_default_examples()
    
    async def _load_initial_guidelines(self):
        """초기 가이드라인 로드"""
        guidelines_file = Path(__file__).parent.parent / "data" / "alimtalk_guidelines.json"
        
        if not guidelines_file.exists():
            # 기본 가이드라인 생성
            await self._create_default_guidelines(guidelines_file)
        
        try:
            with open(guidelines_file, 'r', encoding='utf-8') as f:
                guidelines_data = json.load(f)
            
            # ChromaDB에 추가
            self.chromadb_service.add_guidelines(guidelines_data)
            print(f"✅ 가이드라인 {len(guidelines_data)}개 로드 완료")
            
        except Exception as e:
            print(f"❌ 가이드라인 로드 실패: {e}")
    
    async def _create_default_guidelines(self, file_path: Path):
        """기본 가이드라인 생성"""
        default_guidelines = [
            {
                "id": "guide_001",
                "content": "알림톡 본문은 1000자를 초과할 수 없습니다.",
                "category": "length",
                "type": "rule",
                "metadata": {"priority": "high", "source": "kakaotalk_policy"}
            },
            {
                "id": "guide_002", 
                "content": "거래성 알림톡에는 광고성 표현을 포함할 수 없습니다.",
                "category": "content",
                "type": "policy",
                "metadata": {"priority": "high", "source": "kakaotalk_policy"}
            },
            {
                "id": "guide_003",
                "content": "마케팅 알림톡에는 '(광고)' 표기가 필수입니다.",
                "category": "marketing", 
                "type": "rule",
                "metadata": {"priority": "critical", "source": "kakaotalk_policy"}
            },
            {
                "id": "guide_004",
                "content": "개인정보(주민번호, 카드번호 등)는 템플릿에 직접 포함할 수 없습니다.",
                "category": "privacy",
                "type": "policy", 
                "metadata": {"priority": "critical", "source": "privacy_law"}
            },
            {
                "id": "guide_005",
                "content": "금융 관련 과장 표현(100% 보장, 무조건 등)은 사용할 수 없습니다.",
                "category": "financial",
                "type": "policy",
                "metadata": {"priority": "high", "source": "financial_law"}
            }
        ]
        
        # 디렉토리 생성
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 파일 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(default_guidelines, f, ensure_ascii=False, indent=2)
    
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
