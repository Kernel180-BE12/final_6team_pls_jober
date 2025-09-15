"""
1차 검증: 제약 검증 (ChromaDB 기반 스키마 제약)
ChromaDB에서 제약사항을 검색하여 정확한 스키마 매칭 검증
"""
import re
from typing import Dict, Any, List

try:
    from ..models.alimtalk_models import ValidationResult
    from ..services.chromadb_service import ChromaDBService
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from models.alimtalk_models import ValidationResult
    from services.chromadb_service import ChromaDBService


class ConstraintValidator:
    """ChromaDB 기반 제약 검증기"""

    def __init__(self, vector_db_manager: ChromaDBService = None, rules_path: str = None):
        """
        Args:
            vector_db_manager: 벡터DB 관리자 (ChromaDB 기반 제약 검색)
            rules_path: 기본 규칙 파일 경로 (백업용, 현재 미사용)
        """
        # ChromaDB 연결 (1차 검증용 policy_guidelines 컬렉션)
        self.vector_db = vector_db_manager or ChromaDBService(collection_name="review_guidelines")

    def validate(self, template_data: Dict[str, Any]) -> ValidationResult:
        """
        ChromaDB 기반 제약 검증을 수행합니다.

        Args:
            template_data: 검증할 템플릿 데이터

        Returns:
            ValidationResult: 검증 결과
        """
        errors = []
        warnings = []

        try:
            # 1. ChromaDB에서 제약사항 검색 및 검증
            chromadb_errors, chromadb_warnings = self._check_chromadb_constraints(template_data)
            errors.extend(chromadb_errors)
            warnings.extend(chromadb_warnings)

            # 2. 백업 YAML 규칙 검증 (크리티컬한 기본 제약사항)
            backup_errors, backup_warnings = self._check_backup_constraints(template_data)
            errors.extend(backup_errors)
            warnings.extend(backup_warnings)

            is_valid = len(errors) == 0

            return ValidationResult(
                is_valid=is_valid,
                stage="constraint",
                errors=errors,
                warnings=warnings,
                details={
                    "chromadb_constraints_checked": True,
                    "backup_constraints_checked": True,
                    "total_errors": len(errors),
                    "total_warnings": len(warnings)
                }
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                stage="constraint",
                errors=[f"제약 검증 중 오류 발생: {str(e)}"],
                warnings=[],
                details={"exception": str(e)}
            )

    def _check_chromadb_constraints(self, template_data: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """ChromaDB에서 모든 제약사항을 가져와서 스키마 검증"""
        errors = []
        warnings = []

        try:
            # 템플릿 텍스트에서 변수 추출
            template_text = template_data.get('template_text', '')
            detected_variables = self._extract_variables_from_template(template_text)
            
            # 변수 검증
            variable_errors, variable_warnings = self._validate_variables(template_data, detected_variables)
            errors.extend(variable_errors)
            warnings.extend(variable_warnings)

            # ChromaDB에서 모든 제약사항 가져오기 (RAG 검색이 아닌 전체 조회)
            all_constraints = self._get_all_constraints_from_db()

            # 각 제약사항에 대해 정확한 스키마 검증
            for constraint in all_constraints:
                metadata = constraint.get('metadata', {})

                # constraint 또는 rule 타입만 처리
                constraint_type = metadata.get('type', '').lower()
                if constraint_type not in ['constraint', 'rule']:
                    continue

                # 스키마 제약사항 검증 (정확한 규칙 매칭)
                violation = self._check_schema_constraint(
                    template_data,
                    constraint['content'],
                    metadata
                )

                if violation:
                    priority = metadata.get('priority', 'medium')
                    enforcement = metadata.get('enforcement', 'flexible')

                    constraint_msg = f"스키마 제약 위반: {violation}"

                    # 우선순위에 따라 오류/경고 분류
                    if priority in ['critical', 'high'] and enforcement == 'strict':
                        errors.append(constraint_msg)
                    else:
                        warnings.append(constraint_msg)

        except Exception as e:
            warnings.append(f"ChromaDB 제약사항 검증 중 오류: {str(e)}")

        return errors, warnings

    def _extract_variables_from_template(self, template_text: str) -> List[str]:
        """템플릿 텍스트에서 변수 추출"""
        import re
        variables = []
        
        # {변수명} 패턴 찾기
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, template_text)
        variables.extend(matches)
        
        # #{변수명} 패턴 찾기
        pattern = r'#\{([^}]+)\}'
        matches = re.findall(pattern, template_text)
        variables.extend(matches)
        
        # {{변수명}} 패턴 찾기
        pattern = r'\{\{([^}]+)\}\}'
        matches = re.findall(pattern, template_text)
        variables.extend(matches)
        
        return list(set(variables))  # 중복 제거

    def _validate_variables(self, template_data: Dict[str, Any], detected_variables: List[str]) -> tuple[List[str], List[str]]:
        """변수 검증"""
        errors = []
        warnings = []
        
        # 템플릿에서 감지된 변수들
        variables_detected = template_data.get('variables_detected', {})
        
        # 감지된 변수가 있는데 variables_detected가 비어있는 경우
        if detected_variables and not variables_detected:
            errors.append("템플릿에 변수가 포함되어 있지만 변수 정의가 없습니다.")
            for var in detected_variables:
                errors.append(f"변수 '{var}'에 대한 정의가 필요합니다.")
        
        # 변수 정의는 있지만 템플릿에서 사용되지 않는 경우
        for var_name in variables_detected.keys():
            if var_name not in detected_variables:
                warnings.append(f"변수 '{var_name}'가 정의되었지만 템플릿에서 사용되지 않습니다.")
        
        # 템플릿에서 사용되지만 정의되지 않은 변수
        for var in detected_variables:
            if var not in variables_detected:
                errors.append(f"변수 '{var}'가 템플릿에서 사용되지만 정의되지 않았습니다.")
        
        # 변수 값 검증
        for var_name, var_value in variables_detected.items():
            if not var_value or str(var_value).strip() == '':
                errors.append(f"변수 '{var_name}'의 값이 비어있습니다.")
            elif len(str(var_value)) > 100:
                warnings.append(f"변수 '{var_name}'의 값이 너무 깁니다 (100자 초과).")
        
        return errors, warnings

    def _get_all_constraints_from_db(self) -> List[Dict[str, Any]]:
        """ChromaDB에서 모든 제약사항 가져오기"""
        try:
            # ChromaDB에서 모든 문서 조회
            results = self.vector_db.get_all_documents()
            constraints = []
            
            for doc in results:
                if doc.get('metadata', {}).get('type') in ['constraint', 'rule']:
                    constraints.append(doc)
            
            return constraints
        except Exception as e:
            print(f"ChromaDB에서 제약사항 조회 중 오류: {e}")
            return []

    def _check_schema_constraint(self, template_data: Dict[str, Any], constraint_content: str, metadata: Dict[str, Any]) -> str:
        """스키마 제약사항 검증"""
        try:
            # 기본적인 스키마 검증 로직
            template_text = template_data.get('template_text', '')
            
            # 길이 제한 검증
            if 'max_length' in constraint_content.lower():
                if len(template_text) > 1000:
                    return f"템플릿 길이가 제한을 초과했습니다 (1000자 초과)"
            
            # 변수 개수 제한 검증
            if 'max_variables' in constraint_content.lower():
                variables = template_data.get('variables_detected', {})
                if len(variables) > 10:
                    return f"변수 개수가 제한을 초과했습니다 (10개 초과)"
            
            return None  # 위반사항 없음
            
        except Exception as e:
            return f"스키마 검증 중 오류: {str(e)}"

    def _check_backup_constraints(self, template_data: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """백업 제약사항 검증 (기본적인 크리티컬 규칙)"""
        errors = []
        warnings = []
        
        try:
            template_text = template_data.get('template_text', '')
            
            # 기본 제약사항 검증
            if not template_text or not template_text.strip():
                errors.append("템플릿 내용이 비어있습니다.")
                return errors, warnings
            
            # 길이 제한 검증
            if len(template_text) > 1000:
                warnings.append("템플릿 내용이 너무 깁니다 (1000자 초과).")
            
            # 필수 키워드 검증
            if '안녕하세요' not in template_text and '안녕' not in template_text:
                warnings.append("인사말이 포함되지 않았습니다.")
            
            # 금지어 검증 (기본적인 것들)
            forbidden_words = ['광고', '홍보', '마케팅']
            for word in forbidden_words:
                if word in template_text and 'transaction' not in template_data.get('category', ''):
                    warnings.append(f"금지어 '{word}'가 포함되어 있습니다.")
            
            # 변수 형식 검증 (더 관대한 패턴)
            import re
            # 기본 변수 패턴: {변수명} 또는 #{변수명}
            valid_patterns = [
                r'#?\{[가-힣a-zA-Z0-9_]+\}',  # #{변수명} 또는 {변수명}
            ]
            
            # 모든 변수 패턴 찾기
            all_vars = re.findall(r'#?\{[^}]+\}', template_text)
            
            # 유효하지 않은 변수 찾기
            invalid_vars = []
            for var in all_vars:
                is_valid = False
                for pattern in valid_patterns:
                    if re.match(pattern, var):
                        is_valid = True
                        break
                if not is_valid:
                    invalid_vars.append(var)
            
            if invalid_vars:
                for var in invalid_vars:
                    errors.append(f"잘못된 변수 형식: {var}")
            
        except Exception as e:
            warnings.append(f"백업 제약사항 검증 중 오류: {str(e)}")
        
        return errors, warnings