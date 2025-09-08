from ai.templateEngine.message_analyzer.prompts.base_prompt_builder import BasePromptBuilder

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