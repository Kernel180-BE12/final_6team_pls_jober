try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    print("Warning: ChromaDB 패키지가 설치되지 않았습니다. Mock 모드로 실행됩니다.")
from typing import List, Dict, Any, Optional
import os

from dotenv import load_dotenv

load_dotenv()

class ChromaDBService:
    def __init__(self, db_path: str = None, collection_name: str = "default"):
        """
        ChromaDB 서비스 초기화 (컬렉션별 동적 접근)
        """
        self.collection_name = collection_name
        
        # 환경 변수에서 ChromaDB 설정 읽기
        persist_dir = os.getenv('CHROMA_PERSIST_DIR', './chroma_db')
        chroma_host = os.getenv('CHROMA_HOST')
        chroma_port = os.getenv('CHROMA_PORT')
        
        # db_path 설정
        self.db_path = db_path or persist_dir
        self.client = None
        
        if HAS_CHROMADB:
            try:
                if chroma_host and chroma_port:
                    self.client = chromadb.HttpClient(
                        host=chroma_host,
                        port=int(chroma_port),
                        settings=Settings(anonymized_telemetry=False),
                        tenant="default_tenant",
                        database="default_database"
                    )
                else:
                    self.client = chromadb.PersistentClient(
                        path=persist_dir,
                        settings=Settings(anonymized_telemetry=False)
                    )
            except Exception:
                self.client = None
    
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
    
    async def add_documents(self, collection_name: str, documents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None):
        """
        특정 컬렉션에 문서들을 추가
        """
        try:
            collection = self._get_or_create_collection(collection_name)
            if collection is None:
                return {"message": f"컬렉션을 생성할 수 없어 {len(documents)}개 문서 추가 실패", "ids": []}
            
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in documents]
            
            if metadatas is None:
                metadatas = [{"source": "user_input"} for _ in documents]
            else:
                # None 항목을 기본 메타데이터로 대체
                normalized: List[Dict[str, Any]] = []
                for md in metadatas:
                    normalized.append(md or {"source": "user_input"})
                metadatas = normalized
            
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            return {"message": f"{len(documents)}개의 문서가 추가되었습니다.", "ids": ids}
        except Exception as e:
            raise Exception(f"문서 추가 실패: {str(e)}")
    
    async def search_documents(self, collection_name: str, query: str, n_results: int = 5, where: Optional[Dict[str, Any]] = None):
        """
        특정 컬렉션에서 문서 검색
        """
        try:
            collection = self._get_or_create_collection(collection_name)
            if collection is None:
                return {
                    "query": query,
                    "documents": [],
                    "results": [],
                    "metadatas": [],
                    "distances": []
                }
            
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            documents = results["documents"][0] if results["documents"] else []
            metadatas = results["metadatas"][0] if results["metadatas"] else []
            distances = results["distances"][0] if results["distances"] else []
            return {
                "query": query,
                "documents": documents,
                "results": documents,
                "metadatas": metadatas,
                "distances": distances
            }
        except Exception as e:
            raise Exception(f"문서 검색 실패: {str(e)}")
    
    async def get_document_by_id(self, document_id: str):
        """
        ID로 문서 조회
        """
        try:
            if self.collection is None:
                return None
            results = self.collection.get(ids=[document_id])
            if results["documents"]:
                return {
                    "id": document_id,
                    "document": results["documents"][0],
                    "metadata": results["metadatas"][0] if results["metadatas"] else {}
                }
            else:
                return None
        except Exception as e:
            raise Exception(f"문서 조회 실패: {str(e)}")
    
    async def get_collection_info(self):
        """
        컬렉션 정보 조회
        """
        try:
            if self.collection is None:
                return {
                    "collection_name": self.collection_name,
                    "document_count": 0
                }
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count
            }
        except Exception as e:
            raise Exception(f"컬렉션 정보 조회 실패: {str(e)}")
    
    def get_all_documents(self):
        """
        모든 문서 조회 (ConstraintValidator에서 사용)
        """
        try:
            if self.collection is None:
                return []
            results = self.collection.get()
            documents = []
            
            if results['documents']:
                for i in range(len(results['documents'])):
                    documents.append({
                        'id': results['ids'][i],
                        'content': results['documents'][i],
                        'metadata': results['metadatas'][i] if results['metadatas'] else {}
                    })
            
            return documents
            
        except Exception as e:
            print(f"모든 문서 조회 중 오류: {e}")
            return []
    
    async def initialize(self):
        """서비스 초기화"""
        try:
            if hasattr(self, '_initialized') and self._initialized:
                return
            await self.load_initial_guidelines()
            self._initialized = True
        except Exception:
            raise
    
    
    
    def search_similar(self, 
                      query: str, 
                      collection_name: str = "blacklist",
                      n_results: int = 5,
                      category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        유사한 가이드라인 검색 (VectorDBManager 호환)
        """
        try:
            
            # 지정된 컬렉션 가져오기
            collection = self._get_or_create_collection(collection_name)
            if collection is None:
                return []
            
            # 메타데이터 필터 설정
            where_filter = {}
            if category_filter:
                where_filter['category'] = category_filter
            
            # 컬렉션 문서 개수 확인
            collection_count = collection.count()
            print(f"🔍 {collection_name} 컬렉션 총 문서 수: {collection_count}")
            
            # 카테고리 필터 디버깅
            if where_filter:
                print(f"🔍 카테고리 필터 적용: {where_filter}")
                # 필터 없이 검색해서 전체 문서 확인
                all_results = collection.query(query_texts=[query], n_results=n_results)
                print(f"🔍 필터 없이 검색 시 결과 수: {len(all_results['documents'][0]) if all_results['documents'] and all_results['documents'][0] else 0}")
            
            # 검색 실행
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter if where_filter else None
            )
            
            print(f"🔍 검색 결과 원본: documents={len(results['documents'][0]) if results['documents'] and results['documents'][0] else 0}개")
            
            # 결과 포맷팅
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    distance = results['distances'][0][i]
                    # 코사인 거리(0~2)를 정규화된 유사도(0~1)로 변환
                    # distance가 0이면 similarity=1 (완전 유사)
                    # distance가 2이면 similarity=0 (완전 반대)
                    similarity = max(0.0, 1.0 - (distance / 2.0))
                    print(f"   결과 {i+1}: distance={distance:.4f}, similarity={similarity:.4f}")
                    
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': distance,
                        'similarity': similarity  # 올바른 유사도 계산
                    })
            else:
                print("⚠️ 검색 결과가 비어있음 - 컬렉션에 문서가 없거나 필터 조건에 맞는 문서가 없음")
            
            return formatted_results
            
        except Exception:
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """컬렉션 통계 정보 반환 (VectorDBManager 호환)"""
        try:
            if self.collection is None:
                return {
                    "total_documents": 0,
                    "collection_name": self.collection_name,
                    "mode": "chromadb",
                    "db_path": self.db_path,
                    "error": "collection not initialized"
                }
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "mode": "chromadb",
                "db_path": self.db_path
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def load_initial_guidelines(self):
        """초기 가이드라인 데이터 로드 (필요 시 확장). 현재는 no-op."""
        try:
            return
        except Exception:
            return
    
    def get_collection(self, collection_name: str = None):
        """특정 컬렉션 가져오기"""
        if not HAS_CHROMADB or self.client is None:
            return None
        try:
            # collection_name이 없으면 기본 컬렉션 이름 사용
            name = collection_name or self.collection_name
            return self.client.get_or_create_collection(name=name)
        except Exception:
            return None
    
    def get_blacklist_templates(self) -> List[Dict[str, Any]]:
        """블랙리스트 템플릿 조회"""
        try:
            blacklist_collection = self.get_collection("blacklist")
            if blacklist_collection is None:
                return []
            
            results = blacklist_collection.get()
            
            templates = []
            if results['documents']:
                for i in range(len(results['documents'])):
                    templates.append({
                        'id': results['ids'][i],
                        'content': results['documents'][i],
                        'metadata': results['metadatas'][i] if results['metadatas'] else {}
                    })
            
            return templates
        except Exception as e:
            return []
    
    def get_whitelist_templates(self) -> List[Dict[str, Any]]:
        """화이트리스트 템플릿 조회"""
        try:
            whitelist_collection = self.get_collection("whitelist")
            if whitelist_collection is None:
                return []
            
            results = whitelist_collection.get()
            
            templates = []
            if results['documents']:
                for i in range(len(results['documents'])):
                    templates.append({
                        'id': results['ids'][i],
                        'content': results['documents'][i],
                        'metadata': results['metadatas'][i] if results['metadatas'] else {}
                    })
            
            return templates
        except Exception as e:
            return []
    
    def get_approved_templates(self) -> List[Dict[str, Any]]:
        """승인된 템플릿 조회"""
        try:
            approved_collection = self.get_collection("approved")
            if approved_collection is None:
                return []
            
            results = approved_collection.get()
            
            templates = []
            if results['documents']:
                for i in range(len(results['documents'])):
                    templates.append({
                        'id': results['ids'][i],
                        'content': results['documents'][i],
                        'metadata': results['metadatas'][i] if results['metadatas'] else {}
                    })
            
            return templates
        except Exception as e:
            return []
    
    def add_template_to_collection(self, collection_name: str, template_data: Dict[str, Any]):
        """특정 컬렉션에 템플릿 추가"""
        try:
            collection = self.get_collection(collection_name)
            if collection is None:
                return
            
            collection.add(
                documents=[template_data.get('content', '')],
                metadatas=[template_data.get('metadata', {})],
                ids=[template_data.get('id', '')]
            )
        except Exception as e:
            return
    
    def search_templates_in_collection(self, collection_name: str, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """특정 컬렉션에서 템플릿 검색"""
        try:
            collection = self.get_collection(collection_name)
            if collection is None:
                return []
            
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i],
                        'similarity': 1 - results['distances'][0][i]
                    })
            
            return formatted_results
        except Exception as e:
            return []
    
