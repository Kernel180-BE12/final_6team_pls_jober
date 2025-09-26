from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime


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
    """메시지에서 변수로 처리할 필드를 추출하는 프롬프트 빌더"""
    def build(self) -> List[Dict]:
        # 오늘 날짜를 YYYY-MM-DD 형식으로 가져옵니다.
        today_str = datetime.now().strftime('%Y-%m-%d')

        system_prompt = f"""당신은 텍스트에서 변수를 추출하고 정제하는 '데이터 엔지니어'입니다.
주어진 본문에서 **템플릿화할 수 있는 모든 정보**를 찾아 변수로 추출해야 합니다.

**오늘 날짜: {today_str}**

**변수 추출 기준:**
- 개인 정보: 이름, 전화번호, 주소, 주문번호 등
- 호칭/대명사: "고객님", "회원님", 특정 이름 등 **개인화 가능한 모든 호칭**  
- 날짜/시간: 특정 날짜, 기간, 시간 등
- 금액/수치: 가격, 할인율, 수량 등  
- 이벤트 정보: 테마, 장소, 상품명, 브랜드명 등
- 연락처 정보: 전화번호, 이메일 등
- **템플릿에서 다른 값으로 치환될 가능성이 있는 모든 구체적인 정보**

**변수 추출 및 정제 규칙:**
1. **날짜 추론:** '오늘', '내일', '모레'와 같은 상대적인 날짜 표현이 나오면, **오늘 날짜({today_str})를 기준**으로 실제 날짜(YYYY-MM-DD)를 계산하여 값으로 사용해야 합니다.
   - 예: 오늘이 2024-01-15이고 본문에 '내일'이 있으면, 값은 '2024-01-16'이 됩니다.

2. **변수명 규칙:**
   - **영문 소문자**와 **스네이크 케이스(snake_case)**만 사용해야 합니다.
   - 표준 변수명 사용:
     * 고객 이름: `customer_name`
     * 고객 호칭: `customer_title` (예: "고객님", "회원님")
     * 전화번호: `phone_number`  
     * 도착 예정일: `arrival_date`
     * 주문번호: `order_id`
     * 금액: `amount`
     * 할인율: `discount_rate`
     * 장소: `location`
     * 테마/제목: `theme` 또는 `title`
     * 브랜드명: `brand_name`
     * 기간: `event_period` 또는 `start_date`, `end_date`

3. **추출 대상:** 이름, 날짜, 시간, 금액, 주문번호, 할인율, 장소, 상품명, 전화번호, 주소, 테마, 브랜드명, 기간 등 **구체적이고 변경 가능한 모든 정보**를 빠짐없이 추출해야 합니다.
   
   **⚠️ 특별 주의사항:**
   - "고객님", "회원님" 등의 **호칭도 반드시 변수로 추출**하세요 (개인 이름으로 변경 가능)
   - 아무리 일반적인 표현이라도 **개인화 가능한 모든 호칭**은 변수로 처리하세요

**출력 형식:**
- 추출된 값과 그에 해당하는 변수명을 JSON 형식으로 매핑하세요.
- 변수화할 필드가 전혀 없으면, 반드시 빈 JSON 객체를 반환하세요: {{}}

**완벽한 예시 1:**
- 본문: "김철수님, 주문번호 ORD-123이 50,000원 결제 완료되었습니다."
- 응답:
{{
    "customer_name": "김철수",
    "order_id": "ORD-123", 
    "amount": "50,000원"
}}

**완벽한 예시 2:**
- 오늘 날짜: 2024-01-15
- 본문: "고객님의 상품이 내일 도착 예정입니다."
- 응답:
{{
    "arrival_date": "2024-01-16"
}}

**완벽한 예시 3:**
- 본문: "나이키 브랜드 세일 50% 할인! 강남점 1층에서 진행중입니다. 문의: 02-1234-5678"  
- 응답:
{{
    "brand_name": "나이키",
    "discount_rate": "50%",
    "location": "강남점 1층",
    "phone_number": "02-1234-5678"
}}

**완벽한 예시 4:**
- 본문: "오일릴리 이월행사가 2021년 10월 06일부터 10월 10일까지 롯데백화점 광주점 9층에서 진행됩니다."
- 응답:
{{
    "brand_name": "오일릴리",
    "theme": "이월행사", 
    "start_date": "2021년 10월 06일",
    "end_date": "2021년 10월 10일",
    "location": "롯데백화점 광주점 9층"
}}

**완벽한 예시 5:**
- 본문: "안녕하세요 고객님, 롯데백화점에서 특별 할인 행사를 진행합니다."
- 응답:
{{
    "customer_title": "고객님",
    "location": "롯데백화점"
}}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            *self._build_hint_messages(), # 힌트가 있다면 여기에 추가됨
            {"role": "user", "content": f"분석할 본문:\n{self.userMessage}"}
        ]
        return messages

class CategoryPromptBuilder(BasePromptBuilder):
    """카테고리 분류 프롬프트 빌더 - 적합성 판단 기능 추가"""
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
            // 또는, 적합한 것이 없을 경우:
            {{
                "is_appropriate": false,
                "category_sub": null,
                "confidence": 30,
                "selection_reason": "예: '사전 점검 및 AS 안내'는 단순 '방문서비스'나 '이용안내'와는 성격이 달라 적합한 후보가 없습니다."
            }}
            """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"분석할 메시지:\n{self.userMessage}"}
        ]
        return messages


