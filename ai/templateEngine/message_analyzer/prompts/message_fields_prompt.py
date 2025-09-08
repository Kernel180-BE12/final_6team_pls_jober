fields_prompt = [
    {
        "role": "system",
        "content": r"""
            너는 카카오 알림 메시지에서 구조화된 값을 추출하는 추출기다.
            아래 본문을 읽고 지정된 스키마에 맞춰 JSON만 출력하도록

            [스키마 설명]
            - intent_type: 의도 유형 (정보성, 인증, 광고성 등)
            - recipient_scope: 수신자 범위 (신규가입자, 전체회원 등)
            - links_allowed: 본문에서 링크 허용 여부 (true/false)
            - variables: 본문 내 변수 placeholder 배열
                - `#{NAME}`, `#{SHOPNAME}`처럼 `#{...}` 형식 그대로 추출
                - 메시지 안에서 변수 역할을 하는 자연어 표현(예: "이름", "단체명")도 포함

            [규칙]
            1. 반드시 JSON만 출력하라.
            2. 값이 명확하지 않으면 null을 넣어라.
            3. Boolean은 true/false로만.
            4. 배열이 없으면 []로.
            5. 본문에 나오는 "#{}" 형식은 반드시 문자열로 추출할 것.

            [출력 형식(JSON)]
            {
            "intent_type": "string|null",
            "recipient_scope": "string|null",
            "links_allowed": true/false,
            "variables": ["..."] or []
            }
        """
    },
    {
        "role": "user",
        "content": r"""
            안녕하세요 #{수신자명}님, 배달이 취소되었습니다. 
            취소된 내역을 확인하시고 본인이 주문하시지 않은 경우 연락 부탁드립니다. 
            ▶ 주문 일시 : #{주문 일시} 
            ▶ 주문 내역 : #{주문 내역} 
            ▶ 취소 내역 : #{취소 내역} 
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
            [#{이벤트명} 관련 정보 안내]  
            # 안녕하세요, #{수신자명} 고객님   
            # #{이벤트명}에 대한 상세 내용을 아래와 같이 안내드립니다.  
            # ▶ 내용: #{이벤트내용}   
            # ▶ 기간: #{참여기간}   
            # ▶ 유의사항: #{유의사항}  
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
            "variables": ["#{이벤트명}", "#{수신자명}", "#{이벤트내용}", "#{참여기간}", "#{유의사항}"]
            }
        """
    },
    {
        "role": "user",
        "content": f"본문: {user_text}"
    }
]