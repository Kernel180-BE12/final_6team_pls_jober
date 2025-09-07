import pytest
import asyncio
from ai.templateEngine.searcher import Searcher
from ai.services.openai_service import OpenAIService

@pytest.mark.parametrize("user_text, category_main, category_sub, expected_type", [
    (
        "주문이 정상적으로 접수되었습니다. - 주문일자: 2025.09.08 - 금액: 50,000원",
        "주문/결제",
        ["주문 완료 안내", "결제 완료 안내", "배송 준비 안내"],
        "BASIC"
    ),
    (
        "예약이 완료되었습니다. 차량 이용 시 반드시 주차 여부를 문의 바랍니다.",
        "예약",
        ["예약 안내", "취소 안내", "변경 안내"],
        "EXTRA_INFO"
    ),
    (
        "카드 승인 완료. 채널 추가하고 혜택을 받아보세요.",
        "결제",
        ["결제 승인 안내", "혜택 안내"],
        "CHANNEL_ADD"
    ),
    (
        "결제 명세서 확인 가능합니다. (100일 이후 확인 불가) 채널 추가하고 혜택 받기",
        "결제",
        ["결제 안내", "결제 명세서 안내"],
        "HYBRID"
    ),
])
def test_classify_category_and_type(user_text, category_main, category_sub, expected_type):
    service = OpenAIService()
    searcher = Searcher(service)

    result = asyncio.run(searcher.classify_category_and_type(user_text, category_main, category_sub))

    # 최소한 결과 JSON 필드 검증
    assert "category_sub" in result
    assert "type" in result
    assert result["type"] in ["BASIC", "EXTRA_INFO", "CHANNEL_ADD", "HYBRID"]
    assert result["type"] == expected_type
