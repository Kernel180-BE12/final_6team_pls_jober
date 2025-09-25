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
    """
    실제 발송에 바로 사용 가능한 변수 추출 프롬프트 빌더
    요청사항을 반영하여 main_message, sub_message 등을 추출하도록 개선
    """
    def build(self) -> List[Dict]:
        today_str = datetime.now().strftime('%Y-%m-%d')

        system_prompt = f"""당신은 '실용적 템플릿 변수 추출 전문가'입니다.
메시지 내용을 분석하여, **개인화/재사용이 필요한 핵심 부분만** key-value 쌍으로 추출합니다.

**오늘 날짜: {today_str}**

**변수 추출 원칙:**
1. **내용 보존**: 원본 메시지의 내용과 구조를 최대한 그대로 유지합니다.
2. **의미 단위 추출**: 각 문단이나 문장을 의미에 맞는 key로 매핑합니다.
3. **실용성**: 실제 템플릿 생성에 바로 사용 가능한 형태로 추출합니다.

**추출할 Key 목록 (의미에 맞게 매핑):**
- `customer_title`: 고객 호칭 (예: "고객님", "회원님")
- `company_name`: 회사명 또는 브랜드명
- `main_message`: 가장 핵심적인 안내 문장 또는 문단
- `sub_message`: `main_message`를 보충하는 상세 설명 문단
- `contact_info`: A/S, 상담, 문의 등 연락처 정보 전체 문구
- `closing_message`: 마무리 인사말

**완벽한 예시:**
- 원본:
장수돌침대를 아껴 주시는 고객님 반갑습니다.
겨울철 장수돌침대 사용량 증가로 A/S 및 사전점검 일정을 미리 준비하여 따뜻한 겨울 편안하고 안전하게 사용을 권장 드리고 있습니다.
1599-9988 당사로 연락 주시면 빠른 점검 및 A/S 진행 도와드리겠습니다.
고객님의 겨울을 책임지는 장수돌침대 가 되겠습니다~ 감사합니다

- 추출 결과 (JSON):
{{
    "customer_title": "고객님",
    "company_name": "장수돌침대",
    "main_message": "겨울철 장수돌침대 사용량 증가로 A/S 및 사전점검 일정을 미리 준비하여 따뜻한 겨울 편안하고 안전하게 사용을 권장 드리고 있습니다.",
    "contact_info": "1599-9988 당사로 연락 주시면 빠른 점검 및 A/S 진행 도와드리겠습니다.",
    "closing_message": "고객님의 겨울을 책임지는 장수돌침대 가 되겠습니다~ 감사합니다"
}}

**출력 형식:**
- 추출된 변수와 값을 JSON 형식으로만 반환합니다.
- 변수화할 내용이 없으면 빈 객체 `{{}}`를 반환합니다.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            *self._build_hint_messages(),
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

예시:
- "주문완료 안내"
- "배송출발 알림"
- "예약확정 통보"
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 메시지의 제목을 생성해주세요:\n{self.userMessage}"}
        ]

        return messages

class ReferenceBasedTemplatePromptBuilder:
    """
    [수정됨] 참고 템플릿 기반 - 변수를 치환하여 최종 템플릿 텍스트를 생성
    """
    def __init__(self, userMessage: str, reference_templates: List[Dict], extracted_fields: Dict):
        self.userMessage = userMessage
        self.reference_templates = reference_templates
        self.extracted_fields = extracted_fields

    def build(self) -> List[Dict]:
        reference_context = ""
        for i, template in enumerate(self.reference_templates, 1):
            similarity = template.get('similarity', 0)
            metadata = template.get('metadata', {})
            title_hint = metadata.get('자동 생성 제목', '제목 정보 없음')
            reference_context += f"\n=== 참고 템플릿 {i} (유사도: {similarity:.3f}, 제목: '{title_hint}') ===\n{template.get('text', '')}\n"

        # 변수 치환 규칙을 명확히 전달
        variable_instructions = "\n\n**변수 치환 규칙:**\n"
        variable_instructions += "아래 변수들을 사용하여 자연스러운 문장을 만드세요:\n"
        for key, value in self.extracted_fields.items():
            variable_instructions += f"- `#{{{key}}}` 자리에 '{value}' 내용을 활용하세요.\n"

        system_prompt = f"""당신은 '실용적 알림톡 템플릿 제작자'입니다.