class NewCategoryPromptBuilder(BasePromptBuilder):
    """신규 카테고리 생성 프롬프트 빌더"""
    def __init__(self, userMessage: str, existing_categories: List[str]):
        super().__init__(userMessage)
        self.existing_categories = existing_categories

    def build(self) -> List[Dict]:
        system_prompt = f"""
            당신은 카테고리 네이밍 전문가입니다.
            다음 메시지 내용의 핵심을 가장 잘 나타내는 새로운 카테고리명을 1개 생성해주세요.
            
            생성 규칙:
            1. 기존 카테고리들의 스타일과 형식을 반드시 따르세요. (예: '구매완료', '배송상태' 처럼 '명사' 또는 '명사+동사' 형태)
            2. 간결하고 명확해야 합니다. (2~5자 내외)
            3. 생성된 카테고리명만 JSON 형식으로 응답하세요.
            
            기존 카테고리 스타일 참고:
            {', '.join(self.existing_categories[:10])} # 일부만 보여줘도 스타일 파악 가능
            
            JSON 응답 형식:
            {{
                "new_category": "생성된 카테고리명"
            }}
            """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 메시지에 대한 새로운 카테고리명을 생성해주세요:\n{self.userMessage}"}
        ]
        return messages

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
    """템플릿 제목 생성 프롬프트 빌더"""
    def __init__(self, userMessage: str):
        self.userMessage = userMessage

    def build(self) -> List[Dict]:
        system_prompt = """
카카오 알림톡 템플릿의 제목을 생성하는 전문가입니다.
다음 규칙을 따라 제목을 생성하세요:

1. 10자 이내로 간결하게
2. 메시지의 핵심 내용을 포함
3. 사용자가 쉽게 이해할 수 있는 명확한 표현
4. 제목만 출력 (추가 설명 불필요)
5. 따옴표(" 또는 ')는 절대 사용하지 마세요

올바른 예시:
- 주문완료 안내
- 배송출발 알림
- 예약확정 통보

잘못된 예시 (따옴표 포함):
- "주문완료 안내"
- '배송출발 알림'
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 메시지의 제목을 생성해주세요:\n{self.userMessage}"}
        ]

        return messages

class ReferenceBasedTemplatePromptBuilder:
    """참고 템플릿 기반 생성 프롬프트 빌더"""
    def __init__(self, userMessage: str, reference_templates: List[Dict], extracted_fields: Dict):
        self.userMessage = userMessage
        self.reference_templates = reference_templates
        self.extracted_fields = extracted_fields

    def build(self) -> List[Dict]:
        """
        - 참고 템플릿들을 문자열로 구성
        - LLM에게 제목,목적 등 추가적인 맥락을 제공하여, 생성될 템플릿의 목적성을 더 명확하게 만듦.
        """
        reference_context = ""
        for i, template in enumerate(self.reference_templates, 1):
            similarity = template.get('similarity', 0)
            metadata = template.get('metadata', {})
            # 👇 메타데이터에서 '자동 생성 제목'이나 '목적 분류' 같은 유용한 정보를 추가
            title_hint = metadata.get('자동 생성 제목', '제목 정보 없음')

            reference_context += f"\n=== 참고 템플릿 {i} (유사도: {similarity:.3f}, 제목: '{title_hint}') ===\n{template.get('text', '')}\n"

    # 👇 변수 처리 규칙을 명시적으로 추가
        variable_rules = ""
        if self.extracted_fields:
            variable_rules = "\n\n**중요 변수 처리 규칙:**\n"
            variable_rules += "다음 텍스트는 반드시 지정된 변수명으로 대체하여 `#{{변수명}}` 형태로 표현해야 합니다.\n"
            variable_rules += "**모든 변수는 반드시 #{{변수명}} 형태로만 작성해야 합니다. {{변수명}} 형태는 사용하지 마세요.**\n"
            for value, var_name in self.extracted_fields.items():
                variable_rules += f"- '{value}'는 -> `#{{{var_name}}}'\n`으로 변경하세요.\n"

        system_prompt = f"""
            당신은 최고의 템플릿 구조를 분석하고 모방하는 '템플릿 아키텍트'입니다.
            
            **[미션]**
            1.  아래에 제공된 '참고 템플릿'들의 **구조적 장점(줄 바꿈, 항목 구분, 강조 표시 등)을 분석**하세요.
            2.  분석한 구조를 바탕으로, '사용자 요청'과 '변수 처리 규칙'에 맞춰 가장 이상적인 새 템플릿을 **재창조**하세요.
            
            {variable_rules}
            다음 승인된 템플릿들을 참고하여 새로운 템플릿을 생성하세요:
            
            **[참고 템플릿 분석]**
            {reference_context}
            
            **[학습 포인트]**
            - 위 참고 템플릿들에서 `#{{변수명}}`이 어떤 위치에, 어떤 이름으로 사용되었는지 학습하세요.
            - 예를 들어, 참고 템플릿에 `#{{order_no}}`가 있다면, 새로운 템플릿에서도 주문번호는 비슷한 위치에 `#{{order_id}}`와 같이 배치하는 것이 좋습니다.
            
            생성 규칙:
