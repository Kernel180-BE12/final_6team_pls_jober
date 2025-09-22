# services/chromadb_service.py

import chromadb
from chromadb.config import Settings
import os
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

try:
    import chromadb
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    logger.warning("Warning: ChromaDB 패키지가 설치되지 않았습니다. Mock 모드로 실행됩니다.")

from typing import List, Dict, Any, Optional
import os

from dotenv import load_dotenv

# 현재 폴더의 .env 파일 로드
load_dotenv()

class ChromaDBService:
    def __init__(self):
        self.client = None
        self.approved_collection = None
        self.pulblic_templates = None
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

            self.approved_collection = self.client.get_or_create_collection("approved_templates")
            self.pulblic_templates = self.client.get_or_create_collection("pulblic_templates")
            logger.info("✅ 컬렉션('approved_templates', 'pulblic_templates') 로드 완료")
            self.is_mock = False
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
        # 예: 블랙리스트/화이트리스트 컬렉션 미리 로드
        self._get_or_create_collection("blacklist")
        self._get_or_create_collection("whitelist")
        self._initialized = True

    async def load_initial_guidelines(self):
        """초기 가이드라인 데이터 로드 (필요 시 확장). 현재는 no-op."""
        try:
            return
        except Exception:
            return

    def _get_or_create_collection(self, collection_name: str):
        """
        컬렉션 가져오기 또는 생성
        """
        if not HAS_CHROMADB or self.client is None:
            return None

        try:
            return self.client.get_or_create_collection(name=collection_name)
        except Exception:
            return None

    def search_public_templates(self, query_text: str, top_k: int = 3) -> Dict[str, Any]:
        logger.info("  - 검색 대상: 공용 템플릿")
        if not self.pulblic_templates:
            logger.warning("⚠️ 'pulblic_templates' 컬렉션이 없습니다.")
            return {"templates": [], "max_similarity": 0.0}
        try:
            results = self.pulblic_templates.query(
                query_texts=[query_text], n_results=top_k, include=['documents', 'metadatas', 'distances']
            )
            templates = []
            max_similarity = 0.0

            # 👇 --- 여기가 핵심 수정 사항 --- 👇
            # ChromaDB의 query 결과는 항상 2차원 리스트이므로, 첫 번째 요소([0])에 접근해야 합니다.
            if results and results['ids'] and results['ids'][0]:
                ids = results['ids'][0]
                documents = results['documents'][0]
                metadatas = results['metadatas'][0]
                distances = results['distances'][0]

                for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
                    similarity = 1.0 - float(dist)
                    templates.append({'id': ids[i], 'text': doc, 'metadata': meta, 'similarity': similarity})
                    max_similarity = max(max_similarity, similarity)

                templates.sort(key=lambda x: x['similarity'], reverse=True)
            return {"templates": templates, "max_similarity": max_similarity}
        except Exception as e:
            logger.error(f"❌ 공용 템플릿 검색 중 오류: {e}", exc_info=True)
            return {"templates": [], "max_similarity": 0.0}

    def search_approved_templates(self, query_text: str, category_sub: str = None, top_k: int = 3) -> Dict[str, Any]:
        """
        승인된 템플릿 검색 (카테고리 제한 옵션)
        """
        try:
            # 카테고리 필터링 조건
            where_condition = None if category_sub is None else {"category_sub": category_sub}

            results = self.approved_collection.query(
                query_texts=[query_text],
                n_results=top_k,
                where=where_condition  # None이면 전체 검색, 값이 있으면 해당 카테고리만
            )

            templates = []
            max_similarity = 0.0

            if results['ids'] and results['ids'][0]:
                for i, template_id in enumerate(results['ids'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    similarity = 1 - results['distances'][0][i]  # 거리를 유사도로 변환

                    template_data = {
                        'id': template_id,
                        'similarity': similarity,
                        'content': results['documents'][0][i] if results['documents'] else '',
                        **metadata
                    }
                    templates.append(template_data)
                    max_similarity = max(max_similarity, similarity)

            return {"templates": templates, "max_similarity": max_similarity}

        except Exception as e:
            logger.error(f"템플릿 검색 중 오류: {e}")
            return {"templates": [], "max_similarity": 0.0}