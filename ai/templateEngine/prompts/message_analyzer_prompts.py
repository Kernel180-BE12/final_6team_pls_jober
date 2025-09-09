"""
메시지 분석용 프롬프트 템플릿들
"""
from abc import ABC, abstractmethod

class BasePromptBuilder(ABC):
    def __init__(self, user_text: str):
        self.user_text = user_text
        self.hints: list[dict] = []

    def add_hint(self, description: str, content: str):
        """모든 힌트는 system role"""
        self.hints.append({"description": description, "content": content})
        return self

    def _build_hint_messages(self) -> list[dict]:
        return [
            {
                "role": "system",
                "content": h["content"]  # 문자열 그대로 넣음
            }
            for h in self.hints
        ]

    @abstractmethod
    def build(self) -> list[str]:
        """프롬프트 빌드 로직은 구체 빌더가 구현"""
        pass


class TypePromptBuilder(BasePromptBuilder):
    def __init__(self, user_text: str):
        super().__init__(user_text)

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
                "content": f"본문: {self.user_text}"
            }
        ]
        return prompt


class FieldsPromptBuilder(BasePromptBuilder):
    def __init__(self, user_text: str):
        super().__init__(user_text)
        self.hints: list[dict] = []
    
    def build(self) -> list:
        prompt = [
            {
                "role": "system",
                "content": r"""
                    너는 카카오 알림 메시지에서 구조화된 값을 추출하는 추출기다.
                    아래 본문을 읽고 지정된 스키마에 맞춰 JSON만 출력하도록

                    [스키마 설명]
                    - intent_type: 메시지의 의도 유형
                      - 반드시 ["정보성", "인증", "광고성", "기타"] 중 하나로 출력
                    - label: 사람이 이해하기 쉬운 짧은 라벨 (5~15자, 제목형 명사구).
                      - 예: "특강안내", "포인트 소멸 안내", "배송 지연 공지"
                    - use_case: 메시지의 활용 맥락(유스케이스, 목적).
                      - 예: "마케팅 특강 일정 및 장소 안내", "포인트 소멸 정책 및 만료일 고지"
                    - recipient_scope: 수신자 범위
                      - ["신규가입자", "전체회원", "구매자", "신청자", "기타"] 중 하나로 출력
                    - links_allowed: 본문 내 링크 허용 여부
                      - "http", "https", "www" 등 URL 또는 버튼 링크가 있으면 true, 없으면 false
                    - variables: 본문 내 변수 placeholder 배열
                      - `#{NAME}`, `#{SHOPNAME}` 같은 형식 그대로 추출
                      - 추가로 메시지 안에서 **변수처럼 역할**을 하는 자연어 표현(이름, 주문, 일시, 기간, 장소, 문의, 전화번호, 주소 등)도 반드시 포함
                      - 날짜(예: "2025-09-04"), 시간, 금액, 퍼센트, 전화번호는 전부 변수로 추출

                    [규칙]
                    1. 반드시 JSON만 출력할 것.
                    2. null은 절대 쓰지 말고, 불명확하면 "기타"로 채운다.
                    3. Boolean은 true/false만 사용.
                    4. 배열이 없으면 []로.
                    5. JSON 형식이 틀리면 안 된다. 오직 JSON만 출력한다.

                    [출력 형식(JSON)]
                    {
                    "intent_type": "string|null",
                    "label": "string|null",
                    "use_case": "string|null",
                    "recipient_scope": "string|null",
                    "links_allowed": true/false,
                    "variables": ["..."] or []
                    }
                """
            },
            *self._build_hint_messages(),
            {
                "role": "user",
                "content": r"""
                    안녕하세요 홍길동님, 배달이 취소되었습니다. 
                    취소된 내역을 확인하시고 본인이 주문하시지 않은 경우 연락 부탁드립니다. 
                    ▶ 주문 일시 : 2025-09-04
                    ▶ 주문 내역 : 황금 올리브 
                    ▶ 취소 내역 : 사용자 주문  취소 
                    다시 주문을 하시려면 아래 "주문하기" 를 눌러주세요. 
                    배송 배송상태 배달 취소 안내
                """
            },
            {
                "role": "assistant",
                "content": r"""
                    {
                    "intent_type": "정보성",
                    "label": "배달취소안내",
                    "use_case": "주문 내역 취소 및 재주문 안내",
                    "recipient_scope": "구매자",
                    "links_allowed": true,
                    "variables": ["#{수신자명}", "#{주문 일시}", "#{주문 내역}", "#{취소 내역}"]
                    }
                """
            },
            {
                "role": "user",
                "content": r"""
                    [무료 휴가 관련 정보 안내]  
                    # 안녕하세요, 라이언 고객님   
                    # 무료 휴가에 대한 상세 내용을 아래와 같이 안내드립니다.  
                    # ▶ 내용: 이번주 하루! 무료 휴가를 드립니다!   
                    # ▶ 기간: 9월 2째 주
                    # ▶ 유의사항: 선착순이니 조기마감 될 수도 있습니다.  
                    # ※ 본 메시지는 해당 이벤트 정보 제공을 요청하신 고객님께 발송된 일회성 안내입니다.
                """
            },
            {
                "role": "assistant",
                "content": r"""
                    {
                    "intent_type": "광고성",
                    "label": "이벤트안내",
                    "use_case": "무료 휴가 프로모션 일정 및 유의사항 안내",
                    "recipient_scope": "신청자",
                    "links_allowed": false,
                    "variables": ["#{이벤트명}", "#{수신자명}", "#{내용}", "#{기간}", "#{유의사항}"]
                    }
                """
            },
            {
                "role": "user",
                "content": f"본문: {self.user_text}"
            }
        ]
        return prompt


