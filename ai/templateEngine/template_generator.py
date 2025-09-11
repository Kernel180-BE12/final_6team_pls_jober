#!/usr/bin/env python3
"""
카카오톡 템플릿 자동 생성 API
유사도 검색을 통해 기존 승인 템플릿 참고 또는 새로운 템플릿 생성
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)
from templateEngine.prompts.message_analyzer_prompts import (
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
        
        logger.info("🔗 ChromaDB 연결 시도 중...")
        logger.debug(f"[CONFIG] host: {chroma_host}, port: {chroma_port}, persist_dir: {chroma_persist_dir}")
        
        try:
            # HTTP 클라이언트로 연결 시도
            logger.debug("🌐 HTTP 클라이언트로 연결 시도...")
            self.client = chromadb.HttpClient(
                host=chroma_host,
                port=chroma_port
            )
            self.client.heartbeat()
            logger.info(f"✅ ChromaDB HTTP 연결 성공: {chroma_host}:{chroma_port}")
        except Exception as e:
            logger.warning(f"⚠️ HTTP 연결 실패: {e}")
            try:
                # 로컬 PersistentClient로 연결 시도
                logger.debug("💾 로컬 PersistentClient로 연결 시도...")
                self.client = chromadb.PersistentClient(
                    path=chroma_persist_dir,
                    settings=Settings(anonymized_telemetry=False)
                )
                logger.info(f"✅ 로컬 ChromaDB 연결 성공: {chroma_persist_dir}")
            except Exception as e2:
                logger.error(f"❌ ChromaDB 연결 완전 실패: {e2}")
                raise Exception("ChromaDB 연결에 실패했습니다.")
    
    def search_similar_templates(self, query_text: str, category_main: str, category_sub: str, top_k: int = 3, select_count: int = 2) -> Tuple[List[Dict], float]:
        """
        승인된 템플릿에서 유사도 검색 (요구사항에 맞게 수정)
        - 1차·2차 카테고리 메타데이터로 필터링
        - Top 3 검색 후 2개 선택
        """
        logger.info("🔍 유사 템플릿 검색 시작")
        logger.debug(f"[INPUT] query_text 길이: {len(query_text)}, category: {category_main} > {category_sub}")
        logger.debug(f"[PARAMS] top_k: {top_k}, select_count: {select_count}")
        
        try:
            # approved 컬렉션 가져오기
            logger.debug("📚 'approved' 컬렉션 가져오는 중...")
            collection = self.client.get_collection('approved')
            
            # 카테고리 필터링을 위한 where 조건 구성
            where_filter = {}
            if category_main:
                where_filter['category_main'] = category_main
            if category_sub:
                where_filter['category_sub'] = category_sub
            
            logger.debug(f"🔍 필터 조건: {where_filter}")
            
            # 유사도 검색 수행 (상위 3개)
            logger.debug(f"🔍 ChromaDB에서 {top_k}개 검색 중...")
            results = collection.query(
                query_texts=[query_text],
                n_results=top_k,
                where=where_filter if where_filter else None,
                include=['documents', 'metadatas', 'distances']
            )
            
            similar_templates = []
            max_similarity = 0.0
            
            if results and results['documents'] and results['documents'][0]:
                logger.info(f"📊 검색 결과: {len(results['documents'][0])}개 템플릿 발견")
                
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0], 
                    results['distances'][0]
                )):
                    # 거리를 유사도로 변환 (거리가 작을수록 유사도 높음)
                    similarity = 1.0 - distance
                    max_similarity = max(max_similarity, similarity)
                    
                    template_info = {
                        'id': results['ids'][0][i],
                        'text': doc,
                        'metadata': metadata,
                        'similarity': similarity,
                        'rank': i + 1
                    }
                    similar_templates.append(template_info)
                    logger.debug(f"📄 템플릿 {i+1}: 유사도 {similarity:.3f}, ID: {results['ids'][0][i]}")
            else:
                logger.warning("⚠️ 검색 결과가 없습니다")
            
            # 유사도 순으로 정렬
            similar_templates.sort(key=lambda x: x['similarity'], reverse=True)
            
            # 요구사항: Top 3 중 2개 선택
            selected_templates = similar_templates[:select_count]
            
            logger.info(f"✅ RAG 검색 완료: {len(similar_templates)}개 중 {len(selected_templates)}개 선택 (최대 유사도: {max_similarity:.3f})")
            
            return selected_templates, max_similarity
            
        except Exception as e:
            logger.error(f"❌ 유사도 검색 오류: {e}")
            return [], 0.0
    
    def generate_template_with_reference(self, request: TemplateRequest, reference_templates: List[Dict]) -> str:
        """참고 템플릿 2개를 기반으로 새 템플릿 생성 (요구사항에 맞게 수정)"""
        logger.info("📝 참고 템플릿 기반 생성 시작")
        logger.debug(f"[INPUT] 참고 템플릿 {len(reference_templates)}개, 카테고리: {request.category_main} > {request.category_sub}")
        
        try:
            # 참고 템플릿들을 컨텍스트로 구성
            reference_context = "\n\n".join([
                f"참고 템플릿 {i+1}:\n{template['text']}"
                for i, template in enumerate(reference_templates)
            ])
            logger.debug(f"📚 참고 컨텍스트 구성 완료: {len(reference_context)}자")
            
            prompt = f"""