<<<<<<< HEAD
            1. 변수는 반드시 #{{변수명}} 형태로만 표현, 변수 처리 규칙을 100% 준수해야 합니다. {{변수명}} 형태는 절대 사용하지 마세요.
            2. 참고 템플릿의 구조 모방 : 참고 템플릿의 인사말, 본문, 항목 구분(예: '■'), 마무리, 발송 근거 등의 구조를 적극적으로 따라야 합니다.
            3. 톤앤매너 유지
            3. 광고성 내용 금지, 정보성/안내성 내용만
            4. 발송 근거를 하단에 명시 (*로 시작)
            5. 카카오톡 알림톡 규정 준수
            6. **내용 창작:** 구조는 모방하되, 내용은 '사용자 요청'에 맞게 새롭게 작성해야 합니다.
            
            템플릿 본문만 출력하세요 (변수 설명이나 추가 안내 불포함):
            """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"사용자 요청:\n{self.userMessage}"}
        ]

        return messages

class NewTemplatePromptBuilder:
    """신규 템플릿 생성 프롬프트 빌더 - 카카오 공용 템플릿 기반"""
    def __init__(self, userMessage: str,  extracted_fields: Dict, public_templates: Optional[List[Dict]] = None):
        self.userMessage = userMessage
        self.extracted_fields = extracted_fields  # 👈 전달받은 인자를 self.extracted_fields에 저장
        self.public_templates = public_templates or []

    def build(self) -> List[Dict]:
        public_context = ""
        if self.public_templates:
            public_context = "\n\n=== 카카오 공용 템플릿 참고 ===\n"
            for i, template in enumerate(self.public_templates[:3], 1):  # 최대 3개만
                public_context += f"{i}. {template.get('text', '')}\n\n"
        # 👇 변수 처리 규칙을 명시적으로 추가
        variable_rules = ""
        if self.extracted_fields:
            variable_rules = "\n\n**🔥 중요 변수 처리 규칙 (반드시 준수):**\n"
            variable_rules += "아래 규칙에 따라, 원본 메시지의 특정 단어를 `#{{변수명}}` 형태로 반드시 교체해야 합니다.\n"
            variable_rules += "**모든 변수는 반드시 #{{변수명}} 형태로만 작성해야 합니다. {{변수명}} 형태는 절대 사용하지 마세요.**\n"
            variable_rules += "**변수 처리 규칙을 위반하면 템플릿이 거부됩니다.**\n\n"
            # extracted_fields가 { "변수값": "변수명" } 형태라고 가정
            for value, var_name in self.extracted_fields.items():
                variable_rules += f"- '{value}' → `#{{{var_name}}}` (반드시 이 형태로 변경)\n"
            variable_rules += "\n**변수 처리 예시:**\n"
            variable_rules += "- '오일릴리' → `#{{brand_name}}`\n"
            variable_rules += "- '이월행사' → `#{{theme}}`\n"
            variable_rules += "- '40%~60%' → `#{{discount_rate}}`\n"

        system_prompt = f"""
            **[당신의 역할]**
            당신은 15년차 카피라이터이자 카카오 알림톡 템플릿 검수 전문가입니다.
            고객에게 전달되는 메시지인 만큼, 명확하고 친절하며 프로페셔널한 톤앤매너를 유지해야 합니다.
            아래 제공된 모든 규칙을 완벽하게 준수하여, 단 하나의 템플릿만 생성해야 합니다.
            사용자가 제공한 '변수 처리 규칙'을 완벽하게 준수해야 합니다.
            
            {variable_rules}
            **[필수 규칙 2: 템플릿 구조]**
            1.  **인사:** "안녕하세요, 고객님." 과 같이 부드러운 문장으로 시작합니다.
            2.  **핵심 내용:** 전달하려는 가장 중요한 내용을 먼저 제시합니다.
            3.  **상세 정보 (선택 사항):** 필요시, '•' 기호를 사용하여 정보를 항목별로 명확하게 구분합니다.
            4.  **마무리:** "감사합니다." 또는 "많은 이용 부탁드립니다." 와 같은 긍정적인 문장으로 끝맺습니다.
            5.  **발송 근거:** 템플릿 가장 마지막 줄에는 `*`로 시작하는 발송 근거를 반드시 포함해야 합니다. (예: `*본 알림은 정보통신망법에 따라 발송되었습니다.`)
            6.  **변수 형태:** 모든 변수는 반드시 `#{{변수명}}` 형태로만 작성해야 합니다. `{{변수명}}` 형태는 절대 사용하지 마세요.

            **[좋은 템플릿의 조건]**
            1.  **친절함:** 딱딱하지 않고 부드러운 문장으로 시작하고 끝냅니다.
            2.  **명확성:** 핵심 정보를 쉽게 파악할 수 있도록 줄 바꿈과 구성을 활용합니다.
            3.  **정확성:** 변수 규칙을 포함한 모든 규칙을 100% 준수합니다.
            4.  **완성도:** 의미없는 텍스트나 중간에 끊어진 문장이 없어야 합니다.
            5.  **일관성:** 모든 불릿 포인트는 '•' 기호를 사용해야 합니다.
            
            **[생성 예시]**
            - 사용자 요청: "김철수님, 주문하신 상품(스마트폰)이 정상적으로 접수되었습니다. 주문번호는 ORD-2024-001이며, 결제금액은 850,000원입니다."
            - 변수 규칙: '김철수' -> `customer_name`, 'ORD-2024-001' -> `order_id`, '850,000' -> `amount`
            - 좋은 템플릿 결과 (모든 변수는 #{{변수명}} 형태):
            안녕하세요, #{{customer_name}}님.
            주문하신 상품이 정상적으로 접수되었습니다.
            
            • 주문번호: #{{order_id}}
            • 결제금액: #{{amount}}원
            
            상품 준비 후 배송이 시작되면 다시 한번 안내해 드리겠습니다.
            저희 서비스를 이용해 주셔서 감사합니다.
            
            *본 알림은 정보통신망법에 따라 발송되었습니다.
            
            ---
            위 예시와 모든 규칙을 참고하여, 주어진 요청에 맞는 최고의 템플릿을 생성해주세요.
            
            {public_context}
            
            **⚠️ 중요 주의사항:**
            - 템플릿은 반드시 완성된 형태로 생성하세요
            - 의미없는 텍스트나 중간에 끊어진 문장이 없어야 합니다
            - 모든 문장은 완전하고 의미가 있어야 합니다
            - "다양한 삿포득을 학이되" 같은 의미없는 텍스트는 절대 생성하지 마세요
            
            템플릿 본문만 출력하세요:
            """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 요청에 맞는 알림톡 템플릿을 생성해주세요:\n{self.userMessage}"}
        ]
        return messages
