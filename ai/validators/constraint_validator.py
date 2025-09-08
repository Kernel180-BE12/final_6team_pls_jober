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

    def _get_all_constraints_from_db(self) -> List[Dict[str, Any]]:
        """ChromaDB에서 모든 제약사항 조회"""
        try:
            # ChromaDBService의 메서드 활용
            if hasattr(self.vector_db, 'get_all_documents'):
                all_docs = self.vector_db.get_all_documents()
                constraints = []
                for doc in all_docs:
                    constraint_type = doc.get('metadata', {}).get('type', '').lower()
                    if constraint_type in ['constraint', 'rule']:
                        constraints.append(doc)
                return constraints
            else:
                # Mock 데이터나 기본 제약사항 반환
                return self._get_mock_constraints()

        except Exception as e:
            print(f"제약사항 조회 중 오류: {e}")
            return self._get_mock_constraints()

    def _get_mock_constraints(self) -> List[Dict[str, Any]]:
        """Mock 제약사항 데이터"""
        return [
            {
                'id': 'constraint_001',
                'content': '알림톡 본문은 1000자를 초과할 수 없습니다.',
                'metadata': {
                    'type': 'constraint',
                    'category': 'length',
                    'max_length': 1000,
                    'field': 'body',
                    'priority': 'critical',
                    'enforcement': 'strict'
                }
            },
            {
                'id': 'constraint_002',
                'content': '버튼은 최대 5개까지 허용됩니다.',
                'metadata': {
                    'type': 'constraint',
                    'category': 'button',
                    'max_buttons': 5,
                    'priority': 'high',
                    'enforcement': 'strict'
                }
            },
            {
                'id': 'constraint_003',
                'content': '금칙어는 사용할 수 없습니다.',
                'metadata': {
                    'type': 'constraint',
                    'category': 'forbidden_words',
                    'forbidden_words': ['도박', '카지노', '성인', '대출'],
                    'priority': 'high',
                    'enforcement': 'strict'
                }
            }
        ]

    def _check_schema_constraint(self, template_data: Dict[str, Any], constraint_content: str, metadata: Dict[str, Any]) -> str:
        """정확한 스키마 제약사항 검증"""
        category = metadata.get('category', 'general')

        # 메타데이터에 정확한 제약 조건이 있는 경우 우선 사용
        if 'max_length' in metadata:
            return self._check_exact_length(template_data, metadata)
        elif 'forbidden_words' in metadata:
            return self._check_exact_forbidden_words(template_data, metadata)
        elif 'max_buttons' in metadata:
            return self._check_exact_button_count(template_data, metadata)
        elif 'required_fields' in metadata:
            return self._check_required_fields(template_data, metadata)

        # 메타데이터가 없으면 카테고리별 기본 검증
        if category == 'length':
            return self._check_length_constraint(template_data, constraint_content, metadata)
        elif category == 'forbidden_words' or '금칙어' in constraint_content:
            return self._check_forbidden_constraint(template_data, constraint_content, metadata)
        elif category == 'button':
            return self._check_button_constraint(template_data, constraint_content, metadata)
        elif category == 'variable':
            return self._check_variable_constraint(template_data, constraint_content, metadata)
        elif category == 'url' or category == 'domain':
            return self._check_url_constraint(template_data, constraint_content, metadata)
        elif category == 'marketing':
            return self._check_marketing_constraint(template_data, constraint_content, metadata)
        elif category == 'privacy':
            return self._check_privacy_constraint(template_data, constraint_content, metadata)

        return ""  # 위반 없음

    def _check_exact_length(self, template_data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """정확한 길이 제약 검증"""
        max_length = metadata.get('max_length')
        field = metadata.get('field', 'body')  # 기본값: body

        if field == 'body':
            content = template_data.get('body', '')
            if len(content) > max_length:
                return f"본문이 {max_length}자를 초과했습니다 (현재: {len(content)}자)"
        elif field == 'title':
            content = template_data.get('title', '')
            if content and len(content) > max_length:
                return f"제목이 {max_length}자를 초과했습니다 (현재: {len(content)}자)"

        return ""

    def _check_exact_forbidden_words(self, template_data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """정확한 금칙어 제약 검증"""
        forbidden_words = metadata.get('forbidden_words', [])
        title = template_data.get('title', '')
        body = template_data.get('body', '')
        content = f"{title} {body}".lower()

        for word in forbidden_words:
            if word.lower() in content:
                return f"금칙어 '{word}'가 포함되어 있습니다"

        return ""

    def _check_exact_button_count(self, template_data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """정확한 버튼 개수 제약 검증"""
        max_buttons = metadata.get('max_buttons')
        buttons = template_data.get('buttons', [])

        if len(buttons) > max_buttons:
            return f"버튼은 최대 {max_buttons}개까지 허용됩니다 (현재: {len(buttons)}개)"

        return ""

    def _check_required_fields(self, template_data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """필수 필드 제약 검증"""
        required_fields = metadata.get('required_fields', [])

        for field in required_fields:
            if field not in template_data or not template_data[field]:
                return f"필수 필드 '{field}'가 누락되었습니다"

        return ""

    def _check_length_constraint(self, template_data: Dict[str, Any], constraint: str, metadata: Dict[str, Any]) -> str:
        """길이 제약사항 검증"""
        body = template_data.get('body', '')
        title = template_data.get('title', '')

        # 1000자 제한 확인
        if '1000자' in constraint and len(body) > 1000:
            return f"본문이 1000자를 초과했습니다 (현재: {len(body)}자)"

        # 제목 길이 확인
        if '제목' in constraint and '50자' in constraint and title and len(title) > 50:
            return f"제목이 50자를 초과했습니다 (현재: {len(title)}자)"

        return ""

    def _check_forbidden_constraint(self, template_data: Dict[str, Any], constraint: str, metadata: Dict[str, Any]) -> str:
        """금칙어 제약사항 검증"""
        title = template_data.get('title', '')
        body = template_data.get('body', '')
        content = f"{title} {body}".lower()

        # 메타데이터에서 금칙어 목록 추출
        forbidden_words = metadata.get('forbidden_words', [])

        # 제약사항 텍스트에서 금칙어 추출 (백업)
        if not forbidden_words:
            common_forbidden = ['도박', '카지노', '성인', '대출', '투자보장', '100% 보장']
            for word in common_forbidden:
                if word in constraint:
                    forbidden_words.append(word)

        # 금칙어 검사
        for word in forbidden_words:
            if word.lower() in content:
                return f"금칙어 '{word}'가 포함되어 있습니다"

        return ""

    def _check_button_constraint(self, template_data: Dict[str, Any], constraint: str, metadata: Dict[str, Any]) -> str:
        """버튼 제약사항 검증"""
        buttons = template_data.get('buttons', [])

        # 버튼 개수 제한
        if '5개' in constraint and len(buttons) > 5:
            return f"버튼은 최대 5개까지 허용됩니다 (현재: {len(buttons)}개)"

        # 버튼명 길이 확인
        for i, button in enumerate(buttons):
            name = button.get('name', '')
            if '14자' in constraint and len(name) > 14:
                return f"버튼 {i+1}의 이름이 14자를 초과했습니다 (현재: {len(name)}자)"

        return ""

    def _check_variable_constraint(self, template_data: Dict[str, Any], constraint: str, metadata: Dict[str, Any]) -> str:
        """변수 제약사항 검증"""
        body = template_data.get('body', '')
        variables = template_data.get('variables', {})

        # 변수 참조 패턴 찾기
        variable_pattern = r'#{([^}]+)}'
        referenced_vars = set(re.findall(variable_pattern, body))
        defined_vars = set(variables.keys())

        # 정의되지 않은 변수 참조
        undefined_vars = referenced_vars - defined_vars
        if undefined_vars and '정의' in constraint:
            return f"정의되지 않은 변수가 참조되었습니다: {', '.join(undefined_vars)}"

        return ""

    def _check_url_constraint(self, template_data: Dict[str, Any], constraint: str, metadata: Dict[str, Any]) -> str:
        """URL 제약사항 검증"""
        buttons = template_data.get('buttons', [])

        for i, button in enumerate(buttons):
            url_mobile = button.get('url_mobile', '')
            url_pc = button.get('url_pc', '')

            # URL 필수 설정 확인
            if 'URL' in constraint and '설정' in constraint:
                if not url_mobile and not url_pc:
                    return f"버튼 {i+1}에 모바일 URL 또는 PC URL 중 하나는 설정해야 합니다"

        return ""

    def _check_marketing_constraint(self, template_data: Dict[str, Any], constraint: str, metadata: Dict[str, Any]) -> str:
        """마케팅 제약사항 검증"""
        body = template_data.get('body', '')
        category = template_data.get('category', '')

        # 마케팅 알림톡 광고 표기 확인
        if category == 'marketing' and '광고' in constraint:
            if '(광고)' not in body and '광고' not in body:
                return "마케팅 알림톡에는 '(광고)' 표기가 필요합니다"

        return ""

    def _check_privacy_constraint(self, template_data: Dict[str, Any], constraint: str, metadata: Dict[str, Any]) -> str:
        """개인정보 제약사항 검증"""
        body = template_data.get('body', '')
        title = template_data.get('title', '')
        content = f"{title} {body}"

        # 개인정보 패턴 검사
        privacy_patterns = [
            (r'\d{6}-\d{7}', '주민번호'),
            (r'\d{4}-\d{4}-\d{4}-\d{4}', '카드번호'),
            (r'\d{3}-\d{2,3}-\d{6}', '계좌번호')
        ]

        for pattern, info_type in privacy_patterns:
            if re.search(pattern, content):
                return f"{info_type} 형태의 개인정보가 포함되어 있습니다"

        return ""

    def _check_backup_constraints(self, template_data: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """백업 제약사항 검증 (ChromaDB 실패 시 최소한의 안전장치)"""
        errors = []
        warnings = []

        try:
            # ChromaDB가 실패했을 때만 사용하는 최소한의 크리티컬 제약사항
            body = template_data.get('body', '')

            # 1. 절대적 길이 제한 (시스템 한계)
            if len(body) > 2000:  # 카카오톡 시스템 한계
                errors.append(f"본문이 시스템 한계(2000자)를 초과했습니다 (현재: {len(body)}자)")

            # 2. 절대적 버튼 개수 제한 (시스템 한계)
            buttons = template_data.get('buttons', [])
            if len(buttons) > 10:  # 카카오톡 시스템 한계
                errors.append(f"버튼이 시스템 한계(10개)를 초과했습니다 (현재: {len(buttons)}개)")

        except Exception as e:
            warnings.append(f"백업 제약사항 검증 중 오류: {str(e)}")

        return errors, warnings