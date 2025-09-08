from ai.services.openai_service import OpenAIService
from prompts.message_type_prompt import type_prompt
from prompts.message_category_prompt import category_prompt
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

class Searcher:
    def __init__(self, service: OpenAIService):
        self.service = service
        self.category_prompt = category_prompt
        self.type_prompt = type_prompt
    
    async def analyze_message(self, user_text: str, category_main: str, category_sub: list):
        """
        classify_category_and_type + extract_message_fields 결과를 합쳐서 반환
        """
        
        logger.info("Starting analyze_message")
        logger.debug(f"[INPUT] user_text={user_text}, category_main={category_main}, category_sub={category_sub}")

        try:
            # 두 메서드 동시에 실행
            logging.info("Calling classify_category_and_type")
            classify_task = asyncio.create_task(
                self.classify_category_and_type(user_text, category_main, category_sub)
            )
            logging.info("Calling extract_message_fields")
            extract_task = asyncio.create_task(
                self.extract_message_fields(user_text)
            )

            classify_result, extract_result = await asyncio.gather(classify_task, extract_task)

            logger.debug(f"[RESULT] classify_category_and_type={classify_result}")
            logger.debug(f"[RESULT] extract_message_fields={extract_result}")

            # dict 합치기 (중복 키 있으면 extract_result 우선)
            combined = {**classify_result, **extract_result}

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
        메세지 유형을 판단하는 메서드. \n
        사용자 입력 내용을 받는다. \n
        메세지 유형을 출력한다.
        """
        content = await self.service.chat_completion(self.type_prompt, model="gpt-3.5-turbo")
        
        try:
            return  json.loads(content.strip())
        except json.JSONDecodeError:
            raise ValueError(f"LLM 응답이 JSON 파싱 불가: {content}")

    async def classify_message_category(self, category_main: str, category_sub_list: list):
        """
        메세지 카테고리를 판단하는 메서드 \n
        카테고리 대분류, 카테고리 소분류 리스트를 받는다. \n
        메세지 카테고리를 출력한다.
        """
        content = await self.service.chat_completion(self.category_prompt, model="gpt-3.5-turbo")

        try:
            return  json.loads(content.strip())
        except json.JSONDecodeError:
            raise ValueError(f"LLM 응답이 JSON 파싱 불가: {content}")

    async def extract_message_fields(self, user_text: str):
        messages = [
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

        content = await self.service.chat_completion(messages, model="gpt-3.5-turbo")

        try:
            return  json.loads(content.strip())
        except json.JSONDecodeError:
            raise ValueError(f"LLM 응답이 JSON 파싱 불가: {content}")