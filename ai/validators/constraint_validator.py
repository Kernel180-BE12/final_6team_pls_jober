"""
1차 검증: 제약 검증 (알림톡 승인 규칙 기반)
LLM을 활용한 동적 규칙 검증 시스템

이 모듈은 템플릿 검증 파이프라인의 첫 번째 단계로, 다음과 같은 검증을 수행합니다:
1. 정보성 메시지 요건 검증
2. 정형화된 템플릿 요건 검증
3. 변수 사용 규칙 검증
4. 기타 템플릿 작성 규칙 검증
"""
import re
from typing import Dict, Any, List
import json
import logging

# 상대 임포트 시도 (패키지 내부에서 실행될 때) / main.py
try:
    from ..models.alimtalk_models import ValidationResult
    from ..services.openai_service import OpenAIService
    from .prompts.informational_message_prompt import get_informational_message_validation_prompt
    from .prompts.standardized_template_prompt import get_standardized_template_validation_prompt
    from .prompts.variable_usage_prompt import get_variable_usage_validation_prompt
    from .prompts.template_writing_prompt import get_template_writing_validation_prompt
except ImportError:
    # 절대 임포트 (단독 실행될 때) / validators/constraint_validator.py
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from models.alimtalk_models import ValidationResult
    from services.openai_service import OpenAIService
    from validators.prompts.informational_message_prompt import get_informational_message_validation_prompt
    from validators.prompts.standardized_template_prompt import get_standardized_template_validation_prompt
    from validators.prompts.variable_usage_prompt import get_variable_usage_validation_prompt
    from validators.prompts.template_writing_prompt import get_template_writing_validation_prompt

logger = logging.getLogger(__name__)