class CategoryPromptBuilder(BasePromptBuilder):
    def __init__(self, user_text: str, category_main: str, category_sub_list: list):
        super().__init__(user_text)
        self.hints: list[dict] = []
        self.category_main = category_main
        self.category_sub_list = category_sub_list
    
    def build(self) -> list:
        prompt = [
            {
                "role": "system",
                "content": """
        너는 카카오 알림톡의 서브 카테고리를 판정하는 분류기다.
        [서브 카테고리 판정 규칙] 
        - 입력된 본문을 읽고, 아래 제공된 서브 카테고리 리스트 중 가장 유사한 하나를 반드시 선택한다. 
        - 리스트에 없는 임의의 값을 생성하지 않는다.  
        [서브 카테고리 판정 원칙]
        1) 먼저 사용자 본문 내용과 가장 적절한 서브 카테고리를 고른다.
        2) 애매하면 가장 합리적인 단일 유형을 고르고 이유를 간단히 남긴다.  
        [출력 형식(JSON만 출력)]
        {
        "category_sub": "리스트 중 하나",
        "explain_category_sub": "한 줄 이유"
        }
        """
            },
            {
                "role": "user",
                "content": f"""
        [입력]: 
        본문: {self.user_text}
        카테고리(대분류): {self.category_main} 
        카테고리(소분류 후보): {self.category_sub_list}          
        """
            },
            *self._build_hint_messages()
        ]
        return prompt


class TemplateGenerationPromptBuilder:
    def __init__(self, category: str, user_message: str, context: str = ""):
        self.category = category
        self.user_message = user_message
        self.context = context
    
    def build(self) -> str:
        """템플릿 생성 프롬프트 생성"""
        return f"""
카테고리: {self.category}
사용자 요청: {self.user_message}

관련 가이드라인:
{self.context}

위 정보를 바탕으로 알림톡 템플릿을 생성해주세요. 
템플릿에는 변수(예: {{변수명}})를 포함하고, 
변수 목록도 함께 제공해주세요.

템플릿 형식:
- 친근하고 정중한 톤
- 명확한 정보 전달
- 적절한 변수 사용
- 카카오톡 알림톡 가이드라인 준수
"""


class TemplateModificationPromptBuilder:
    def __init__(self, current_template: str, user_message: str, chat_context: str = ""):
        self.current_template = current_template
        self.user_message = user_message
        self.chat_context = chat_context
    
    def build(self) -> str:
        """템플릿 수정 프롬프트 생성"""
        return f"""
현재 알림톡 템플릿:
{self.current_template}

채팅 히스토리:
{self.chat_context}

사용자 요청: {self.user_message}

위 정보를 바탕으로 사용자의 요청에 따라 템플릿을 수정해주세요.
- 기존 템플릿의 구조와 변수는 유지하면서 요청사항을 반영
- 수정된 부분에 대한 간단한 설명 제공
- 변수({{변수명}}) 형태는 그대로 유지

수정된 템플릿:
"""


