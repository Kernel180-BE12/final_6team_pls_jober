#!/usr/bin/env python3
"""
통합된 알림톡 템플릿 생성 파이프라인
요구사항에 따른 4단계 순차 처리:
1. 메시지 유형 판단
2. 카테고리 분류  
3. RAG 검색 (Top 3 → 2개 선택)
4. 최종 템플릿 생성
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from services.openai_service import OpenAIService
from services.chromadb_service import ChromaDBService
from templateEngine.message_analyzer import MessageAnalyzer
from templateEngine.template_generator import TemplateGenerator, TemplateRequest, TemplateResponse

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)

@dataclass
class IntegratedGenerationRequest:
    """통합 템플릿 생성 요청"""
    user_text: str
    category_main: str
    category_sub_list: List[str]
    model: Optional[str] = "gpt-4o-mini"

@dataclass
class IntegratedGenerationResult:
    """통합 템플릿 생성 결과"""
    template_text: str
    template_title: str
    variables: List[str]
    generation_method: str
    reference_templates: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

class IntegratedTemplatePipeline:
    """통합된 템플릿 생성 파이프라인"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
        self.chromadb_service = ChromaDBService()
        self.message_analyzer = MessageAnalyzer(self.openai_service)
        self.template_generator = TemplateGenerator()
        
    async def initialize(self):
        """파이프라인 초기화"""
        try:
            await self.chromadb_service.initialize()
            logger.info("✅ 통합 템플릿 생성 파이프라인 초기화 완료")
        except Exception as e:
            logger.error(f"❌ 파이프라인 초기화 실패: {e}")
            raise
    
    async def generate_template(self, request: IntegratedGenerationRequest) -> IntegratedGenerationResult:
        """
        통합된 템플릿 생성 파이프라인 실행
        
        Args:
            request: 생성 요청 정보
            
        Returns:
            IntegratedGenerationResult: 생성 결과
        """
        try:
            logger.info("🚀 통합 템플릿 생성 파이프라인 시작")
            
            # 1단계: 메시지 유형 판단
            logger.info("1️⃣ 메시지 유형 판단 중...")
            type_result = await self._classify_message_type(request.user_text)
            logger.info(f"✅ 메시지 유형: {type_result.get('type')}")
            
            # 2단계: 카테고리 분류
            logger.info("2️⃣ 카테고리 분류 중...")
            category_result = await self._classify_category(
                request.user_text, 
                request.category_main, 
                request.category_sub_list
            )
            logger.info(f"✅ 2차 카테고리: {category_result.get('category_sub')}")
            
            # 3단계: RAG 검색 (Top 3 → 2개 선택)
            logger.info("3️⃣ RAG 검색 중...")
            reference_templates = await self._search_similar_templates(
                request.user_text,
                request.category_main,
                category_result.get('category_sub'),
                top_k=3,
                select_count=2
            )
            logger.info(f"✅ 참고 템플릿 {len(reference_templates)}개 선택")
            
            # 4단계: 최종 템플릿 생성
            logger.info("4️⃣ 최종 템플릿 생성 중...")
            template_result = await self._generate_final_template(
                request, type_result, category_result, reference_templates
            )
            logger.info("✅ 최종 템플릿 생성 완료")
            
            return IntegratedGenerationResult(
                template_text=template_result['template_text'],
                template_title=template_result['template_title'],
                variables=template_result['variables'],
                generation_method=template_result['generation_method'],
                reference_templates=reference_templates,
                metadata={
                    'type_result': type_result,
                    'category_result': category_result,
                    'request': request.__dict__
                },
                success=True
            )
            
        except Exception as e:
            logger.error(f"❌ 템플릿 생성 실패: {e}")
            return IntegratedGenerationResult(
                template_text="",
                template_title="",
                variables=[],
                generation_method="failed",
                reference_templates=[],
                metadata={},
                success=False,
                error_message=str(e)
            )
    
    async def _classify_message_type(self, user_text: str) -> Dict[str, Any]:
        """1단계: 메시지 유형 판단"""
        logger.info("🔍 1단계: 메시지 유형 판단 시작")
        logger.debug(f"[INPUT] user_text 길이: {len(user_text)}")
        
        try:
            result = await self.message_analyzer.classify_message_type(user_text)
            logger.info(f"✅ 메시지 유형 판단 완료: {result.get('type', 'UNKNOWN')}")
            logger.debug(f"[RESULT] {result}")
            return result
        except Exception as e:
            logger.error(f"❌ 메시지 유형 판단 실패: {e}")
            logger.warning("⚠️ 기본값으로 대체")
            # 기본값 반환
            default_result = {
                "has_channel_link": False,
                "has_extra_info": False,
                "type": "BASIC",
                "explain_type": "기본 정보만 포함"
            }
            logger.debug(f"[DEFAULT] {default_result}")
            return default_result
    
    async def _classify_category(self, user_text: str, category_main: str, category_sub_list: List[str]) -> Dict[str, Any]:
        """2단계: 카테고리 분류"""
        logger.info("🏷️ 2단계: 카테고리 분류 시작")
        logger.debug(f"[INPUT] category_main: {category_main}, category_sub_list: {category_sub_list}")
        
        try:
            result = await self.message_analyzer.classify_message_category(
                user_text, category_main, category_sub_list
            )
            logger.info(f"✅ 카테고리 분류 완료: {result.get('category_sub', 'UNKNOWN')}")
            logger.debug(f"[RESULT] {result}")
            return result
        except Exception as e:
            logger.error(f"❌ 카테고리 분류 실패: {e}")
            logger.warning("⚠️ 기본값으로 대체")
            # 기본값 반환
            default_result = {
                "category_sub": category_sub_list[0] if category_sub_list else "기타",
                "explain_category_sub": "기본 카테고리"
            }
            logger.debug(f"[DEFAULT] {default_result}")
            return default_result
    
    async def _search_similar_templates(self, 
                                      user_text: str, 
                                      category_main: str, 
                                      category_sub: str,
                                      top_k: int = 3,
                                      select_count: int = 2) -> List[Dict[str, Any]]:
        """
        3단계: RAG 검색 (Top 3 → 2개 선택)
        
        Args:
            user_text: 사용자 입력 텍스트
            category_main: 1차 카테고리
            category_sub: 2차 카테고리
            top_k: 검색할 상위 개수
            select_count: 최종 선택할 개수
            
        Returns:
            선택된 참고 템플릿 리스트
        """
        try:
            logger.info("🔍 3단계: RAG 검색 시작")
            logger.debug(f"[PARAMS] top_k: {top_k}, select_count: {select_count}")
            
            # template_generator의 search_similar_templates 메서드 사용
            similar_templates, max_similarity = self.template_generator.search_similar_templates(
                user_text, category_main, category_sub, top_k, select_count
            )
            
            logger.info(f"✅ RAG 검색 완료: {len(similar_templates)}개 선택 (최대 유사도: {max_similarity:.3f})")
            logger.debug(f"[SELECTED_TEMPLATES] {[t.get('id', 'unknown') for t in similar_templates]}")
            
            return similar_templates
            
        except Exception as e:
            logger.error(f"❌ RAG 검색 실패: {e}")
            logger.warning("⚠️ 빈 리스트 반환")
            return []
    
    async def _generate_final_template(self, 
                                     request: IntegratedGenerationRequest,
                                     type_result: Dict[str, Any],
                                     category_result: Dict[str, Any],
                                     reference_templates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        4단계: 최종 템플릿 생성
        
        Args:
            request: 생성 요청
            type_result: 메시지 유형 결과
            category_result: 카테고리 분류 결과
            reference_templates: 참고 템플릿 리스트
            
        Returns:
            생성된 템플릿 정보
        """
        try:
            logger.info("📝 4단계: 최종 템플릿 생성 시작")
            logger.debug(f"[INPUT] 참고 템플릿 {len(reference_templates)}개")
            
            # TemplateRequest 객체 생성
            template_request = TemplateRequest(
                category_main=request.category_main,
                category_sub=category_result.get('category_sub', '기타'),
                type=type_result.get('type', 'BASIC'),
                has_channel_link=type_result.get('has_channel_link', False),
                has_extra_info=type_result.get('has_extra_info', False),
                label=category_result.get('category_sub', '기타'),
                use_case=f"{request.category_main} {category_result.get('category_sub', '기타')} 안내",
                intent_type="정보성",
                recipient_scope="전체회원",
                links_allowed=True,
                variables=[],
                section_path=[],
                source="integrated_pipeline",
                source_tag="auto_generated",
                user_text=request.user_text
            )
            
            logger.debug(f"📋 TemplateRequest 생성 완료: {template_request.category_main} > {template_request.category_sub}")
            
            # template_generator의 generate_template 메서드 사용
            template_response = self.template_generator.generate_template(template_request)
            
            result = {
                'template_text': template_response.template_text,
                'template_title': template_response.template_title,
                'variables': template_response.variables_detected,
                'generation_method': template_response.generation_method
            }
            
            logger.info(f"✅ 최종 템플릿 생성 완료: {result['generation_method']}")
            logger.debug(f"[RESULT] 제목: {result['template_title']}, 변수: {len(result['variables'])}개")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 최종 템플릿 생성 실패: {e}")
            raise
