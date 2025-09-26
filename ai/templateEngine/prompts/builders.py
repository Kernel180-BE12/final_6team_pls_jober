from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime
from templateEngine.state import TemplateGenerationState


class BasePromptBuilder(ABC):
    """기본 프롬프트 빌더"""
    def __init__(self, userMessage: str):
        self.userMessage = userMessage
        self.hints: List[Dict] = []

    def add_hint(self, description: str, content: str):
        self.hints.append({"description": description, "content": content})
        return self

    def _build_hint_messages(self) -> List[Dict]:
        return [{"role": "system", "content": h["content"]} for h in self.hints]

    @abstractmethod
    def build(self) -> List[Dict]:
        pass

class FieldsPromptBuilder(BasePromptBuilder):
    """핵심 변수 추출 - 간단하고 명확한 key-value 매핑"""
    def build(self) -> List[Dict]:
        today_str = datetime.now().strftime('%Y-%m-%d')

        system_prompt = f"""당신은 '핵심 변수 추출 전문가'입니다.
사용자 메시지에서 **템플릿 생성에 필요한 핵심 정보만** 추출하여 key-value로 매핑합니다.

**오늘 날짜: {today_str}**

**추출할 핵심 변수 (5가지):**
1. `customer_title`: 고객 호칭 (고객님, 회원님 등)
2. `company_name`: 회사명/브랜드명  
3. `main_content`: 핵심 안내 메시지 (가장 중요한 내용 1-2문장)
4. `contact_info`: 연락처/문의 정보 전체
5. `closing_message`: 마무리 인사/메시지

**추출 원칙:**
- 각 키에 해당하는 **전체 내용**을 value로 매핑
- 중복되는 내용은 가장 적합한 하나의 키에만 매핑
- 없는 정보는 추출하지 않음
- 핵심적이고 변경 가능한 부분만 추출

**완벽한 예시:**
입력: "장수돌침대를 아껴주시는 고객님께 감사드립니다. 겨울철 A/S 및 사전점검을 안내드립니다. 1599-9988로 연락주세요. 감사합니다."

출력:
{{
    "customer_title": "고객님",
    "company_name": "장수돌침대",
    "main_content": "겨울철 A/S 및 사전점검을 안내드립니다",
    "contact_info": "1599-9988로 연락주세요",
    "closing_message": "감사합니다"
}}

**출력 형식:** JSON 객체만 반환하세요.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            *self._build_hint_messages(),
            {"role": "user", "content": f"분석할 본문:\n{self.userMessage}"}
        ]
        return messages


class CategoryPromptBuilder(BasePromptBuilder):
    def __init__(self, userMessage: str, category_sub_list: List[str]):
        super().__init__(userMessage)
        self.category_sub_list = category_sub_list

    def build(self) -> List[Dict]:
        system_prompt = f"""
            당신은 카카오 알림톡 카테고리 분류 전문가입니다.
            주어진 메시지를 분석하여, 아래 '서브 카테고리 후보' 중 가장 적합한 것을 선택하세요.
            
            서브 카테고리 후보:
            {', '.join(self.category_sub_list)}
            
            중요: 만약 후보 중에 적합한 카테고리가 **없다고 판단되면**, "is_appropriate" 값을 false로 설정하고 그 이유를 명확히 설명해주세요.
            
            JSON 형식으로 응답하세요:
            {{
                "is_appropriate": true,
                "category_sub": "선택된 서브 카테고리",
                "confidence": 85,
                "selection_reason": "최종 선택 근거 상세 설명"
            }}
            """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"분석할 메시지:\n{self.userMessage}"}
        ]
        return messages


class NewCategoryPromptBuilder(BasePromptBuilder):
    def __init__(self, userMessage: str, existing_categories: List[str]):
        super().__init__(userMessage)
        self.existing_categories = existing_categories

    def build(self) -> List[Dict]:
        system_prompt = f"""
            당신은 카테고리 네이밍 전문가입니다.
            다음 메시지 내용의 핵심을 가장 잘 나타내는 새로운 카테고리명을 1개 생성해주세요.
            
            생성 규칙:
            1. 기존 카테고리들의 스타일과 형식을 반드시 따르세요.
            2. 간결하고 명확해야 합니다. (2~5자 내외)
            3. 생성된 카테고리명만 JSON 형식으로 응답하세요.
            
            기존 카테고리 스타일 참고:
            {', '.join(self.existing_categories[:10])}
            
            JSON 응답 형식:
            {{
                "new_category": "생성된 카테고리명"
            }}
            """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 메시지에 대한 새로운 카테고리명을 생성해주세요:\n{self.userMessage}"}
        ]
        return message


class TypePromptBuilder(BasePromptBuilder):
    def __init__(self, userMessage: str):
        super().__init__(userMessage)

    def build(self) -> list[dict]:
        prompt = [
            {
                "role": "system",
                "content": """
        너는 카카오 알림 메세지의 유형을 판정하는 분류기다.
        [메세지 유형 정의]
        - BASIC: 핵심 목적(알림/안내/확인 등)만 전달. 링크가 있을 수 있으나, "채널 추가/채널 방문" 목적이 아니면 기본형으로 본다. 
        - 고객에게 반드시 전달되어야 하는 정보
        - EXTRA_INFO:핵심 목적 외에 주의사항·정책·문의·절차·상세 가이드 등 실질적인 추가 설명이 붙음.
        - 이용안내 등 보조적인 정보메시지
        - CHANNEL_ADD: 카카오 채널/브랜드 채널/오픈채팅 등을 추가·구독·방문하도록 유도하는 맥락이 존재. 
        - HYBRID: 채널 추가형 조건 + 부가 정보형 조건을 동시에 충족.  
        [메세지 유형 판정 원칙] 
        1) 먼저 채널 추가 유도 여부를 본다. 단순 웹사이트/배송조회/결제 안내는 채널 추가형이 아니다. 
        2) 다음으로 핵심 목적 외에 실질적인 부가 설명이 있는지 본다. 
        3) 최종 결정: 
        - 둘 다 있으면 HYBRID 
        - 채널 추가만 있으면 CHANNEL_ADD 
        - 부가 설명만 있으면 EXTRA_INFO 
        - 둘 다 없으면 BASIC 
        4) 애매하면 가장 합리적인 단일 유형을 고르고 이유를 간단히 남긴다.  
        [출력 형식(JSON만 출력)] 
        {
        "has_channel_link": true/false,
        "has_extra_info": true/false,
        "type": "BASIC | EXTRA_INFO | CHANNEL_ADD | HYBRID",
        "explain_type": "한 줄 이유"
        }
                """
            },
            *self._build_hint_messages(),
            {
                "role": "user",
                "content": """
        에이프릴키친 입니다.
        라이언님, 안녕하세요.
        소중한 주문이 접수완료 되었습니다.
        - 주문일자: 2024.05.01(토)
        - 금액: 12,0000원
        - 주문번호
        """
            },
            {
                "role": "assistant",
                "content": """
        {
        "has_channel_link": false,
        "has_extra_info": false,
        "type": "BASIC",
        "explain_type": "기본 정보만 포함"
        }
        """
            },
            {
                "role": "user",
                "content": """
        라이언님 안녕하세요.
        객실 정보 안내드립니다.
        - 예약번호: 1234
        - 객실명: 420호
        차량 이용시, 주차가능 여부를 반드시 문의하시기 바랍니다.
        * 예약 취소 시 최소규정에 따라 수수료가 부과될 수 있습니다.
        """
            },
            {
                "role": "assistant",
                "content": """
        {
        "has_channel_link": false,
        "has_extra_info": true,
        "type": "EXTRA_INFO",
        "explain_type": "부가 정보 포함"
        }
        """
            },
            {
                "role": "user",
                "content": """
        [국민카드] 홍길동 1234승인
        50,000원
        3개월
        2025-09-08
        14:35
        ABC 전자상가

        채널 추가하고 이 채널의 마케팅 메시지 등을 카카오톡으로 받기

        [카카오톡 채널 추가 버튼]
        """
            },
            {
                "role": "assistant",
                "content": """
        {
        "has_channel_link": true,
        "has_extra_info": false,
        "type": "CHANNEL_ADD",
        "explain_type": "채널 추가 정보 포함"
        }
        """
            },
            {
                "role": "user",
                "content": """
        카카오톡 명세서 라이언 회원님 결제 명세서 입니다.
        - 당일 결제 금액: 100원
        * 개인정보 보호를 위해 메세지 발송완료 부터 100일까지만, 위의 링크를 통한 상세내용 확인이 가능합니다.
        채널 추가하고 이 채널의 마케팅메세지 등을 카카오톡으로 받기
        """
            },
            {
                "role": "assistant",
                "content": """
        {
        "has_channel_link": true,
        "has_extra_info": true,
        "type": "HYBRID",
        "explain_type": "채널 추가 정보, 부가 정보 포함"
        }
        """
            },
            {
                "role": "user",
                "content": f"본문: {self.userMessage}"
            }
        ]
        return prompt

class TemplateTitlePromptBuilder:
    def __init__(self, userMessage: str):
        self.userMessage = userMessage

    def build(self) -> List[Dict]:
        system_prompt = """
