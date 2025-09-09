#!/usr/bin/env python3
"""
카카오톡 템플릿 자동 생성 API
유사도 검색을 통해 기존 승인 템플릿 참고 또는 새로운 템플릿 생성
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ai.templateEngine.prompts.message_analyzer_prompts import (
    ReferenceBasedTemplatePromptBuilder,
    PolicyGuidedTemplatePromptBuilder,
    NewTemplatePromptBuilder,
    TemplateTitlePromptBuilder
)

# 환경 변수 로드
load_dotenv()

# OpenAI API 설정
openai.api_key = os.getenv('OPENAI_API_KEY')

class TemplateRequest(BaseModel):
    """템플릿 생성 요청 모델"""
    category_main: str                    # 카테고리 대분류
    category_sub: str                     # 카테고리 소분류
    type: str                            # 메시지 유형: "BASIC" | "EXTRA_INFO" | "CHANNEL_ADD" | "HYBRID"
    has_channel_link: bool               # 채널 링크 여부
    has_extra_info: bool                 # 부가 설명 여부
    label: Optional[str] = None          # 라벨
    use_case: Optional[str] = None
    intent_type: Optional[str] = None
    recipient_scope: Optional[str] = None
    links_allowed: bool = True
    variables: List[str] = []
    section_path: List[str] = []
    source: Optional[str] = None
    source_tag: Optional[str] = None
    user_text: str                       # 원본 사용자 메시지 (유사도 검색용)

class TemplateResponse(BaseModel):
    """템플릿 생성 응답 모델"""
    template_text: str
    template_title: str
    variables_detected: List[str]
    generation_method: str  # "reference_based", "new_creation"
    reference_template_id: Optional[str] = None
    metadata: Dict[str, Any]

class TemplateGenerator:
    def __init__(self):
        self.client = None
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.connect_to_chroma()
    
    def connect_to_chroma(self):
        """ChromaDB 연결"""
        chroma_host = os.getenv('CHROMA_HOST', 'localhost')
        chroma_port = int(os.getenv('CHROMA_PORT', '8000'))
        chroma_persist_dir = os.getenv('CHROMA_PERSIST_DIR', './chroma_db')
        
        try:
            # HTTP 클라이언트로 연결 시도
            self.client = chromadb.HttpClient(
                host=chroma_host,
                port=chroma_port
            )
            self.client.heartbeat()
            print(f"ChromaDB 연결 성공: {chroma_host}:{chroma_port}")
        except Exception as e:
            print(f"HTTP 연결 실패: {e}")
            try:
                # 로컬 PersistentClient로 연결 시도
                self.client = chromadb.PersistentClient(
                    path=chroma_persist_dir,
                    settings=Settings(anonymized_telemetry=False)
                )
                print(f"로컬 ChromaDB 연결 성공: {chroma_persist_dir}")
            except Exception as e2:
                print(f"ChromaDB 연결 완전 실패: {e2}")
                raise Exception("ChromaDB 연결에 실패했습니다.")
    
    def search_similar_templates(self, query_text: str, similarity_threshold: float = 0.7) -> Tuple[List[Dict], float]:
        """승인된 템플릿에서 유사도 검색"""
        try:
            # approved 컬렉션 가져오기 (기존 임베딩 함수 사용)
            collection = self.client.get_collection('approved')
            
            # 유사도 검색 수행 (상위 3개)
            results = collection.query(
                query_texts=[query_text],
                n_results=3,
                include=['documents', 'metadatas', 'distances']
            )
            
            similar_templates = []
            max_similarity = 0.0
            
            if results and results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0], 
                    results['distances'][0]
                )):
                    # 거리를 유사도로 변환 (거리가 작을수록 유사도 높음)
                    similarity = 1.0 - distance
                    max_similarity = max(max_similarity, similarity)
                    
                    if similarity >= similarity_threshold:
                        template_info = {
                            'id': results['ids'][0][i],
                            'text': doc,
                            'metadata': metadata,
                            'similarity': similarity,
                            'rank': i + 1
                        }
                        similar_templates.append(template_info)
            
            return similar_templates, max_similarity
            
        except Exception as e:
            print(f"유사도 검색 오류: {e}")
            return [], 0.0
    
    def generate_template_with_reference(self, request: TemplateRequest, reference_template: Dict) -> str:
        """참고 템플릿을 기반으로 새 템플릿 생성"""
        try:
            # 프롬프트 빌더 사용
            prompt_builder = ReferenceBasedTemplatePromptBuilder(request, reference_template)
            prompt = prompt_builder.build()
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "당신은 카카오톡 알림톡 템플릿 생성 전문가입니다. 승인받은 템플릿을 참고하여 규정에 맞는 새로운 템플릿을 생성합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"참고 템플릿 기반 생성 오류: {e}")
            return self.generate_new_template(request)
    
    def search_policy_guidelines(self, request: TemplateRequest) -> List[Dict]:
        """정책 가이드라인 검색"""
        try:
            guideline_collection = self.client.get_collection('policy_guidelines')
            
            # 카테고리와 사용사례로 관련 정책 검색
            search_query = f"{request.category_main} {request.category_sub} {request.use_case}"
            
            results = guideline_collection.query(
                query_texts=[search_query],
                n_results=2,  # 정책은 너무 많으면 혼란
                include=['documents', 'metadatas']
            )
            
            guidelines = []
            if results and results['documents'] and results['documents'][0]:
                for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                    guidelines.append({
                        'text': doc,
                        'metadata': metadata
                    })
            
            return guidelines
            
        except Exception as e:
            print(f"정책 가이드라인 검색 오류: {e}")
            return []

    def generate_template_with_policy_guidelines(self, request: TemplateRequest, guidelines: List[Dict]) -> str:
        """정책 가이드라인을 참고하여 템플릿 생성"""
        try:
            guidelines_text = "\n".join([g['text'] for g in guidelines])
            
            # 프롬프트 빌더 사용
            prompt_builder = PolicyGuidedTemplatePromptBuilder(request, guidelines_text)
            prompt = prompt_builder.build()
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "당신은 카카오톡 알림톡 정책 전문가입니다. 정책 가이드라인을 완벽히 준수하는 템플릿만 생성합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # 정책 준수를 위해 더 낮은 온도
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"정책 기반 템플릿 생성 오류: {e}")
            return self.generate_new_template(request)

    def generate_new_template(self, request: TemplateRequest) -> str:
        """완전히 새로운 템플릿 생성"""
        try:
            # 프롬프트 빌더 사용
            prompt_builder = NewTemplatePromptBuilder(request)
            prompt = prompt_builder.build()
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "당신은 카카오톡 알림톡 템플릿 생성 전문가입니다. 알림톡 규정을 준수하는 정보성/안내성 템플릿을 생성합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"새 템플릿 생성 오류: {e}")
            return "템플릿 생성 중 오류가 발생했습니다."
    
    def extract_variables(self, template_text: str) -> List[str]:
        """템플릿에서 변수 추출"""
        import re
        variables = re.findall(r'#\{([^}]+)\}', template_text)
        return list(set(variables))  # 중복 제거
    
    def generate_title(self, request: TemplateRequest, template_text: str) -> str:
        """템플릿 제목 생성"""
        try:
            # 프롬프트 빌더 사용
            prompt_builder = TemplateTitlePromptBuilder(request, template_text)
            prompt = prompt_builder.build()
            
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "간단하고 명확한 템플릿 제목을 생성합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"제목 생성 오류: {e}")
            return request.label or "템플릿 안내"
    
    
    def generate_template(self, request: TemplateRequest) -> TemplateResponse:
        """메인 템플릿 생성 함수"""
        try:
            # 1. 유사도 검색
            similar_templates, max_similarity = self.search_similar_templates(
                request.user_text, 
                similarity_threshold=0.7
            )
            
            reference_template_id = None
            generation_method = "new_creation"
            
            # 2. 템플릿 생성 로직 개선
            if similar_templates and max_similarity >= 0.7:
                # 유사도 높음: 참고 템플릿 기반 생성
                reference_template = similar_templates[0]
                template_text = self.generate_template_with_reference(request, reference_template)
                reference_template_id = reference_template['id']
                generation_method = "reference_based"
            else:
                # 유사도 낮음: 정책 가이드라인 기반 생성
                guidelines = self.search_policy_guidelines(request)
                if guidelines:
                    template_text = self.generate_template_with_policy_guidelines(request, guidelines)
                    generation_method = "policy_guided"
                else:
                    # 가이드라인도 없으면 기본 생성
                    template_text = self.generate_new_template(request)
                    generation_method = "new_creation"
            
            # 3. 템플릿 제목 생성
            template_title = self.generate_title(request, template_text)
            
            # 4. 변수 추출
            variables_detected = self.extract_variables(template_text)
            
            # 5. 응답 생성
            return TemplateResponse(
                template_text=template_text,
                template_title=template_title,
                variables_detected=variables_detected,
                generation_method=generation_method,
                reference_template_id=reference_template_id,
                metadata={
                    "request_info": request.dict()
                }
            )
            
        except Exception as e:
            print(f"템플릿 생성 오류: {e}")
            raise HTTPException(status_code=500, detail=f"템플릿 생성 실패: {str(e)}")

# FastAPI 앱 생성
app = FastAPI(title="카카오톡 템플릿 생성 API", version="1.0.0")
generator = TemplateGenerator()

@app.post("/generate-template", response_model=TemplateResponse)
async def generate_template_endpoint(request: TemplateRequest):
    """템플릿 생성 API 엔드포인트"""
    return generator.generate_template(request)

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "message": "Template Generator API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
