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

import logging

logger = logging.getLogger(__name__)

class ConstraintValidator:
    def __init__(self, vector_db_manager: ChromaDBService = None, rules_path: str = None):
        """
        Args:
            vector_db_manager: 벡터DB 관리자 (ChromaDB 기반 제약 검색)
            rules_path: 기본 규칙 파일 경로 (백업용, 현재 미사용)
        """
        try:
            self.vector_db = vector_db_manager or ChromaDBService(collection_name="review_guidelines")
            logger.info("✅ ConstraintValidator 초기화 완료 (collection=review_guidelines)")
        except Exception as e:
            logger.exception("❌ ConstraintValidator 초기화 실패")
            raise

    def validate(self, template_data: Dict[str, Any]) -> ValidationResult:
        """ChromaDB 기반 제약 검증을 수행합니다."""
        logger.info("🔍 제약 검증 시작")
        logger.debug(f"입력 데이터 keys: {list(template_data.keys())}")  # 전체 데이터 말고 key만 출력

        errors = []
        warnings = []

        try:
            # 1. ChromaDB 제약사항 검증
            logger.info("📌 [1단계] ChromaDB 제약사항 검증 실행")
            chromadb_errors, chromadb_warnings = self._check_chromadb_constraints(template_data)
            errors.extend(chromadb_errors)
            warnings.extend(chromadb_warnings)

            # 2. 백업 규칙 검증
            logger.info("📌 [2단계] 백업 규칙 검증 실행")
            backup_errors, backup_warnings = self._check_backup_constraints(template_data)
            errors.extend(backup_errors)
            warnings.extend(backup_warnings)

            # 최종 결과
            is_valid = len(errors) == 0
            logger.info(f"✅ 제약 검증 완료 → valid={is_valid}, 총 오류={len(errors)}, 총 경고={len(warnings)}")

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
            logger.exception("❌ 제약 검증 중 예외 발생")  # stack trace까지 로깅
            return ValidationResult(
                is_valid=False,
                stage="constraint",
                errors=[f"제약 검증 중 오류 발생: {str(e)}"],
                warnings=[],
                details={"exception": str(e)}
            )

    def _check_chromadb_constraints(self, template_data: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """ChromaDB에서 모든 제약사항을 가져와서 스키마 검증"""
        logger.info("🔍 ChromaDB 제약사항 검증 시작")
        errors = []
        warnings = []

        try:
            # 템플릿 텍스트 변수 추출
            templateContent = template_data.get('templateContent', '')
            logger.debug(f"템플릿 텍스트 길이: {len(templateContent)}")
            detected_variables = self._extract_variables_from_template(templateContent)
            logger.debug(f"추출된 변수: {detected_variables}")

            # 변수 검증
            variable_errors, variable_warnings = self._validate_variables(template_data, detected_variables)
            errors.extend(variable_errors)
            warnings.extend(variable_warnings)
            if variable_errors or variable_warnings:
                logger.info(f"📌 변수 검증 결과 → 오류 {len(variable_errors)}개, 경고 {len(variable_warnings)}개")

            # 제약사항 전체 조회
            all_constraints = self._get_all_constraints_from_db()
            logger.info(f"📥 제약사항 {len(all_constraints)}개 로드됨")

            # 각 제약사항 검증
            for idx, constraint in enumerate(all_constraints, start=1):
                content = constraint.get('content', '')
                metadata = constraint.get('metadata', {})
                logger.debug(f"➡️ 제약[{idx}] 검사 시작: section={metadata.get('section', 'N/A')}")

                violation = self._check_schema_constraint(template_data, content, metadata)

                if violation:
                    priority = metadata.get('priority', 'medium')
                    enforcement = metadata.get('enforcement', 'flexible')
                    msg = f"[제약:{idx}] {violation}"

                    if priority in ['critical', 'high'] and enforcement == 'strict':
                        logger.error(f"❌ 치명적 위반: {msg}")
                        errors.append(msg)
                    else:
                        logger.warning(f"⚠️ 경고성 위반: {msg}")
                        warnings.append(msg)
                else:
                    logger.debug(f"✅ 제약[{idx}] 통과")

            logger.info(f"✅ ChromaDB 제약사항 검증 완료 → 오류 {len(errors)}개, 경고 {len(warnings)}개")

        except Exception as e:
            msg = f"ChromaDB 제약사항 검증 중 오류: {str(e)}"
            logger.error(f"❌ {msg}")
            warnings.append(msg)

        return errors, warnings

    def _extract_variables_from_template(self, templateContent: str) -> List[str]:
        """템플릿 텍스트에서 변수 추출"""
        import re
        logger.debug("변수 추출 시작")
        variables = []

        # {변수명} 패턴
        matches = re.findall(r'\{([^}]+)\}', templateContent)
        variables.extend(matches)

        # #{변수명} 패턴
        matches = re.findall(r'#\{([^}]+)\}', templateContent)
        variables.extend(matches)

        # {{변수명}} 패턴
        matches = re.findall(r'\{\{([^}]+)\}\}', templateContent)
        variables.extend(matches)

        unique_vars = list(set(variables))
        logger.debug(f"추출된 변수 최종 목록: {unique_vars}")
        return unique_vars

    def _validate_variables(self, template_data: Dict[str, Any], detected_variables: List[str]) -> tuple[List[str], List[str]]:
        """변수 검증"""
        logger.info("🔍 변수 검증 시작")
        errors = []
        warnings = []
        
        variableList = template_data.get('variableList', {})
        logger.debug(f"템플릿 감지 변수: {detected_variables}")
        logger.debug(f"입력된 변수 정의: {variableList}")

        # 템플릿에 변수가 있는데 정의가 없는 경우
        if detected_variables and not variableList:
            msg = "템플릿에 변수가 포함되어 있지만 변수 정의가 없습니다."
            errors.append(msg)
            for var in detected_variables:
                errors.append(f"변수 '{var}'에 대한 정의가 필요합니다.")
            logger.error(f"❌ {msg} (총 {len(detected_variables)}개)")

        # 정의는 있는데 사용되지 않은 변수
        unused_vars = [var for var in variableList.keys() if var not in detected_variables]
        for var in unused_vars:
            warnings.append(f"변수 '{var}'가 정의되었지만 템플릿에서 사용되지 않습니다.")
        if unused_vars:
            logger.warning(f"⚠️ 사용되지 않은 변수 {len(unused_vars)}개 발견: {unused_vars}")

        # 사용됐지만 정의되지 않은 변수
        undefined_vars = [var for var in detected_variables if var not in variableList]
        for var in undefined_vars:
            errors.append(f"변수 '{var}'가 템플릿에서 사용되지만 정의되지 않았습니다.")
        if undefined_vars:
            logger.error(f"❌ 정의되지 않은 변수 {len(undefined_vars)}개 발견: {undefined_vars}")

        # 변수 값 검증
        for var_name, var_value in variableList.items():
            if not var_value or str(var_value).strip() == '':
                errors.append(f"변수 '{var_name}'의 값이 비어있습니다.")
            elif len(str(var_value)) > 100:
                warnings.append(f"변수 '{var_name}'의 값이 너무 깁니다 (100자 초과).")
        logger.debug("변수 값 검증 완료")

        logger.info(f"✅ 변수 검증 완료 (errors={len(errors)}, warnings={len(warnings)})")
        return errors, warnings

    def _get_all_constraints_from_db(self) -> List[Dict[str, Any]]:
        """ChromaDB에서 모든 제약사항 가져오기"""
        logger.debug("📥 ChromaDB 제약사항 전체 조회 시작")
        try:
            results = self.vector_db.get_all_documents()
            constraints = [
                doc for doc in results
                if doc.get("metadata", {}).get("guideline_type") == "review_guideline"
            ]
            logger.info(f"✅ 제약사항 {len(constraints)}개 로드됨")
            return constraints
        except Exception as e:
            logger.error("❌ ChromaDB에서 제약사항 조회 중 오류 발생", exc_info=True)
            logger.warning("⚠️ 제약사항을 불러오지 못해 빈 리스트 반환 → 모든 검증이 통과될 수 있음")
            return []

    def _check_schema_constraint(self, template_data: Dict[str, Any], constraint_content: str, metadata: Dict[str, Any]) -> str:
        """스키마 제약사항 검증"""
        logger.debug(f"🔍 스키마 제약사항 검증 실행 (content={constraint_content}, metadata={metadata})")
        try:
            templateContent = template_data.get('templateContent', '')
            userMessage = template_data.get('userMessage', '')

            # 길이 제한 검증
            if 'max_length' in constraint_content.lower():
                if len(userMessage.strip()) > 1000:
                    return "템플릿 길이가 제한을 초과했습니다 (1000자 초과)"

            # 변수 개수 제한 검증
            if 'max_variables' in constraint_content.lower():
                variables = template_data.get('variableList', {})
                if len(variables) > 10:
                    return "변수 개수가 제한을 초과했습니다 (10개 초과)"

            logger.debug("✅ 스키마 제약 위반 없음")
            return None
        except Exception as e:
            msg = f"스키마 검증 중 오류: {str(e)}"
            logger.error(msg)
            return msg

    def _check_backup_constraints(self, template_data: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """백업 제약사항 검증 (기본적인 크리티컬 규칙)"""
        errors = []
        warnings = []
        
        logger.info("📌 백업 제약사항 검증 시작")
        
        try:
            templateContent = template_data.get('templateContent', '')
            logger.debug(f"템플릿 내용 길이: {len(templateContent)}")
            
            # 기본 제약사항 검증
            if not templateContent or not templateContent.strip():
                errors.append("템플릿 내용이 비어있습니다.")
                return errors, warnings
            
            # 길이 제한 검증
            if len(templateContent) > 1000:
                warnings.append("템플릿 내용이 너무 깁니다 (1000자 초과).")
            
            # 필수 키워드 검증
            if '안녕하세요' not in templateContent and '안녕' not in templateContent:
                warnings.append("인사말이 포함되지 않았습니다.")
            
            # 금지어 검증
            forbidden_words = ['광고', '홍보', '마케팅']
            for word in forbidden_words:
                if word in templateContent and 'transaction' not in template_data.get('category', ''):
                    warnings.append(f"금지어 '{word}'가 포함되어 있습니다.")
            
            # 변수 형식 검증
            import re
            valid_patterns = [
                r'#?\{[가-힣a-zA-Z0-9_]+\}',  # #{변수명} 또는 {변수명}
            ]
            
            all_vars = re.findall(r'#?\{[^}]+\}', templateContent)
            logger.debug(f"탐지된 변수 패턴: {all_vars}")
            
            for var in all_vars:
                if not any(re.match(pattern, var) for pattern in valid_patterns):
                    errors.append(f"잘못된 변수 형식: {var}")
        
        except Exception as e:
            warnings.append(f"백업 제약사항 검증 중 오류: {str(e)}")
        
        logger.info(f"✅ 백업 제약사항 검증 완료 (errors={len(errors)}, warnings={len(warnings)})")
        return errors, warnings