class ReferenceBasedTemplatePromptBuilder:
    def __init__(self, request, reference_template):
        self.request = request
        self.reference_template = reference_template
    
    def build(self) -> str:
        """참고 템플릿 기반 생성 프롬프트"""
        return f"""
다음은 승인받은 카카오톡 알림톡 템플릿입니다:

=== 참고 템플릿 ===
제목: {self.reference_template['metadata'].get('auto_generated_title', '')}
분류: {self.reference_template['metadata'].get('category_primary', '')} > {self.reference_template['metadata'].get('category_secondary', '')}
템플릿: {self.reference_template['text']}
업종: {self.reference_template['metadata'].get('industry', '')}
목적: {self.reference_template['metadata'].get('purpose', '')}

=== 새 템플릿 요청 정보 ===
카테고리 대분류: {self.request.category_main}
카테고리 소분류: {self.request.category_sub}
메시지 유형: {self.request.type}
채널 링크 여부: {self.request.has_channel_link}
부가 설명 여부: {self.request.has_extra_info}
라벨: {self.request.label}
사용 사례: {self.request.use_case}
의도 유형: {self.request.intent_type}
수신자 범위: {self.request.recipient_scope}
링크 허용: {self.request.links_allowed}
변수: {self.request.variables}
원본 사용자 텍스트: {self.request.user_text}

위 참고 템플릿의 구조와 스타일을 따라하되, 새 요청 정보에 맞게 카카오톡 알림톡 템플릿을 생성해주세요.

중요 규칙:
1. 변수는 #{{변수명}} 형태로 표현
2. 광고성 내용 금지, 정보성/안내성 내용만 포함
3. 발송 근거를 템플릿 하단에 명시 (*표시로 시작)
4. 참고 템플릿과 유사한 톤앤매너 유지
5. 버튼이 필요한 경우 #{{버튼명}} 형태로 표시

템플릿만 생성해주세요:
"""


class PolicyGuidedTemplatePromptBuilder:
    def __init__(self, request, guidelines_text):
        self.request = request
        self.guidelines_text = guidelines_text
    
    def build(self) -> str:
        """정책 가이드라인 기반 생성 프롬프트"""
        return f"""
=== 알림톡 정책 가이드라인 ===
{self.guidelines_text}

=== 템플릿 생성 요청 ===
카테고리: {self.request.category_main} > {self.request.category_sub}
사용 사례: {self.request.use_case}
의도 유형: {self.request.intent_type}
수신자 범위: {self.request.recipient_scope}
원본 메시지: {self.request.user_text}

위 정책 가이드라인을 엄격히 준수하여 카카오톡 알림톡 템플릿을 생성해주세요.

중요 사항:
1. 가이드라인에 명시된 금지사항 절대 포함 금지
2. 허용된 카테고리와 목적에만 부합하는 내용
3. 변수는 #{{변수명}} 형태로 표현
4. 발송 근거를 템플릿 하단에 명시

템플릿만 생성해주세요:
"""


class NewTemplatePromptBuilder:
    def __init__(self, request):
        self.request = request
    
    def build(self) -> str:
        """새 템플릿 생성 프롬프트"""
        return f"""
다음 정보를 바탕으로 카카오톡 알림톡 템플릿을 생성해주세요:

=== 템플릿 요청 정보 ===
라벨: {self.request.label}
카테고리: {self.request.category_main} > {self.request.category_sub}
사용 사례: {self.request.use_case}
의도 유형: {self.request.intent_type}
수신자 범위: {self.request.recipient_scope}
링크 허용: {self.request.links_allowed}
변수: {self.request.variables}
원본 메시지: {self.request.user_text}

카카오톡 알림톡 규정에 맞는 템플릿을 생성해주세요.

중요 규칙:
1. 변수는 #{{변수명}} 형태로 표현
2. 광고성 내용 금지, 정보성/안내성 내용만 포함
3. 발송 근거를 템플릿 하단에 명시 (*표시로 시작)
4. 명확하고 간결한 안내 메시지
5. 버튼이 필요한 경우 #{{버튼명}} 형태로 표시
6. 수신자가 요청했거나 관련 서비스를 이용하는 경우에만 발송되는 내용

템플릿만 생성해주세요:
"""


class TemplateTitlePromptBuilder:
    def __init__(self, request, template_text):
        self.request = request
        self.template_text = template_text
    
    def build(self) -> str:
        """템플릿 제목 생성 프롬프트"""
        return f"""
다음 카카오톡 알림톡 템플릿에 대한 간단한 제목을 생성해주세요:

템플릿: {self.template_text}
카테고리: {self.request.category_main} > {self.request.category_sub}
사용 사례: {self.request.use_case}

제목 규칙:
1. 10자 이내의 간단한 제목
2. 템플릿의 주요 목적을 나타내는 제목
3. "안내", "알림", "발송" 등의 단어 활용

제목만 생성해주세요:
"""
