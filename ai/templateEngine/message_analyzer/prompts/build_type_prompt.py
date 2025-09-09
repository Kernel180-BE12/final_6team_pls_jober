from ai.templateEngine.message_analyzer.prompts.base_prompt_builder import BasePromptBuilder

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
