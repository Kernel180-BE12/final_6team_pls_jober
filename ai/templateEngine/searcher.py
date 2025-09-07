import openai
import json

def classify_category_and_type(user_text: str, category_main: str, category_sub: list):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages = [
            {   # 프롬프트, 추후 하드코딩 수정 예정(db에 넣던가 뭐 하던가)
            "role": "system",
            "content": """
                너는 카카오 알림 메시지의 유형과 서브 카테고리를 판정하는 분류기다.

                [서브 카테고리 판정 규칙]
                - 입력된 본문을 읽고, 아래 제공된 서브 카테고리 리스트 중 가장 유사한 하나를 반드시 선택한다.
                - 리스트에 없는 임의의 값을 생성하지 않는다.

                [메세지 유형 정의]
                - BASIC(기본형): 핵심 목적(알림/안내/확인 등)만 전달. 링크가 있을 수 있으나, "채널 추가/채널 방문" 목적이 아니면 기본형으로 본다.
                - EXTRA_INFO(부가 정보형): 핵심 목적 외에 주의사항·정책·문의·절차·상세 가이드 등 **실질적인** 추가 설명이 붙음.
                - CHANNEL_ADD(채널 추가형): 수신자에게 카카오 채널/브랜드 채널/오픈채팅 등을 **추가·구독·방문**하도록 유도하는 맥락이 존재.
                - HYBRID(복합형): 채널 추가형 조건 + 부가 정보형 조건을 **동시에 충족**.

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
                "category_sub": "리스트 중 하나",
                "type": "BASIC | EXTRA_INFO | CHANNEL_ADD | HYBRID",
                "has_channel_link": true/false,
                "has_extra_info": true/false,
                "explain_category_sub": "한 줄 이유",
                "explain_type": "한 줄 이유",
                "confidence": 0.0~1.0
                }
            """
            },
                # === 샷 1: BASIC ===
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
                    "category_sub": "...",
                    "type": "BASIC",
                    "has_channel_link": false,
                    "has_extra_info": false,
                    "explain_category_sub": "기본 정보만 포함",
                    "explain_type": "...",
                    "confidence": 0.9
                    }
                """
            },
                # === 샷 2: EXTRA_INFO ===
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
                    "category_sub": "...",
                    "type": "EXTRA_INFO",
                    "has_channel_link": false,
                    "has_extra_info": true,
                    "explain_category_sub": "부가 정보 포함",
                    "explain_type": "...",
                    "confidence": 0.7
                    }
                """
            },
                # === 샷 3: CHANNEL_ADD ===
            {
                "role": "user",
                "content": """
                    [OO카드]
                    #{고객명} OO#{카드번호4자리}승인 
                    #{승인금액}원 #{할부개월}개월
                    #{거래일자} #{거래시각} 
                    #{가맹점명}

                    채널 추가하고 이 채널의 마케팅 메시지 등을 카카오톡으로 받기
                    #{카카오톡 채널 추가 버튼}
                """
            },
            {
                "role": "assistant",
                "content": """
                    {
                    "category_sub": "...",
                    "type": "CHANNEL_ADD",
                    "has_channel_link": true,
                    "has_extra_info": false,
                    "explain_category_sub": "채널 추가 정보 포함",
                    "explain_type": "...",
                    "confidence": 0.5
                    }
                """
            },
                # === 샷 4: HYBRID ===
            {
                "role": "user",
                "content": """
                    카카오톡 명세서
                    라이언 회원님 결제 명세서 입니다.
                    - 당일 결제 금액: 100원

                    * 개인정보 보호를 위해 메세지 발송완료 부터 100일까지만, 위의 링크를 통한 상세내용 확인이 가능합니다.

                    채널 추가하고 이 채널의 마케팅메세지 등을 카카오톡으로 받기
                """
            },
            {
                "role": "assistant",
                "content": """
                    {
                    "category_sub": "...",
                    "type": "HYBRID",
                    "has_channel_link": true,
                    "has_extra_info": true,
                    "explain_category_sub": "채널 추가 정보, 부가 정보 포함",
                    "explain_type": "...",
                    "confidence": 0.3
                    }
                """
            },
                # === 실제 입력 
            {
            "role": "user",
            "content": f"""
                카테고리(대분류): {category_main}
                본문:
                {user_text}

                카테고리(소분류 후보):
                {category_sub}
            """
            }
        ],

        temperature=0,
        max_tokens=300
    )

    content = response.choices[0].message.content.strip()
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(f"LLM 응답이 JSON 파싱 불가: {content}")

    return result