**[미션]**
주어진 변수(`extracted_fields`)와 참고 템플릿을 활용하여, **사용자에게 보여줄 최종 알림톡 템플릿 본문**을 생성하세요.

{variable_instructions}

**[참고 템플릿 분석]**
{reference_context}

**[템플릿 생성 규칙]**
1. **Value 중심**: 최종 결과물에는 `#{{변수명}}` 같은 key나 변수 표시가 전혀 보이면 안 됩니다.
2. **자연스러운 조합**: 변수 값(Value)들을 자연스럽게 연결하여 완성된 하나의 글로 만드세요.
3. **구조와 톤앤매너**: 참고 템플릿의 구조와 친근한 톤앤매너를 따르세요.
4. **내용 보존**: 원본 메시지의 핵심 내용과 감성을 그대로 살려야 합니다.
5. **출력 형식**: **템플릿 본문 텍스트만** 출력하세요. (JSON, 추가 설명 절대 금지)

**[생성 예시]**
안녕하세요, 고객님.

장수돌침대에서 안내드립니다.

겨울철 장수돌침대 사용량 증가로 A/S 및 사전점검 일정을 미리 준비하여 따뜻한 겨울 편안하고 안전하게 사용을 권장 드리고 있습니다.

1599-9988 당사로 연락 주시면 빠른 점검 및 A/S 진행 도와드리겠습니다.

고객님의 겨울을 책임지는 장수돌침대 가 되겠습니다~ 감사합니다
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"위 규칙에 따라 최종 템플릿을 생성해주세요."}
        ]
        return messages


