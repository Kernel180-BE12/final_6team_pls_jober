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
        self.vector_db = vector_db_manager or ChromaDBService(collection_name="policy_guidelines")

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