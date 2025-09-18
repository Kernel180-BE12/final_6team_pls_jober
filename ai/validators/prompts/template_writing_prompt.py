"""
기타 템플릿 작성 규칙 검증 프롬프트
"""

def get_template_writing_validation_prompt(template_title: str, template_content: str) -> str:
    """기타 템플릿 작성 규칙 검증 프롬프트 생성"""
    return f"""다음 알림톡 템플릿이 기타 템플릿 작성 규칙을 만족하는지 검증해주세요.

## 기타 템플릿 작성 규칙
- 미리보기 메시지는 템플릿 내용과 직접 관련 있어야 함
- 템플릿 내용과 무관한 문구, 불필요한 광고 안내 문구 포함 불가
- 간단한 인사말(예: "안녕하세요") 정도는 허용

## 검증 대상 템플릿
제목: {template_title}
내용: {template_content}

이 템플릿이 위 규칙들을 준수하고 있는지 검증해주세요.
특히 템플릿 내용의 일관성과 불필요한 광고성 문구가 포함되어 있지 않은지 확인해주세요.

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