class NewTemplatePromptBuilder:
    """
    [수정됨] 신규 템플릿 생성 - 추출된 변수(Value)를 조합하여 최종 템플릿 텍스트를 생성
    """
    def __init__(self, userMessage: str, extracted_fields: Dict[str, Any], public_templates: Optional[List[Dict]] = None):
        self.userMessage = userMessage
        self.extracted_fields = extracted_fields or {}
        self.public_templates = public_templates or []

    def build(self) -> List[Dict]:
        # 변수(Value)들을 프롬프트에 명확히 전달
        variable_values = "\n\n**사용할 문장/단어 (Value):**\n"
        for key, value in self.extracted_fields.items():
            variable_values += f"- {value} (이 내용은 '{key}'에 해당함)\n"

        system_prompt = f"""**[당신의 역할]**
당신은 '고객 친화적 알림톡 템플릿 작성 전문가'입니다.

**[미션]**
아래에 주어진 문장과 단어(Value)들을 조합하여, 고객에게 발송할 **최종 알림톡 템플릿 본문**을 자연스러운 하나의 글로 완성하세요.

{variable_values}

**[템플릿 생성 핵심 원칙]**
1. **Value만 사용**: 최종 결과물에는 key 이름이나 JSON 형식이 전혀 보이면 안 됩니다. 오직 주어진 Value들을 조합한 텍스트만 있어야 합니다.
2. **자연스러운 흐름**: 어색하지 않게 문장들을 연결하고, 필요한 경우 "안녕하세요," "감사합니다." 같은 기본 인사말을 추가하여 완성도를 높이세요.
3. **가독성**: 문단 구분이 필요하면 엔터(줄바꿈)를 적절히 사용하세요.
4. **출력 형식**: **생성된 템플릿 본문 텍스트만** 응답으로 출력해야 합니다. (JSON, 코드 블록, 부가 설명 절대 금지)

**[완벽한 생성 예시]**
안녕하세요, 회원님.

올워크에서 안내드립니다.

여러분의 미소를 지키기 위한 새로운 기회를 소개합니다.

치과 방문 더 이상 미루지 마세요. 올워크가 신뢰할 수 있는 치과와 손잡았습니다. 회원분들에게 합리적인 비용과 특별한 혜택을 제공합니다.

지금 바로 치과 방문 신청서를 작성하세요!

여러분의 건강한 치아를 위해, 올워크가 함께합니다.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "위 원칙과 예시에 따라, 주어진 Value들을 조합하여 최종 템플릿을 생성해주세요."}
        ]
        return messages


async def extract_fields_node(state: TemplateGenerationState) -> Dict[str, Any]:
    logger.info("=" * 60)
    logger.info("✨ 실용적 변수 필드 추출 시작")
    response = ""
    clean_response = ""
    try:
        user_message = state.get("userMessage")
        openai_service = state.get("openai_service")

        if not user_message:
            logger.error("❌ 'userMessage'가 state에 없습니다.")
            return {"extracted_fields": {}}
        if not openai_service:
            logger.error("❌ 'openai_service'가 state에 없습니다.")
            return {"extracted_fields": {}}

        prompt_builder = FieldsPromptBuilder(state["userMessage"])
        messages = prompt_builder.build()
        # response = await state["openai_service"].chat_completion(messages) # 실제 환경에서는 이 코드를 사용
        # 테스트를 위한 Mock 응답
        response = """
        ```json
        {
            "customer_title": "고객님",
            "company_name": "장수돌침대",
            "main_message": "겨울철 장수돌침대 사용량 증가로 A/S 및 사전점검 일정을 미리 준비하여 따뜻한 겨울 편안하고 안전하게 사용을 권장 드리고 있습니다.",
            "sub_message": "가을이 오기 전 장수돌침대 사전점검과 함께 따뜻하고 편안한 겨울 지내시길 요청 드립니다.\\n장수제품의 수명을 길게 유지하고 최상의 성능을 발휘하려면, 정기적인 유지보수와 관리가 중요합니다.\\n장수돌침대 서비스만의 전문적인 기술력으로 제품의 수명과 청결로 전기세를 아끼고 효율을 극대화하세요!\\n고객님들 사전에 고장 체크해보시고 이상 있을 경우 미리 서비스 받아두셔서 불편함이 없도록 하시기 바랍니다.",
            "contact_info": "1599-9988 당사로 연락 주시면 빠른 점검 및 A/S 진행 도와드리겠습니다.\\n장수돌침대 사용 중 고장이나 이상증상이 있으신 경우 1588-9988 으로 전화 주시면 신속하고 친절한 상담 도와드리겠습니다.",
            "closing_message": "고객님의 겨울을 책임지는 장수돌침대 가 되겠습니다~ 감사합니다"
        }
        ```
        """
        logger.debug(f"OpenAI API 원본 응답: {response}")

        json_match = re.search(r'```json\s*({.*?})\s*```', response, re.DOTALL)
        if json_match:
            clean_response = json_match.group(1)
        else:
            json_match = re.search(r'({.*?})', response, re.DOTALL)
            if json_match:
                clean_response = json_match.group(1)
            else:
                clean_response = response.strip()

        if not clean_response:
            logger.warning("⚠️ 변수 추출 결과가 비어있습니다. 빈 객체를 반환합니다.")
            return {"extracted_fields": {}}

        result = json.loads(clean_response)

        if not isinstance(result, dict):
            logger.warning(f"⚠️ 추출된 결과가 딕셔너리 형식이 아닙니다: {result}. 빈 객체를 반환합니다.")
            return {"extracted_fields": {}}

        logger.info(f"✅ 추출된 변수 필드: {result}")
        return {"extracted_fields": result}
    except json.JSONDecodeError as e:
        logger.error(f"❌ 변수 필드 추출 JSON 파싱 실패: {e}", exc_info=True)
        logger.error(f"   파싱 실패한 원본 응답: {response}")
        logger.error(f"   파싱 시도한 클린 응답: {clean_response}")
        return {"extracted_fields": {}}
    except Exception as e:
        logger.error(f"❌ 변수 필드 추출 실패: {e}", exc_info=True)
        logger.error(f"   원본 응답: {response}")
        return {"extracted_fields": {}}