카카오 알림톡 템플릿의 간결한 제목을 생성하는 전문가입니다.

생성 규칙:
1. 8자 이내로 간결하게
2. 메시지의 핵심 목적을 명확히 표현
3. 고객이 한눈에 이해할 수 있는 표현
4. 제목만 출력 (따옴표, 추가 설명 불필요)

예시:
- "점검안내"
- "서비스안내" 
- "예약확인"
- "결제완료"
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 메시지의 제목을 생성해주세요:\n{self.userMessage}"}
        ]
        return messages

class ReferenceBasedTemplatePromptBuilder:
    """참고 템플릿 기반 - 실제 내용으로 완성된 템플릿 생성"""
    def __init__(self, userMessage: str, reference_templates: List[Dict], extracted_fields: Dict[str, str]):
        self.userMessage = userMessage
        self.reference_templates = reference_templates
        self.extracted_fields = extracted_fields

    def build(self) -> List[Dict]:
        reference_context = ""
        for i, template in enumerate(self.reference_templates, 1):
            similarity = template.get('similarity', 0)
            reference_context += f"\n=== 참고 템플릿 {i} (유사도: {similarity:.3f}) ===\n{template.get('text', '')}\n"

        variables_info = self._format_variables()

        system_prompt = f"""당신은 '완성도 있는 알림톡 템플릿 작성자'입니다.

**[미션]**
추출된 변수들과 원본 메시지를 활용하여 **실제 내용으로 완성된** 알림톡 템플릿을 생성하세요.

**[원본 메시지]**
{self.userMessage}

**[추출된 변수들]**
{variables_info}

**[참고 템플릿]**
{reference_context}

**[생성 규칙]**
1. **완성된 내용**: 변수명이나 따옴표 없이 실제 내용으로만 구성
2. **풍부한 구성**: 원본 메시지의 상세한 내용을 최대한 활용
3. **자연스러운 흐름**: 고객이 읽기 편하고 이해하기 쉬운 완성된 문장
4. **실제 값 사용**: 추출된 변수의 value 값들을 자연스럽게 배치

**[완성된 템플릿 예시]**
```
안녕하세요 고객님,

장수돌침대에서 겨울철 서비스 개편을 안내드립니다.

겨울철 대비 장수돌침대 사전 점검 및 A/S 서비스를 안내드립니다.

보다 따뜻하고 안전한 사용을 위해 미리 점검과 유지보수를 권장드립니다. 
정기적인 점검으로 제품의 수명을 연장하고 최상의 성능을 유지하실 수 있습니다.
장수돌침대 서비스만의 전문적인 기술력으로 제품 효율을 극대화해드립니다.

사전점검 및 A/S 문의: 1599-9988
고장이나 이상 증상 시 신속한 상담: 1588-9988

불편함 예방을 위해 사용 전 이상 여부를 미리 확인하시기 바랍니다.

고객님의 겨울을 책임지는 장수돌침대가 되겠습니다.

*본 알림은 정보통신망법에 따라 발송되었습니다.
```

**중요**: 
- 변수명(#{{}}, '', 등) 절대 사용 금지
- 실제 내용으로만 구성된 완성된 템플릿 생성
- 원본의 풍부한 내용을 살려서 구성
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "위 규칙에 따라 완성된 템플릿을 생성해주세요."}
        ]
        return messages

    def _format_variables(self) -> str:
        if not self.extracted_fields:
            return "추출된 변수가 없습니다."

        formatted = []
        for key, value in self.extracted_fields.items():
            formatted.append(f"- {key}: '{value}'")
        return "\n".join(formatted)

    def _format_variables(self) -> str:
        if not self.extracted_fields:
            return "추출된 변수가 없습니다."

        formatted = []
        for key, value in self.extracted_fields.items():
            formatted.append(f"- {key}: '{value}'")
        return "\n".join(formatted)


class NewTemplatePromptBuilder:
    """신규 템플릿 생성 - 실제 내용으로 완성된 템플릿 생성"""
    def __init__(self, userMessage: str, extracted_fields: Dict[str, str], public_templates: Optional[List[Dict]] = None):
        self.userMessage = userMessage
        self.extracted_fields = extracted_fields
        self.public_templates = public_templates or []

    def build(self) -> List[Dict]:
        variables_info = self._format_variables()

        public_context = ""
        if self.public_templates:
            public_context = "\n\n**[공용 템플릿 참고]**\n"
            for i, template in enumerate(self.public_templates[:2], 1):
                public_context += f"{i}. {template.get('text', '')}\n\n"

        system_prompt = f"""당신은 '완성도 있는 알림톡 템플릿 작성자'입니다.

