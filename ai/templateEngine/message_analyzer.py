import asyncio
import json
import logging
import os
from typing import Optional

from services.openai_service import OpenAIService
from templateEngine.prompts.message_analyzer_prompts import TypePromptBuilder, CategoryPromptBuilder, FieldsPromptBuilder
from dotenv import load_dotenv

load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)

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
            # 메세지 유형 판별
            logger.info("Calling classify_message_type")
            type_result = await self.classify_message_type(user_text)
            logger.debug(f"[RESULT] classify_message_type={type_result}")

            # 메세지 카테고리 판별
            logger.info("Calling classify_message_category")
            category_result = await self.classify_message_category(user_text, category_main, category_sub_list)
            logger.debug(f"[RESULT] classify_message_category={category_result}")

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
        logger.info("🔍 메시지 유형 분류 시작")
        logger.debug(f"[INPUT] user_text 길이: {len(user_text)}, hint: {hint}")
        
        try:
            prompt_builder = TypePromptBuilder(user_text)
            self._apply_hints(prompt_builder, hint)
            prompt = prompt_builder.build()
            
            logger.debug("📝 프롬프트 생성 완료, OpenAI API 호출 중...")
            content = await self.service.chat_completion(prompt, model=os.getenv('OPENAI_MODEL', None))
            logger.debug(f"[API_RESPONSE] 응답 길이: {len(content)}")

            result = json.loads(content.strip())
            logger.info(f"✅ 메시지 유형 분류 완료: {result.get('type', 'UNKNOWN')}")
            logger.debug(f"[RESULT] {result}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON 파싱 실패: {e}")
            logger.error(f"[RAW_RESPONSE] {content}")
            raise ValueError(f"LLM 응답이 JSON 파싱 불가: {content}")
        except Exception as e:
            logger.error(f"❌ 메시지 유형 분류 실패: {e}")
            raise

    async def classify_message_category(self, user_text: str, category_main: str, category_sub_list: list, hint: Optional[list[str]] = None):
        """
        메시지 카테고리를 판단하는 메서드.
        """
        logger.info("🏷️ 메시지 카테고리 분류 시작")
        logger.debug(f"[INPUT] category_main: {category_main}, category_sub_list: {category_sub_list}")
        
        try:
            prompt_builder = CategoryPromptBuilder(user_text, category_main, category_sub_list)
            self._apply_hints(prompt_builder, hint)
            prompt = prompt_builder.build()
            
            logger.debug("📝 카테고리 분류 프롬프트 생성 완료, OpenAI API 호출 중...")
            content = await self.service.chat_completion(prompt, model=os.getenv('OPENAI_MODEL', None))
            logger.debug(f"[API_RESPONSE] 응답 길이: {len(content)}")

            result = json.loads(content.strip())
            logger.info(f"✅ 카테고리 분류 완료: {result.get('category_sub', 'UNKNOWN')}")
            logger.debug(f"[RESULT] {result}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON 파싱 실패: {e}")
            logger.error(f"[RAW_RESPONSE] {content}")
            raise ValueError(f"LLM 응답이 JSON 파싱 불가: {content}")
        except Exception as e:
            logger.error(f"❌ 카테고리 분류 실패: {e}")
            raise

    async def extract_message_fields(self, user_text: str, hint: Optional[list[str]] = None):
        """
        메시지에서 필드를 뽑아내는 메서드.
        """
        logger.info("🔍 메시지 필드 추출 시작")
        logger.debug(f"[INPUT] user_text 길이: {len(user_text)}, hint: {hint}")
        
        try:
            prompt_builder = FieldsPromptBuilder(user_text)
            self._apply_hints(prompt_builder, hint)
            prompt = prompt_builder.build()
            
            logger.debug("📝 필드 추출 프롬프트 생성 완료, OpenAI API 호출 중...")
            content = await self.service.chat_completion(prompt, model=os.getenv('OPENAI_MODEL', None))
            logger.debug(f"[API_RESPONSE] 응답 길이: {len(content)}")

            result = json.loads(content.strip())
            logger.info(f"✅ 필드 추출 완료: {len(result.get('fields', []))}개 필드 발견")
            logger.debug(f"[RESULT] {result}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON 파싱 실패: {e}")
            logger.error(f"[RAW_RESPONSE] {content}")
            raise ValueError(f"LLM 응답이 JSON 파싱 불가: {content}")
        except Exception as e:
            logger.error(f"❌ 필드 추출 실패: {e}")
            raise
        
        
    def _apply_hints(self, builder, hint: Optional[list[str]]):
        """hint 문자열 리스트를 받아 builder에 적용"""
        if not hint:
            logger.debug("💡 힌트 없음")
            return
        logger.debug(f"💡 {len(hint)}개 힌트 적용 중...")
        for i, h in enumerate(hint):
            builder.add_hint("hint", h)
            logger.debug(f"💡 힌트 {i+1} 적용 완료")