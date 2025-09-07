import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch
from ai.services.openai_service import OpenAIService
from ai.templateEngine.searcher import Searcher

@pytest.mark.parametrize("fake_intent, fake_scope, fake_links, fake_vars", [
    ("정보성", "구매자", True, ["#{수신자명}", "#{주문 일시}", "#{주문 내역}", "#{취소 내역}"]),
    ("광고성", "이벤트 신청자", False, ["#{이벤트명}", "#{수신자명}", "#{이벤트내용}"]),
    ("인증", "전체회원", False, ["#{인증번호}"]),
])
def test_extract_message_fields_with_mock(fake_intent, fake_scope, fake_links, fake_vars):
    """
    LLM 호출은 Mock 처리.
    extract_message_fields가 chat_completion JSON 응답을
    올바르게 파싱하는지만 검증.
    """

    service = OpenAIService()
    searcher = Searcher(service)

    # 가짜 응답 JSON
    fake_response = {
        "intent_type": fake_intent,
        "recipient_scope": fake_scope,
        "links_allowed": fake_links,
        "variables": fake_vars,
    }

    # service.chat_completion을 Mock 처리
    with patch.object(service, "chat_completion", new=AsyncMock(return_value=json.dumps(fake_response))):
        result = asyncio.run(searcher.extract_message_fields("더미 본문"))

    # 검증
    assert isinstance(result, dict)
    assert result["intent_type"] == fake_intent
    assert result["recipient_scope"] == fake_scope
    assert result["links_allowed"] == fake_links
    assert result["variables"] == fake_vars
