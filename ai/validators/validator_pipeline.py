"""
검증 파이프라인 - 2단계 검증을 순차적으로 실행
"""
from typing import Dict, Any
# 👇 --- try-except 블록을 모두 제거하고, 이렇게 깔끔하게 정리합니다. ---
from .constraint_validator import ConstraintValidator
from .semantic_validator import SemanticValidator
from models.alimtalk_models import ValidationResult
from services.chromadb_service import ChromaDBService


class ValidationPipeline:
    """2단계 검증 파이프라인 - 의존성을 외부에서 주입받는 구조"""
    
    def __init__(self, chromadb_service: ChromaDBService, constraint_validator: ConstraintValidator):
        """
        2단계 검증 파이프라인 초기화
        모든 의존성을 외부에서 주입받습니다.
        이 클래스는 더 이상 아무것도 직접 생성하지 않습니다.
        즉, 오직 "검증 순서 제어"라는 자신의 책임에만 100% 집중합니다.
        """
        # ✅ 의존성 주입으로 수정함.
        self.chromadb_service = chromadb_service
        self.constraint_validator = constraint_validator  # 외부에서 주입받음
        self.semantic_validator = SemanticValidator(chromadb_service=chromadb_service)      # ChromaDB blacklist 컬렉션 사용
        
    def validate(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        2단계 검증을 순차적으로 실행
        
        Args:
            template_data: 검증할 템플릿 데이터 (TemplateGenerationResponse 구조)
                - template_content: 템플릿 텍스트 내용
                - template_title: 템플릿 제목
                - variables: 변수 정의 리스트 (List[Dict[str, str]])
                - category: 템플릿 카테고리
                - model: 사용된 모델명
                - detected_variables: 이미 추출된 변수 리스트
            
        Returns:
            각 단계별 검증 결과와 최종 결과
        """
        results = {
            'constraint_result': None, 
            'semantic_result': None,
            'final_result': None
        }
        
        # 1차 검증: 제약 검증
        print("🔍 1차 검증: 제약 검증 실행 중...")
        constraint_result = self.constraint_validator.validate(template_data)
        results['constraint_result'] = constraint_result
        
        if not constraint_result.is_valid:
            print("❌ 1차 제약 검증 실패")
            results['final_result'] = constraint_result
            return results
            
        print("✅ 1차 제약 검증 통과")
        
        # 2차 검증: 의미적 검증 (RAG)
        print("🔍 2차 검증: 의미적 검증 실행 중...")
        semantic_result = self.semantic_validator.validate(template_data)
        results['semantic_result'] = semantic_result
        
        if not semantic_result.is_valid:
            print("❌ 2차 의미적 검증 실패")
            results['final_result'] = semantic_result
            return results
            
        print("✅ 2차 의미적 검증 통과")
        
        # 모든 단계 통과 - 최종 결과 생성
        final_result = self._create_final_result(
            constraint_result, 
            semantic_result
        )
        results['final_result'] = final_result
        
        print("🎉 모든 검증 단계 통과!")
        return results

    def _create_final_result(self, 
                           constraint_result: ValidationResult, 
                           semantic_result: ValidationResult) -> ValidationResult:
        """
        각 단계 결과를 종합하여 최종 결과 생성
        
        Args:
            constraint_result: 제약 검증 결과
            semantic_result: 의미적 검증 결과
            
        Returns:
            최종 검증 결과
        """
        # 모든 오류와 경고 수집
        all_errors = []
        all_warnings = []
        
        for result in [constraint_result, semantic_result]:
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
        
        # 모든 단계가 통과했으므로 is_valid는 True
        is_valid = len(all_errors) == 0
        
        # 상세 정보 수집
        details = {
            'constraint_details': constraint_result.details,
            'semantic_details': semantic_result.details,
            'total_errors': len(all_errors),
            'total_warnings': len(all_warnings),
            'validation_summary': {
                'constraint_passed': constraint_result.is_valid,
                'semantic_passed': semantic_result.is_valid,
                'overall_passed': is_valid
            }
        }
        
        return ValidationResult(
            is_valid=is_valid,
            stage="final",
            errors=all_errors,
            warnings=all_warnings,
            details=details
        )
 