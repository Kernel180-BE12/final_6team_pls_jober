# services/chromadb_service.py

import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    logger.warning("Warning: ChromaDB 패키지가 설치되지 않았습니다. Mock 모드로 실행됩니다.")

# 현재 폴더의 .env 파일 로드
load_dotenv()

class ChromaDBService:
    def __init__(self):
        self.client = None
        self.collections: Dict[str, Any] = {}
        self._connect()

    def _connect(self):
        if not HAS_CHROMADB:
            self.is_mock = True
            logger.warning("ChromaDB가 설치되지 않아 Mock 모드로 실행됩니다.")
            return
        try:
            chroma_host = os.getenv('CHROMA_HOST')
            chroma_port = os.getenv('CHROMA_PORT')
            if chroma_host and chroma_port:
                self.client = chromadb.HttpClient(host=chroma_host, port=int(chroma_port), settings=Settings(anonymized_telemetry=False))
                self.client.heartbeat()
                logger.info(f"✅ ChromaDB HTTP 연결 성공: {chroma_host}:{chroma_port}")
            else:
                persist_dir = os.getenv('CHROMA_PERSIST_DIR', './chroma_db')
                self.client = chromadb.PersistentClient(path=persist_dir)
                logger.info(f"✅ 로컬 ChromaDB 연결 성공: {persist_dir}")

            required_collections = [
                "approved_templates",
                "public_templates",   # 오타 pulblic → public
                "denied_templates",
                "blacklist",
                "rejection_reasons",  # 반려 사유 컬렉션 추가
            ]
            for col in required_collections:
                self.collections[col] = self.client.get_or_create_collection(col)
                logger.info(f"✅ 컬렉션 준비 완료: {col}")
        except Exception as e:
            logger.error(f"❌ ChromaDB 연결 또는 컬렉션 로드 실패: {e}", exc_info=True)
            self.client = None
            self.is_mock = True
        
    async def initialize(self):
        """
        ChromaDB 서비스 초기화 (비동기)
        필요 시 초기 컬렉션 로드나 가이드라인 로드 가능
        """
        if getattr(self, "_initialized", False):
            return
        # 초기화 완료 표시
        self._initialized = True

    def search_templates(self, 
                        collection_name: str, 
                        query_text: str, 
                        top_k: int = 3, 
                        category_sub: str = None,
                        result_format: str = "standard") -> List[Dict]:
        """
        템플릿 검색 공통 함수
        
        Args:
            collection_name: 검색할 컬렉션 이름 ('approved_templates' 또는 'public_templates')
            query_text: 검색 쿼리 텍스트
            top_k: 반환할 결과 개수
            category_sub: 카테고리 필터링 (approved_templates에서만 사용)
            result_format: 결과 형식 ('standard' 또는 'legacy')
        
        Returns:
            List[Dict]: 검색된 템플릿 리스트 (유사도 기준 정렬됨)
        """

        # 컬렉션 선택
        if collection_name == "approved_templates":
            collection = self.collections.get("approved_templates")
            logger.info("  - 검색 대상: 승인된 템플릿")
        elif collection_name == "public_templates":
            collection = self.collections.get("public_templates")
            logger.info("  - 검색 대상: 공용 템플릿")
        elif collection_name == "blacklist":
            collection = self.collections.get("blacklist")
            logger.info("  - 검색 대상: 블랙리스트")
        elif collection_name == "denied_templates":
            collection = self.collections.get("denied_templates")
            logger.info("  - 검색 대상: 반려된 템플릿")
        elif collection_name == "rejection_reasons":
            collection = self.collections.get("rejection_reasons")
            logger.info("  - 검색 대상: 반려 사유")
        else:
            logger.error(f"❌ 알 수 없는 컬렉션: {collection_name}")
            return []
        
        if not collection:
            logger.warning(f"⚠️ '{collection_name}' 컬렉션이 없습니다.")
            return []
        
        try:
            # 카테고리 필터링 조건 (approved_templates에서만 사용)
            where_condition = None
            if collection_name == "approved_templates" and category_sub is not None:
                where_condition = {"category_sub": category_sub}
            
            # 쿼리 실행
            results = collection.query(
                query_texts=[query_text],
                n_results=top_k,
                where=where_condition,
                include=['documents', 'metadatas', 'distances']
            )
            
            templates = []
            
            # 결과 처리
            if results and results['ids'] and results['ids'][0]:
                ids = results['ids'][0]
                documents = results['documents'][0] if results['documents'] else []
                metadatas = results['metadatas'][0] if results['metadatas'] else []
                distances = results['distances'][0] if results['distances'] else []
                
                for i, template_id in enumerate(ids):
                    doc = documents[i] if i < len(documents) else ''
                    meta = metadatas[i] if i < len(metadatas) else {}
                    dist = distances[i] if i < len(distances) else 1.0
                    similarity = 1.0 - float(dist)
                    
                    # 결과 형식에 따른 데이터 구조 결정
                    if result_format == "legacy" and collection_name == "public_templates":
                        # 공용 템플릿 형식 (text, metadata 필드 사용)
                        template_data = {
                            'id': template_id,
                            'text': doc,
                            'metadata': meta,
                            'similarity': similarity
                        }
                    else:
                        # 승인된 템플릿 형식 (content 필드와 메타데이터 병합)
                        template_data = {
                            'id': template_id,
                            'similarity': similarity,
                            'content': doc,
                            **meta
                        }
                    
                    templates.append(template_data)
                
                # 유사도 기준으로 정렬
                templates.sort(key=lambda x: x['similarity'], reverse=True)
            
            return templates
                
        except Exception as e:
            logger.error(f"❌ {collection_name} 검색 중 오류: {e}", exc_info=True)
            return []

