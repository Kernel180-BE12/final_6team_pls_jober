import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch
from ai.services.openai_service import OpenAIService
from ai.templateEngine.searcher import Searcher

@pytest.mark.parametrize("fake_type", ["BASIC", "EXTRA_INFO", "CHANNEL_ADD", "HYBRID"])
def test_classify_category_and_type_with_mock(fake_type):
    """
    LLM 호출은 Mock 처리.
    내 코드가 chat_completion 결과(JSON)를 잘 파싱하는지만 확인.
    """

    service = OpenAIService()
    searcher = Searcher(service)

    # 가짜 응답 생성
    fake_response = {
        "category_sub": "테스트 서브카테고리",
        "type": fake_type,
        "has_channel_link": False,
        "has_extra_info": False,
        "explain_category_sub": "Mocked explanation",
        "explain_type": "Mocked explanation"
    }

    # service.chat_completion 을 Mock으로 대신하기
    with patch.object(service, "chat_completion", new=AsyncMock(return_value=json.dumps(fake_response))):
        result = asyncio.run(
            searcher.classify_category_and_type("더미 본문", "더미 대분류", ["후보1", "후보2"])
        )

    # 5) 검증: JSON 필드 & 타입이 내가 원하는 대로 나오는지
    assert result["type"] == fake_type
    assert result["category_sub"] == "테스트 서브카테고리"
    assert "has_channel_link" in result
    assert "has_extra_info" in result