다음은 승인받은 카카오톡 알림톡 템플릿들입니다:

=== 참고 템플릿들 ===
{reference_context}

=== 새 템플릿 생성 요청 ===
사용자 입력: {request.user_text}
1차 카테고리: {request.category_main}
2차 카테고리: {request.category_sub}
메시지 유형: {request.type}
채널 링크 여부: {request.has_channel_link}
부가 정보 여부: {request.has_extra_info}
라벨: {request.label}
사용 사례: {request.use_case}
의도 유형: {request.intent_type}
수신자 범위: {request.recipient_scope}

위 참고 템플릿들의 구조와 스타일을 참고하여, 사용자 입력에 맞는 새로운 카카오톡 알림톡 템플릿을 생성해주세요.

중요 규칙:
1. 변수는 #{{변수명}} 형태로 표현
2. 광고성 내용 금지, 정보성/안내성 내용만 포함
3. 발송 근거를 템플릿 하단에 명시 (*표시로 시작)
4. 참고 템플릿과 유사한 톤앤매너 유지
5. 카카오톡 알림톡 규정 준수
6. **절대 변수 목록이나 변수 설명을 템플릿 내용에 포함하지 마세요**
7. **템플릿은 실제 발송될 메시지 내용만 포함해야 합니다**

템플릿만 생성해주세요:
"""
            
            logger.debug("🤖 OpenAI API 호출 중... (참고 기반 생성)")
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 카카오톡 알림톡 템플릿 생성 전문가입니다. 승인받은 템플릿을 참고하여 규정에 맞는 새로운 템플릿을 생성합니다. 절대 변수 목록이나 변수 설명을 템플릿 내용에 포함하지 마세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content.strip()
            logger.info(f"✅ 참고 템플릿 기반 생성 완료: {len(result)}자")
            logger.debug(f"[RESULT] {result[:100]}...")
            return result
            
        except Exception as e:
            logger.error(f"❌ 참고 템플릿 기반 생성 오류: {e}")
            logger.info("🔄 기본 생성 방식으로 전환...")
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
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 카카오톡 알림톡 정책 전문가입니다. 정책 가이드라인을 완벽히 준수하는 템플릿만 생성합니다. 절대 변수 목록이나 변수 설명을 템플릿 내용에 포함하지 마세요."},
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
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 카카오톡 알림톡 템플릿 생성 전문가입니다. 알림톡 규정을 준수하는 정보성/안내성 템플릿을 생성합니다. 절대 변수 목록이나 변수 설명을 템플릿 내용에 포함하지 마세요."},
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
        """
        메인 템플릿 생성 함수 (요구사항에 맞는 4단계 흐름)
        1. 메시지 유형 판단 (이미 request에 포함됨)
        2. 카테고리 분류 (이미 request에 포함됨)
        3. RAG 검색 (Top 3 → 2개 선택)
        4. 최종 템플릿 생성
        """
        try:
            print("🚀 템플릿 생성 파이프라인 시작")
            
            # 1단계: 메시지 유형 판단 (이미 request에 포함됨)
            print(f"1️⃣ 메시지 유형: {request.type}")
            
            # 2단계: 카테고리 분류 (이미 request에 포함됨)
            print(f"2️⃣ 카테고리: {request.category_main} > {request.category_sub}")
            
            # 3단계: RAG 검색 (Top 3 → 2개 선택)
            print("3️⃣ RAG 검색 중...")
            similar_templates, max_similarity = self.search_similar_templates(
                request.user_text,
                request.category_main,
                request.category_sub,
                top_k=3,
                select_count=2
            )
            print(f"✅ 참고 템플릿 {len(similar_templates)}개 선택")
            
            # 4단계: 최종 템플릿 생성
            print("4️⃣ 최종 템플릿 생성 중...")
            reference_template_ids = []
            generation_method = "new_creation"
            
            if similar_templates:
                # 참고 템플릿 2개를 활용한 생성
                template_text = self.generate_template_with_reference(request, similar_templates)
                reference_template_ids = [template['id'] for template in similar_templates]
                generation_method = "reference_based"
            else:
                # 참고 템플릿이 없으면 정책 가이드라인 기반 생성
                guidelines = self.search_policy_guidelines(request)
                if guidelines:
                    template_text = self.generate_template_with_policy_guidelines(request, guidelines)
                    generation_method = "policy_guided"
                else:
                    # 가이드라인도 없으면 기본 생성
                    template_text = self.generate_new_template(request)
                    generation_method = "new_creation"
            
            # 템플릿 제목 생성
            template_title = self.generate_title(request, template_text)
            
            # 변수 추출
            variables_detected = self.extract_variables(template_text)
            
            print("✅ 최종 템플릿 생성 완료")
            
            # 응답 생성
            return TemplateResponse(
                template_text=template_text,
                template_title=template_title,
                generation_method=generation_method,
                reference_template_id=reference_template_ids[0] if reference_template_ids else None,
                metadata={
                    "request_info": request.dict(),
                    "reference_templates": similar_templates,
                    "generation_flow": "4단계 파이프라인 완료",
                    "variables_detected": variables_detected  # 메타데이터에 포함
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
