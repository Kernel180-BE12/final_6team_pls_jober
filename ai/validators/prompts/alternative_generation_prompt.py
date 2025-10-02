"""
배치 대안 생성 프롬프트
여러 오류에 대한 대안을 한 번의 API 호출로 생성하는 프롬프트
"""

def get_batch_alternative_generation_prompt(stage: str, errors: list, template_content: str = "") -> str:
    """
    여러 오류에 대한 대안을 배치로 생성하는 프롬프트
    
    Args:
        stage: 검증 단계 (constraint, semantic 등)
        errors: 오류 메시지 리스트
        template_content: 템플릿 내용 (선택사항)
    
    Returns:
        배치 대안 생성 프롬프트
    """
    
    # 오류 목록을 문자열로 변환
    errors_text = "\n".join([f"{i+1}. {error}" for i, error in enumerate(errors)])
    
    prompt = f"""당신은 알림톡 템플릿 검증 전문가입니다. 
{stage} 검증 단계에서 발견된 다음 오류들에 대한 구체적이고 실용적인 대안을 제시해주세요.

**발견된 오류들:**
{errors_text}

**템플릿 내용 (참고용):**
{template_content[:500] if template_content else "템플릿 내용이 제공되지 않았습니다."}

**요구사항:**
1. 각 오류에 대해 2-3개의 구체적인 대안을 제시하세요
2. 대안은 실제로 적용 가능한 수정 방안이어야 합니다
3. 알림톡 승인 규칙을 준수하는 방향으로 제시하세요
4. 간결하고 명확한 언어를 사용하세요
5. 변수는 {{변수명}} 형식으로 표시하세요 (예: {{고객명}}, {{할인율}})

**대안 형식 규칙:**
- 각 대안은 반드시 다음 구조를 따라야 합니다:
  - "기존_텍스트" → "수정된_텍스트" (텍스트 교체의 경우)
  - "REMOVE_BULLET_TYPE" (불릿 포인트 삭제의 경우)
  - "수정된_텍스트" (새로운 텍스트 추가의 경우)

**응답 형식:**
다음 JSON 형식으로 응답해주세요:

```json
{{
  "alternatives": {{
    "할인율과 관련된 구체적인 혜택이 제공되고 있습니다.": [
      "쿠폰 제공해드립니다 → 쿠폰 확인하세요",
      "특별 할인 혜택 → 다양한 혜택",
      "REMOVE_DISCOUNT_BULLET"
    ],
    "강한 광고성 표현이 포함되어 있음": [
      "지금 바로 → 확인해보세요",
      "놓치지 마세요 → 참고해주세요"
    ]
  }}
}}
```

**중요**: 
- 키는 반드시 위의 오류 메시지와 정확히 일치해야 합니다.
- 대안은 "기존텍스트 → 수정텍스트" 형식으로 작성하거나, 불릿 포인트 삭제는 "REMOVE_타입_BULLET" 형식으로 작성하세요.
- 각 오류에 대한 대안을 제시해주세요."""

    return prompt


def get_single_alternative_generation_prompt(stage: str, error: str, template_content: str = "") -> str:
    """
    단일 오류에 대한 대안을 생성하는 프롬프트
    
    Args:
        stage: 검증 단계
        error: 오류 메시지
        template_content: 템플릿 내용
    
    Returns:
        단일 대안 생성 프롬프트
    """
    
    prompt = f"""당신은 알림톡 템플릿 검증 전문가입니다.
{stage} 검증 단계에서 다음 오류가 발견되었습니다.

**발견된 오류:**
{error}

**템플릿 내용:**
{template_content[:500] if template_content else "템플릿 내용이 제공되지 않았습니다."}

**요구사항:**
1. 이 오류를 해결할 수 있는 3개의 구체적인 대안을 제시하세요
2. 대안은 실제로 적용 가능한 수정 방안이어야 합니다
3. 알림톡 승인 규칙을 준수하는 방향으로 제시하세요
4. 간결하고 명확한 언어를 사용하세요

**대안 형식 규칙:**
- 각 대안은 반드시 다음 구조를 따라야 합니다:
  - "기존_텍스트" → "수정된_텍스트" (텍스트 교체의 경우)
  - "REMOVE_BULLET_TYPE" (불릿 포인트 삭제의 경우)
  - "수정된_텍스트" (새로운 텍스트 추가의 경우)

**응답 형식:**
다음 JSON 형식으로 응답해주세요:

```json
{{
  "alternatives": [
    "쿠폰 제공해드립니다 → 쿠폰 확인하세요",
    "특별 할인 혜택 → 다양한 혜택",
    "REMOVE_DISCOUNT_BULLET"
  ]
}}
```

**중요**: 
- 대안은 "기존텍스트 → 수정텍스트" 형식으로 작성하거나, 불릿 포인트 삭제는 "REMOVE_타입_BULLET" 형식으로 작성하세요.
- 이 오류에 대한 대안을 제시해주세요."""

    return prompt