class ConstraintValidator:
    """
    템플릿 제약사항 검증을 담당하는 클래스
    
    알림톡 승인 규칙을 기반으로 LLM을 활용한 동적 검증을 수행합니다.
    """
    
    def __init__(self):
        """
        ConstraintValidator 초기화
        """
        try:
            self.openai_service = OpenAIService()
            logger.info("✅ ConstraintValidator 초기화 완료 (LLM 기반)")
        except Exception as e:
            logger.exception("❌ ConstraintValidator 초기화 실패")
            raise

    def validate(self, template_data: Dict[str, Any]) -> ValidationResult:
        """
        1차 검증: 알림톡 승인 규칙 기반 검증
        
        검증 규칙:
        1. 정보성 메시지 요건
        2. 정형화된 템플릿 요건  
        3. 변수 사용 규칙
        4. 기타 템플릿 작성 규칙
        
        Args:
            template_data: 검증할 템플릿 데이터
                - templateContent: 템플릿 텍스트 내용
                - templateTitle: 템플릿 제목
                - variableList: 변수 정의 딕셔너리
                - category: 템플릿 카테고리
        
        Returns:
            ValidationResult: 검증 결과 객체
        """
        logger.info("🔍 1차 검증 시작: 알림톡 승인 규칙 검증")
        logger.debug(f"입력 데이터 keys: {list(template_data.keys())}")

        errors = []
        warnings = []
        rejected_variables = []
        validation_details = []

        try:
            # 1. 정보성 메시지 요건 검증
            logger.info("📌 [1단계] 정보성 메시지 요건 검증")
            info_errors, info_warnings, info_details = self._check_informational_message_requirements(template_data)
            errors.extend(info_errors)
            warnings.extend(info_warnings)
            validation_details.extend(info_details)
            
            # 1단계 결과 로그
            if info_errors:
                print(f"❌ [1단계] 정보성 메시지 오류 {len(info_errors)}개:")
                for i, error in enumerate(info_errors, 1):
                    print(f"   {i}. {error}")
            if info_warnings:
                print(f"⚠️ [1단계] 정보성 메시지 경고 {len(info_warnings)}개:")
                for i, warning in enumerate(info_warnings, 1):
                    print(f"   {i}. {warning}")
            if not info_errors and not info_warnings:
                print("✅ [1단계] 정보성 메시지 검증 통과")

            # 2. 정형화된 템플릿 요건 검증
            logger.info("📌 [2단계] 정형화된 템플릿 요건 검증")
            standard_errors, standard_warnings, standard_details = self._check_standardized_template_requirements(template_data)
            errors.extend(standard_errors)
            warnings.extend(standard_warnings)
            validation_details.extend(standard_details)
            
            # 2단계 결과 로그
            if standard_errors:
                print(f"❌ [2단계] 정형화된 템플릿 오류 {len(standard_errors)}개:")
                for i, error in enumerate(standard_errors, 1):
                    print(f"   {i}. {error}")
            if standard_warnings:
                print(f"⚠️ [2단계] 정형화된 템플릿 경고 {len(standard_warnings)}개:")
                for i, warning in enumerate(standard_warnings, 1):
                    print(f"   {i}. {warning}")
            if not standard_errors and not standard_warnings:
                print("✅ [2단계] 정형화된 템플릿 검증 통과")

            # 3. 변수 사용 규칙 검증
            logger.info("📌 [3단계] 변수 사용 규칙 검증")
            var_errors, var_warnings, var_details, var_rejected = self._check_variable_usage_rules(template_data)
            errors.extend(var_errors)
            warnings.extend(var_warnings)
            validation_details.extend(var_details)
            rejected_variables.extend(var_rejected)
            
            # 3단계 결과 로그
            if var_errors:
                print(f"❌ [3단계] 변수 사용 오류 {len(var_errors)}개:")
                for i, error in enumerate(var_errors, 1):
                    print(f"   {i}. {error}")
            if var_warnings:
                print(f"⚠️ [3단계] 변수 사용 경고 {len(var_warnings)}개:")
                for i, warning in enumerate(var_warnings, 1):
                    print(f"   {i}. {warning}")
            if var_rejected:
                print(f"🚫 [3단계] 반려된 변수 {len(var_rejected)}개: {var_rejected}")
            if not var_errors and not var_warnings:
                print("✅ [3단계] 변수 사용 규칙 검증 통과")

            # 4. 기타 템플릿 작성 규칙 검증
            logger.info("📌 [4단계] 기타 템플릿 작성 규칙 검증")
            other_errors, other_warnings, other_details = self._check_other_template_rules(template_data)
            errors.extend(other_errors)
            warnings.extend(other_warnings)
            validation_details.extend(other_details)
            
            # 4단계 결과 로그
            if other_errors:
                print(f"❌ [4단계] 기타 규칙 오류 {len(other_errors)}개:")
                for i, error in enumerate(other_errors, 1):
                    print(f"   {i}. {error}")
            if other_warnings:
                print(f"⚠️ [4단계] 기타 규칙 경고 {len(other_warnings)}개:")
                for i, warning in enumerate(other_warnings, 1):
                    print(f"   {i}. {warning}")
            if not other_errors and not other_warnings:
                print("✅ [4단계] 기타 템플릿 작성 규칙 검증 통과")

            # 최종 결과
            is_valid = len(errors) == 0
            print(f"\n📋 1차 검증 최종 결과:")
            print(f"   ✅ 통과 여부: {'통과' if is_valid else '실패'}")
            print(f"   ❌ 총 오류: {len(errors)}개")
            print(f"   ⚠️ 총 경고: {len(warnings)}개")
            print(f"   🚫 반려된 변수: {len(rejected_variables)}개")
            
            logger.info(f"✅ 1차 검증 완료 → valid={is_valid}, 총 오류={len(errors)}, 총 경고={len(warnings)}")

            return ValidationResult(
                is_valid=is_valid,
                stage="constraint",
                errors=errors,
                warnings=warnings,
                details={
                    "validation_type": "alimtalk_approval_rules",
                    "total_errors": len(errors),
                    "total_warnings": len(warnings),
                    "rejected_variables": rejected_variables,
                    "validation_details": validation_details,
                    "rules_checked": [
                        "informational_message_requirements",
                        "standardized_template_requirements", 
                        "variable_usage_rules",
                        "other_template_rules"
                    ]
                }
            )

        except Exception as e:
            logger.exception("❌ 1차 검증 중 예외 발생")
            return ValidationResult(
                is_valid=False,
                stage="constraint",
                errors=[f"1차 검증 중 오류 발생: {str(e)}"],
                warnings=[],
                details={"exception": str(e)}
            )

    def _check_informational_message_requirements(self, template_data: Dict[str, Any]) -> tuple[List[str], List[str], List[Dict[str, Any]]]:
        """정보성 메시지 요건 검증 (LLM 기반)"""
        errors, warnings, details = [], [], []
        
        # 검증 대상 데이터 추출 (카테고리, 제목, 내용)
        templateContent = template_data.get('templateContent', '')
        templateTitle = template_data.get('templateTitle', '')
        category = template_data.get('category', '')
        
        try:
            prompt = get_informational_message_validation_prompt(category, templateTitle, templateContent)
            
            import asyncio
            response = asyncio.run(self.openai_service.chat_completion([
                {"role": "system", "content": "알림톡 템플릿 검증 전문가입니다. JSON 형식으로만 응답하세요."},
                {"role": "user", "content": prompt}
            ]))
            
            try:
                result = json.loads(response)
                if not result.get('is_valid', True):
                    for violation in result.get('violations', []):
                        message = f"정보성 메시지 요건 위반: {violation.get('reason', '알 수 없는 사유')}"
                        if violation.get('severity') == 'error':
                            errors.append(message)
                        else:
                            warnings.append(message)
                        details.append({
                            "rule_type": "informational_message",
                            "rule": violation.get('rule', '알 수 없는 규칙'),
                            "reason": violation.get('reason', '알 수 없는 사유'),
                            "suggestion": violation.get('suggestion', '수정이 필요합니다'),
                            "severity": violation.get('severity', 'error')
                        })
            except json.JSONDecodeError:
                warnings.append("정보성 메시지 검증 중 오류가 발생했습니다.")
                
        except Exception as e:
            warnings.append("정보성 메시지 검증 중 오류가 발생했습니다.")
        
        return errors, warnings, details

    def _check_standardized_template_requirements(self, template_data: Dict[str, Any]) -> tuple[List[str], List[str], List[Dict[str, Any]]]:
        """정형화된 템플릿 요건 검증 (LLM 기반)"""
        errors, warnings, details = [], [], []
        
        # 검증 대상 데이터 추출 (제목, 내용)
        templateContent = template_data.get('templateContent', '')
        templateTitle = template_data.get('templateTitle', '')
        
        try:
            prompt = get_standardized_template_validation_prompt(templateTitle, templateContent)
            
            import asyncio
            response = asyncio.run(self.openai_service.chat_completion([
                {"role": "system", "content": "알림톡 템플릿 검증 전문가입니다. JSON 형식으로만 응답하세요."},
                {"role": "user", "content": prompt}
            ]))
            
            try:
                result = json.loads(response)
                if not result.get('is_valid', True):
                    for violation in result.get('violations', []):
                        message = f"정형화된 템플릿 요건 위반: {violation.get('reason', '알 수 없는 사유')}"
                        if violation.get('severity') == 'error':
                            errors.append(message)
                        else:
                            warnings.append(message)
                        details.append({
                            "rule_type": "standardized_template",
                            "rule": violation.get('rule', '알 수 없는 규칙'),
                            "reason": violation.get('reason', '알 수 없는 사유'),
                            "suggestion": violation.get('suggestion', '수정이 필요합니다'),
                            "severity": violation.get('severity', 'error')
                        })
            except json.JSONDecodeError:
                warnings.append("정형화된 템플릿 검증 중 오류가 발생했습니다.")
                
        except Exception as e:
            warnings.append("정형화된 템플릿 검증 중 오류가 발생했습니다.")
        
        return errors, warnings, details

    def _check_variable_usage_rules(self, template_data: Dict[str, Any]) -> tuple[List[str], List[str], List[Dict[str, Any]], List[str]]:
        """변수 사용 규칙 검증 (LLM 기반)"""
        errors, warnings, details = [], [], []
        rejected_variables = []
        
        templateContent = template_data.get('templateContent', '')
        variableList = template_data.get('variableList', {})
        detected_variables = self._extract_variables_from_template(templateContent)
        
        try:
            prompt = get_variable_usage_validation_prompt(templateContent, detected_variables, variableList)
            
            import asyncio
            response = asyncio.run(self.openai_service.chat_completion([
                {"role": "system", "content": "알림톡 템플릿 변수 사용 검증 전문가입니다. JSON 형식으로만 응답하세요."},
                {"role": "user", "content": prompt}
            ]))
            
            try:
                result = json.loads(response)
                if not result.get('is_valid', True):
                    for violation in result.get('violations', []):
                        message = f"변수 사용 규칙 위반: {violation.get('reason', '알 수 없는 사유')}"
                        if violation.get('severity') == 'error':
                            errors.append(message)
                        else:
                            warnings.append(message)
                        
                        # 변수 관련 오류인 경우 반려 변수 목록에 추가
                        if violation.get('variable_name'):
                            rejected_variables.append(violation.get('variable_name'))
                        
                        details.append({
                            "rule_type": "variable_usage",
                            "rule": violation.get('rule', '알 수 없는 규칙'),
                            "reason": violation.get('reason', '알 수 없는 사유'),
                            "suggestion": violation.get('suggestion', '수정이 필요합니다'),
                            "severity": violation.get('severity', 'error'),
                            "variable_name": violation.get('variable_name')
                        })
            except json.JSONDecodeError:
                warnings.append("변수 사용 규칙 검증 중 오류가 발생했습니다.")
                
        except Exception as e:
            warnings.append("변수 사용 규칙 검증 중 오류가 발생했습니다.")
        
        return errors, warnings, details, rejected_variables

    def _check_other_template_rules(self, template_data: Dict[str, Any]) -> tuple[List[str], List[str], List[Dict[str, Any]]]:
        """기타 템플릿 작성 규칙 검증 (LLM 기반)"""
        errors, warnings, details = [], [], []
        
        # 검증 대상 데이터 추출 (제목, 내용)
        templateContent = template_data.get('templateContent', '')
        templateTitle = template_data.get('templateTitle', '')
        
        try:
            prompt = get_template_writing_validation_prompt(templateTitle, templateContent)
            
            import asyncio
            response = asyncio.run(self.openai_service.chat_completion([
                {"role": "system", "content": "알림톡 템플릿 작성 규칙 검증 전문가입니다. JSON 형식으로만 응답하세요."},
                {"role": "user", "content": prompt}
            ]))
            
            try:
                result = json.loads(response)
                if not result.get('is_valid', True):
                    for violation in result.get('violations', []):
                        message = f"템플릿 작성 규칙 위반: {violation.get('reason', '알 수 없는 사유')}"
                        if violation.get('severity') == 'error':
                            errors.append(message)
                        else:
                            warnings.append(message)
                        details.append({
                            "rule_type": "template_writing",
                            "rule": violation.get('rule', '알 수 없는 규칙'),
                            "reason": violation.get('reason', '알 수 없는 사유'),
                            "suggestion": violation.get('suggestion', '수정이 필요합니다'),
                            "severity": violation.get('severity', 'error')
                        })
            except json.JSONDecodeError:
                warnings.append("기타 템플릿 작성 규칙 검증 중 오류가 발생했습니다.")
        except Exception as e:
            warnings.append("기타 템플릿 작성 규칙 검증 중 오류가 발생했습니다.")
        
        return errors, warnings, details

    def _extract_variables_from_template(self, templateContent: str) -> List[str]:
        """
        템플릿 텍스트에서 변수 추출
        
        지원하는 변수 패턴:
        1. {변수명} - 기본 패턴
        2. #{변수명} - 해시 접두사 패턴
        3. {{변수명}} - 이중 중괄호 패턴
        
        Args:
            templateContent: 템플릿 텍스트 내용
        
        Returns:
            List[str]: 중복 제거된 변수명 리스트
        """
        import re
        logger.debug("변수 추출 시작")
        variables = []

        # 1. {변수명} 패턴 - 기본 변수 형식
        matches = re.findall(r'\{([^}]+)\}', templateContent)
        variables.extend(matches)

        # 2. #{변수명} 패턴 - 해시 접두사가 있는 변수
        matches = re.findall(r'#\{([^}]+)\}', templateContent)
        variables.extend(matches)

        # 3. {{변수명}} 패턴 - 이중 중괄호 변수 (일부 템플릿 엔진 지원)
        matches = re.findall(r'\{\{([^}]+)\}\}', templateContent)
        variables.extend(matches)

        # 중복 제거 후 반환
        unique_vars = list(set(variables))
        logger.debug(f"추출된 변수 최종 목록: {unique_vars}")
        return unique_vars
