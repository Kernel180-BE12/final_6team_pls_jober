import asyncio
import json
import logging
import os
from typing import Optional

from ai.services.openai_service import OpenAIService
from ai.templateEngine.prompts.message_analyzer_prompts import TypePromptBuilder, CategoryPromptBuilder, FieldsPromptBuilder
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class MessageAnalyzer:
    def __init__(self, service: OpenAIService):
        self.service = service

    async def analyze_message(self, user_text: str, category_main: str, category_sub_list: list):
        """
        메시지 유형, 카테고리, 필드 추출 결과를 합쳐서 반환한다.
        """
        logger.info("Starting analyze_message")
        logger.debug(f"[INPUT] user_text={user_text}, category_main={category_main}, category_sub={category_sub_list}")

        try:
            # 📌 변경 부분 메시지 유형, 카테고리를 병렬 처리
            type_result, category_result = await asyncio.gather(
                self.classify_message_type(user_text),
                self.classify_message_category(user_text, category_main, category_sub_list)
            )
            logger.debug(f"[RESULT] type={type_result}, category={category_result}")

            # 메세지 필드 추출
            logger.info("Calling extract_message_fields")
            
            # 메세지 필드 추출 힌트 생성
            fields_hint = [f"""
                [힌트 제공]
                - 메시지 유형: {type_result.get("type")}
                - 카테고리: {category_result.get("category_sub")}

                위 힌트를 참고하여 본문에서 필드를 더 정확하게 추출하라.
            """]
            extract_result = await self.extract_message_fields(user_text, fields_hint)
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

    async def classify_message_type(self, user_text: str, hint: Optional[list[str]] = None):
        """
        메시지 유형을 판단하는 메서드.
        """
        prompt_builder = TypePromptBuilder(user_text)
        self._apply_hints(prompt_builder, hint)
        prompt = prompt_builder.build()
        content = await self.service.chat_completion(prompt, model=os.getenv('OPENAI_MODEL', None))

        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            raise ValueError(f"LLM 응답이 JSON 파싱 불가: {content}")

    async def classify_message_category(self, user_text: str, category_main: str, category_sub_list: list, hint: Optional[list[str]] = None):
        """
        메시지 카테고리를 판단하는 메서드.
        """
        prompt_builder = CategoryPromptBuilder(user_text, category_main, category_sub_list)
        self._apply_hints(prompt_builder, hint)
        prompt = prompt_builder.build()
        content = await self.service.chat_completion(prompt, model=os.getenv('OPENAI_MODEL', None))

        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            raise ValueError(f"LLM 응답이 JSON 파싱 불가: {content}")

    async def extract_message_fields(self, user_text: str, hint: Optional[list[str]] = None):
        """
        메시지에서 필드를 뽑아내는 메서드.
        """
        prompt_builder = FieldsPromptBuilder(user_text)
        self._apply_hints(prompt_builder, hint)
        prompt = prompt_builder.build()
        content = await self.service.chat_completion(prompt, model=os.getenv('OPENAI_MODEL', None))

        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            raise ValueError(f"LLM 응답이 JSON 파싱 불가: {content}")
        
        
    def _apply_hints(self, builder, hint: Optional[list[str]]):
        """hint 문자열 리스트를 받아 builder에 적용"""
        if not hint:
            return
        for h in hint:
            builder.add_hint("hint", h)