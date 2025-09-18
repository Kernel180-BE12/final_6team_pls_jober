"""
정형화된 템플릿 요건 검증 프롬프트
"""

def get_standardized_template_validation_prompt(template_title: str, template_content: str) -> str:
    """정형화된 템플릿 요건 검증 프롬프트 생성"""
    return f"""다음 알림톡 템플릿이 정형화된 템플릿 요건을 만족하는지 검증해주세요.

## 정형화된 템플릿 요건
- 동일한 조건일 때 항상 같은 구조로 발송되는 메시지여야 함
- 특정 사용자, 특정 상황에 따라 가변적으로 달라지는 공지사항은 불가

## 검증 대상 템플릿
제목: {template_title}
내용: {template_content}

이 템플릿이 정형화된 구조를 가지고 있는지, 특정 상황에 따라 가변적으로 변하는 내용이 포함되어 있지는 않은지 검증해주세요.

## 응답 형식 (JSON)
{{
    "is_valid": true/false,
    "violations": [
        {{
            "rule": "위반된 규칙",
            "reason": "위반 사유",
            "severity": "error/warning",
            "suggestion": "개선 방안"
        }}
    ],
    "overall_assessment": "전체적인 평가"
}}"""
