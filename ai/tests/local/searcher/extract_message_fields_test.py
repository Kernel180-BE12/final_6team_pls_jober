import pytest
import asyncio
from ai.services.openai_service import OpenAIService
from ai.templateEngine.searcher import Searcher

@pytest.mark.parametrize("user_text, expected", [
    (
        # 케이스 1: 배달 취소 안내
        r"""
        안녕하세요 #{수신자명}님, 배달이 취소되었습니다.
        ▶ 주문 일시 : #{주문 일시}
        ▶ 주문 내역 : #{주문 내역}
        ▶ 취소 내역 : #{취소 내역}
        다시 주문을 하시려면 아래 "주문하기" 를 눌러주세요.
        """,
        {
            "intent_type": "정보성",
            "recipient_scope": "구매자",
            "links_allowed": True,
            "variables": ["#{수신자명}", "#{주문 일시}", "#{주문 내역}", "#{취소 내역}"]
        }
    ),
    (
        # 케이스 2: 광고 캠페인 승인
        r"""
        #{수신자명}님, 신청하신 광고캠페인이 검토를 마치고 승인되었습니다.
        ▶광고: #{광고} ▶금액: #{금액} 원 ▶진행 기간: #{진행 기간}
        감사합니다.
        """,
        {
            "intent_type": "정보성",
            "recipient_scope": "광고주",
            "links_allowed": False,
            "variables": ["#{수신자명}", "#{광고}", "#{금액}", "#{진행 기간}"]
        }
    )
])
def test_extract_message_fields(user_text, expected):
    service = OpenAIService()
    searcher = Searcher(service)

    result = asyncio.run(searcher.extract_message_fields(user_text))

    # 결과는 dict여야 함
    assert isinstance(result, dict)

    # 필수 키 확인
    for key in ["intent_type", "recipient_scope", "links_allowed", "variables"]:
        assert key in result

    # 값 검증
    assert result["intent_type"] == expected["intent_type"]
    assert result["recipient_scope"] == expected["recipient_scope"]
    assert result["links_allowed"] == expected["links_allowed"]
    assert sorted(result["variables"]) == sorted(expected["variables"])
