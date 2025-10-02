"""
문제 영역 추출 프롬프트
AI를 사용해서 템플릿에서 문제가 되는 영역을 자동으로 추출하는 프롬프트
"""

def get_problem_extraction_prompt(template_content: str, error_text: str) -> str:
    """
    템플릿에서 문제 영역을 추출하는 프롬프트
    
    Args:
        template_content: 전체 템플릿 내용
        error_text: 발견된 오류 메시지
    
    Returns:
        문제 영역 추출 프롬프트
    """
    
    prompt = f"""당신은 알림톡 템플릿 검증 전문가입니다.
다음 템플릿에서 발견된 오류와 관련된 문제 영역을 정확히 찾아주세요.

**템플릿 내용:**
{template_content}

**발견된 오류:**
{error_text}

**요구사항:**
1. 오류와 직접적으로 관련된 텍스트 영역을 찾아주세요
2. 가능한 한 구체적인 위치를 지정해주세요
3. 문제가 되는 텍스트의 시작과 끝 위치를 정확히 계산해주세요
4. 만약 전체 템플릿에 문제가 있다면 "전체 템플릿"으로 표시해주세요

**응답 형식:**
다음 JSON 형식으로 응답해주세요:

```json
{{
  "area_type": "specific_text|entire_template|variable_usage",
  "location": "문제 영역의 설명",
  "problem_text": "실제 문제가 되는 텍스트",
  "start_position": 시작_위치_숫자,
  "end_position": 끝_위치_숫자,
  "search_methods": {{
    "keyword_search": "검색한 키워드",
    "context_analysis": "컨텍스트 분석 결과",
    "approximate_position": 대략적인_위치
  }}
}}
```

**위치 계산 방법:**
- 템플릿 내용의 첫 번째 문자부터 0부터 시작하여 계산
- 공백, 줄바꿈, 특수문자 모두 포함하여 계산
- start_position은 문제 텍스트의 첫 번째 문자 위치
- end_position은 문제 텍스트의 마지막 문자 다음 위치

**변수 표시 형식:**
- 변수는 {{변수명}} 형식으로 표시해주세요
- 예: #{{고객명}} → {{고객명}}
- 예: #{{40%~60% + 추가10%}} → {{할인율}}

문제 영역을 정확히 찾아주세요."""

    return prompt