**[미션]**
추출된 변수들과 원본 메시지를 활용하여 **실제 내용으로 완성된** 알림톡 템플릿을 생성하세요.

**[원본 메시지]**
{self.userMessage}

**[추출된 변수들]**
{variables_info}

{public_context}

**[생성 원칙]**
1. **완성된 내용**: 변수명이나 따옴표 없이 실제 내용으로만 구성
2. **풍부한 구성**: 원본 메시지의 상세한 내용을 최대한 활용하여 완성도 있게 구성
3. **자연스러운 문체**: 고객이 이해하기 쉽고 친근하며 전문적인 완성된 문장
4. **실제 값 활용**: 추출된 변수의 실제 값들을 자연스럽게 배치

**[완성된 템플릿 예시 - 장수돌침대 케이스]**
```
안녕하세요 고객님,

장수돌침대에서 겨울철 서비스 개편을 안내드립니다. 내용은 다음과 같습니다.

겨울철 대비 장수돌침대 사전 점검 및 A/S 서비스를 안내드립니다. 보다 따뜻하고 안전한 사용을 위해 미리 점검과 유지보수를 권장드립니다.

정기적인 점검으로 제품의 수명을 연장하고 최상의 성능을 유지하실 수 있습니다.
장수돌침대 서비스만의 전문적인 기술력으로 제품 효율을 극대화해드립니다.

사전점검 및 A/S 문의: 1599-9988
고장이나 이상 증상 시 신속한 상담: 1588-9988

불편함 예방을 위해 사용 전 이상 여부를 미리 확인하시기 바랍니다.

감사합니다.

*본 알림은 정보통신망법에 따라 발송되었습니다.
```

