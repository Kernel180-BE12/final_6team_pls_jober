import asyncio
import json
import logging

from ai.services.openai_service import OpenAIService
from ai.templateEngine.message_analyzer.prompts.build_type_prompt import build_type_prompt
from ai.templateEngine.message_analyzer.prompts.build_category_prompt import build_category_prompt
from ai.templateEngine.message_analyzer.prompts.build_fields_prompt import build_fields_prompt

logger = logging.getLogger(__name__)

class MessageAnalyzer:
    def __init__(self, service: OpenAIService):
        self.service = service

    async def analyze_message(self, user_text: str, category_main: str, category_sub: list):
        """
        메시지 유형, 카테고리, 필드 추출 결과를 합쳐서 반환한다.
        """
        logger.info("Starting analyze_message")
        logger.debug(f"[INPUT] user_text={user_text}, category_main={category_main}, category_sub={category_sub}")

        try:
            # 메세지 유형 판별
            logger.info("Calling classify_message_type")
            type_result = await self.classify_message_type(user_text)
            logger.debug(f"[RESULT] classify_message_type={type_result}")

            # 메세지 카테고리 판별
            logger.info("Calling classify_message_category")
            category_result = await self.classify_message_category(category_main, category_sub)
            logger.debug(f"[RESULT] classify_message_category={category_result}")

            # 메세지 필드 추출
            logger.info("Calling extract_message_fields")
            extract_result = await self.extract_message_fields(user_text)
            logger.debug(f"[RESULT] extract_message_fields={extract_result}")

            # dict 합치기 (중복 키 있으면 extract_result 우선)
            combined = {**type_result, **category_result, **extract_result}

            logger.info("Finished analyze_message")
            logger.debug(f"[COMBINED RESULT] {combined}")

            return combined
        except asyncio.TimeoutError as e:
            logger.error(f"❌ chat_completion timeout: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            logger.exception(e)
            raise

    async def classify_message_type(self, user_text: str):
        """
        메시지 유형을 판단하는 메서드.
        """
        prompt = build_type_prompt(user_text)
        content = await self.service.chat_completion(prompt, model="gpt-3.5-turbo")

        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            raise ValueError(f"LLM 응답이 JSON 파싱 불가: {content}")

    async def classify_message_category(self, category_main: str, category_sub_list: list):
        """
        메시지 카테고리를 판단하는 메서드.
        """
        prompt = build_category_prompt(category_main, category_sub_list)
        content = await self.service.chat_completion(prompt, model="gpt-3.5-turbo")

        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            raise ValueError(f"LLM 응답이 JSON 파싱 불가: {content}")

    async def extract_message_fields(self, user_text: str):
        """
        메시지에서 필드를 뽑아내는 메서드.
        """
        prompt = build_fields_prompt(user_text)
        content = await self.service.chat_completion(prompt, model="gpt-3.5-turbo")

        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            raise ValueError(f"LLM 응답이 JSON 파싱 불가: {content}")
