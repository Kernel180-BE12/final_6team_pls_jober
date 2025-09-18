"""
변수 사용 규칙 검증 프롬프트
"""

def get_variable_usage_validation_prompt(template_content: str, detected_variables: list, variable_list: dict) -> str:
    """변수 사용 규칙 검증 프롬프트 생성"""
    return f"""다음 알림톡 템플릿의 변수 사용이 적절한지 검증해주세요.

## 변수 사용 규칙
- 변수는 최대 40개까지만 사용 가능
- 변수 예시값 반드시 기재 필요
- 템플릿이 변수로만 이루어질 수 없음
- 버튼명, 미리보기 메시지에는 변수를 포함할 수 없음
- 충분한 고정 텍스트가 있어야 함

## 검증 대상 템플릿
내용: {template_content}
탐지된 변수 목록: {detected_variables}
변수 정의 및 예시값: {variable_list}

이 템플릿의 변수 사용이 위 규칙들을 모두 준수하고 있는지 검증해주세요.
특히 변수 개수, 예시값 존재 여부, 템플릿 구조의 적절성을 중점적으로 확인해주세요.

## 응답 형식 (JSON)
{{
    "is_valid": true/false,
    "violations": [
        {{
            "rule": "위반된 규칙",
            "reason": "위반 사유",
            "severity": "error/warning",
            "suggestion": "개선 방안",
            "variable_name": "관련 변수명 (해당하는 경우)"
        }}
    ],
    "overall_assessment": "전체적인 평가"
}}"""