**중요**: 
- 실제 발송 가능한 완성된 템플릿으로 생성
- 원본의 풍부한 내용을 살려서 구성하되 너무 간략하게 하지 말 것
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "위 원칙에 따라 완성된 템플릿을 생성해주세요."}
        ]
        return messages

    def _format_variables(self) -> str:
        if not self.extracted_fields:
            return "추출된 변수가 없습니다."

        formatted = []
        for key, value in self.extracted_fields.items():
            formatted.append(f"- {key}: '{value}'")
        return "\n".join(formatted)

# 백엔드에서 변수 위치를 찾기 위한 매핑 함수

def create_variable_mapping_from_template(template_content: str, extracted_fields: Dict[str, str]) -> Dict[str, str]:
    """완성된 템플릿에서 변수에 해당하는 부분을 찾아 매핑 생성"""
    variable_mapping = {}

    # 추출된 필드의 값들이 템플릿에서 어디에 위치하는지 찾기
    for var_name, original_value in extracted_fields.items():
        if original_value in template_content:
            variable_mapping[var_name] = original_value
        else:
            # 부분 매칭도 시도 (값이 템플릿에 일부만 포함된 경우)
            for line in template_content.split('\n'):
                if any(word in line for word in original_value.split() if len(word) > 2):
                    # 해당 라인에서 변수 값과 가장 유사한 부분 추출
                    variable_mapping[var_name] = line.strip()
                    break

    return variable_mapping


