"""
1단계: 스키마 검증 (형식/빈값)
JSON Schema를 사용한 구조적 검증
"""
import json
import jsonschema
from typing import Dict, Any, List
from pathlib import Path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import ValidationResult


class SchemaValidator:
    """JSON 스키마 기반 검증기"""
    
    def __init__(self, schema_path: str = None):
        """
        Args:
            schema_path: 스키마 파일 경로
        """
        if schema_path is None:
            schema_path = Path(__file__).parent.parent / "schemas" / "alimtalk_schema.json"
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)
            
        self.validator = jsonschema.Draft7Validator(self.schema)
    
    def validate(self, template_data: Dict[str, Any]) -> ValidationResult:
        """
        템플릿 데이터의 스키마 검증을 수행합니다.
        
        Args:
            template_data: 검증할 템플릿 데이터
            
        Returns:
            ValidationResult: 검증 결과
        """
        errors = []
        warnings = []
        
        try:
            # 기본 스키마 검증
            validation_errors = list(self.validator.iter_errors(template_data))
            
            for error in validation_errors:
                error_path = " -> ".join(str(p) for p in error.absolute_path)
                if error_path:
                    error_msg = f"[{error_path}] {error.message}"
                else:
                    error_msg = error.message
                errors.append(error_msg)
            
            # 추가 커스텀 검증
            custom_errors, custom_warnings = self._custom_validations(template_data)
            errors.extend(custom_errors)
            warnings.extend(custom_warnings)
            
            is_valid = len(errors) == 0
            
            return ValidationResult(
                is_valid=is_valid,
                stage="schema",
                errors=errors,
                warnings=warnings,
                details={
                    "schema_version": "draft-07",
                    "total_errors": len(errors),
                    "total_warnings": len(warnings)
                }
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                stage="schema",
                errors=[f"스키마 검증 중 오류 발생: {str(e)}"],
                warnings=[],
                details={"exception": str(e)}
            )
    
    def _custom_validations(self, template_data: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """
        커스텀 검증 로직
        
        Returns:
            tuple: (errors, warnings)
        """
        errors = []
        warnings = []
        
        # 1. 빈 문자열 검증 (공백만 있는 경우도 포함)
        if 'title' in template_data and template_data['title']:
            if not template_data['title'].strip():
                errors.append("제목은 공백만으로 구성될 수 없습니다")
        
        if 'body' in template_data:
            if not template_data['body'].strip():
                errors.append("본문은 공백만으로 구성될 수 없습니다")
        
        # 2. 버튼 관련 검증
        if 'buttons' in template_data and template_data['buttons']:
            for i, button in enumerate(template_data['buttons']):
                # 버튼명 공백 검증
                if 'name' in button and not button['name'].strip():
                    errors.append(f"버튼 {i+1}의 이름은 공백만으로 구성될 수 없습니다")
                
                # 버튼 타입별 필수 필드 검증
                button_type = button.get('type')
                if button_type == 'WL':  # 웹링크
                    if not button.get('url_mobile') and not button.get('url_pc'):
                        errors.append(f"웹링크 버튼 {i+1}은 모바일 URL 또는 PC URL이 필요합니다")
                elif button_type == 'AL':  # 앱링크
                    if not button.get('scheme_android') and not button.get('scheme_ios'):
                        errors.append(f"앱링크 버튼 {i+1}은 안드로이드 또는 iOS 스킴이 필요합니다")
        
        # 3. 변수 관련 검증
        if 'variables' in template_data and template_data['variables']:
            for var_name, var_value in template_data['variables'].items():
                if not var_value.strip():
                    errors.append(f"변수 '{var_name}'의 값은 공백만으로 구성될 수 없습니다")
        
        # 4. 길이 경고
        if 'body' in template_data and len(template_data['body']) > 800:
            warnings.append("본문이 800자를 초과했습니다. 가독성을 위해 줄이는 것을 권장합니다")
        
        if 'title' in template_data and template_data['title'] and len(template_data['title']) > 40:
            warnings.append("제목이 40자를 초과했습니다. 가독성을 위해 줄이는 것을 권장합니다")
        
        return errors, warnings
