import openai
import os
from typing import List, Dict, Any
from openai import OpenAI

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def chat_completion(self, messages: List[Dict[str, str]], model: str = "gpt-4o-mini") -> str:
        """
        OpenAI 채팅 완성 API 호출
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_completion_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API 호출 실패: {str(e)}")
    
    async def embeddings(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """
        OpenAI 임베딩 API 호출
        """
        try:
            response = self.client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"OpenAI 임베딩 API 호출 실패: {str(e)}")
    
