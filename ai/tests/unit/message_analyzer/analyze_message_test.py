import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch
from ai.services.openai_service import OpenAIService
from ai.templateEngine.message_analyzer.message_analyzer import MessageAnalyzer


def test_analyze_message_with_mock():
    service = OpenAIService()
    messageAnalyzer = MessageAnalyzer(service)

    # classify_message_type 가짜 응답
    fake_type_response = {
        "type": "BASIC",
        "has_channel_link": False,
        "has_extra_info": False,
        "explain_type": "Mock explanation for type"
    }

    # classify_message_category 가짜 응답
    fake_category_response = {
        "category_sub": "주문 완료 안내",
        "explain_category_sub": "Mock explanation for category"
    }

    # extract_message_fields 가짜 응답
    fake_extract_response = {
        "intent_type": "정보성",
        "recipient_scope": "구매자",
        "links_allowed": True,
        "variables": ["#{수신자명}", "#{주문번호}", "#{주문일시}", "#{주문상품}"]
    }

    # 세 메서드 동시에 Mock 처리
    with patch.object(messageAnalyzer, "classify_message_type", new=AsyncMock(return_value=fake_type_response)), \
         patch.object(messageAnalyzer, "classify_message_category", new=AsyncMock(return_value=fake_category_response)), \
         patch.object(messageAnalyzer, "extract_message_fields", new=AsyncMock(return_value=fake_extract_response)):

        result = asyncio.run(
            messageAnalyzer.analyze_message(
                "안녕하세요 #{수신자명}님, 주문이 완료되었습니다.",
                "주문/결제",
                ["주문 완료 안내", "결제 완료 안내", "배송 준비 안내"]
            )
        )

    # 검증: 결과 타입 확인
    assert isinstance(result, dict)

    # type 결과 확인
    assert result["type"] == "BASIC"
    assert result["has_channel_link"] is False
    assert result["has_extra_info"] is False
    assert result["explain_type"] == "Mock explanation for type"

    # category 결과 확인
    assert result["category_sub"] == "주문 완료 안내"
    assert result["explain_category_sub"] == "Mock explanation for category"

    # extract 결과 확인
    assert result["intent_type"] == "정보성"
    assert result["recipient_scope"] == "구매자"
    assert result["links_allowed"] is True
    assert "#{주문번호}" in result["variables"]

