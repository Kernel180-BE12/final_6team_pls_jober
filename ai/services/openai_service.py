import os
from typing import List, Dict
from openai import AsyncOpenAI

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def chat_completion(self, messages: List[Dict[str, str]], model: str = "gpt-4o-mini") -> str:
        """
        OpenAI 채팅 완성 API 호출
        """
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_completion_tokens=1000,
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API 호출 실패: {str(e)}")
    
    async def generate_response(self, prompt: str, model: str = "gpt-4o-mini") -> str:
        """
        프롬프트를 받아서 OpenAI 응답을 생성하는 편의 메서드
        """
        messages = [
            {"role": "system", "content": "알림톡 템플릿 검증 전문가입니다."},
            {"role": "user", "content": prompt}
        ]
        return await self.chat_completion(messages, model)
