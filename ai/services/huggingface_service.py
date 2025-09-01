from transformers import pipeline, AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import torch
from typing import List, Dict, Any, Optional
import os

class HuggingFaceService:
    def __init__(self):
        """
        Hugging Face 서비스 초기화
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.models = {}
        self.tokenizers = {}
        self.pipelines = {}
    
    async def load_text_generation_model(self, model_name: str = "gpt2"):
        """
        텍스트 생성 모델 로드
        """
        try:
            if model_name not in self.pipelines:
                self.pipelines[model_name] = pipeline(
                    "text-generation",
                    model=model_name,
                    device=self.device
                )
            return {"message": f"{model_name} 모델이 로드되었습니다."}
        except Exception as e:
            raise Exception(f"모델 로드 실패: {str(e)}")
    
    async def generate_text(self, prompt: str, model_name: str = "gpt2", max_length: int = 100):
        """
        텍스트 생성
        """
        try:
            if model_name not in self.pipelines:
                await self.load_text_generation_model(model_name)
            
            result = self.pipelines[model_name](
                prompt,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7
            )
            return {"generated_text": result[0]["generated_text"]}
        except Exception as e:
            raise Exception(f"텍스트 생성 실패: {str(e)}")
    
    async def load_sentiment_analysis_model(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment"):
        """
        감정 분석 모델 로드
        """
        try:
            if model_name not in self.pipelines:
                self.pipelines[model_name] = pipeline(
                    "sentiment-analysis",
                    model=model_name,
                    device=self.device
                )
            return {"message": f"{model_name} 모델이 로드되었습니다."}
        except Exception as e:
            raise Exception(f"모델 로드 실패: {str(e)}")
    
    async def analyze_sentiment(self, text: str, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment"):
        """
        감정 분석
        """
        try:
            if model_name not in self.pipelines:
                await self.load_sentiment_analysis_model(model_name)
            
            result = self.pipelines[model_name](text)
            return {"sentiment": result[0]}
        except Exception as e:
            raise Exception(f"감정 분석 실패: {str(e)}")
    
    async def load_embedding_model(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        임베딩 모델 로드
        """
        try:
            if model_name not in self.models:
                self.models[model_name] = SentenceTransformer(model_name, device=self.device)
            return {"message": f"{model_name} 모델이 로드되었습니다."}
        except Exception as e:
            raise Exception(f"모델 로드 실패: {str(e)}")
    
    async def get_embeddings(self, texts: List[str], model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        텍스트 임베딩 생성
        """
        try:
            if model_name not in self.models:
                await self.load_embedding_model(model_name)
            
            embeddings = self.models[model_name].encode(texts)
            return {"embeddings": embeddings.tolist()}
        except Exception as e:
            raise Exception(f"임베딩 생성 실패: {str(e)}")
    
    async def load_question_answering_model(self, model_name: str = "deepset/roberta-base-squad2"):
        """
        질문-답변 모델 로드
        """
        try:
            if model_name not in self.pipelines:
                self.pipelines[model_name] = pipeline(
                    "question-answering",
                    model=model_name,
                    device=self.device
                )
            return {"message": f"{model_name} 모델이 로드되었습니다."}
        except Exception as e:
            raise Exception(f"모델 로드 실패: {str(e)}")
    
    async def answer_question(self, question: str, context: str, model_name: str = "deepset/roberta-base-squad2"):
        """
        질문-답변
        """
        try:
            if model_name not in self.pipelines:
                await self.load_question_answering_model(model_name)
            
            result = self.pipelines[model_name](
                question=question,
                context=context
            )
            return {
                "answer": result["answer"],
                "score": result["score"],
                "start": result["start"],
                "end": result["end"]
            }
        except Exception as e:
            raise Exception(f"질문-답변 실패: {str(e)}")
    
    async def get_available_models(self):
        """
        사용 가능한 모델 목록 반환
        """
        return {
            "text_generation": ["gpt2", "gpt2-medium", "gpt2-large"],
            "sentiment_analysis": ["cardiffnlp/twitter-roberta-base-sentiment", "distilbert-base-uncased-finetuned-sst-2-english"],
            "embedding": ["sentence-transformers/all-MiniLM-L6-v2", "sentence-transformers/all-mpnet-base-v2"],
            "question_answering": ["deepset/roberta-base-squad2", "distilbert-base-cased-distilled-squad"]
        }
