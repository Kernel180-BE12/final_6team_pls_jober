try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    print("Warning: ChromaDB 패키지가 설치되지 않았습니다. Mock 모드로 실행됩니다.")
from typing import List, Dict, Any, Optional
import os
import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

class ChromaDBService:
    def __init__(self, 
                 collection_name: str = "policy_guidelines",
                 db_path: str = None):
        """
        ChromaDB 서비스 초기화
        """

        # 환경 변수에서 ChromaDB 설정 읽기
        persist_dir = os.getenv('CHROMA_PERSIST_DIR', './chroma_db')
        chroma_host = os.getenv('CHROMA_HOST', None)
        chroma_port = os.getenv('CHROMA_PORT', None)
        
        # db_path 설정
        self.db_path = db_path or persist_dir
        
        if chroma_host and chroma_port:
            # 원격 ChromaDB 서버 연결
            self.client = chromadb.HttpClient(
                host=chroma_host,
                port=int(chroma_port)
            )
        else:
            # 로컬 ChromaDB 사용
            self.client = chromadb.PersistentClient(path=persist_dir)
        
        self.collection_name = collection_name
        self.mock_guidelines = []  # Mock 데이터용
        
        self.is_mock = False  # 기본값 설정
        
        if HAS_CHROMADB:
            try:
                # ChromaDB 클라이언트 초기화 (원격/로컬 자동 선택)
                chroma_host = os.getenv("CHROMA_HOST")
                chroma_port = os.getenv("CHROMA_PORT")
                
                if chroma_host and chroma_port:
                    # 원격 ChromaDB 서버 연결
                    print(f"원격 ChromaDB 서버에 연결 중: {chroma_host}:{chroma_port}")
                    self.client = chromadb.HttpClient(
                        host=chroma_host,
                        port=int(chroma_port),
                        settings=Settings(anonymized_telemetry=False)
                    )
                else:
                    # 로컬 ChromaDB 연결
                    print(f"로컬 ChromaDB에 연결 중: {persist_dir}")
                    self.client = chromadb.PersistentClient(
                        path=persist_dir,
                        settings=Settings(anonymized_telemetry=False)
                    )
                
                self.collection = self._get_or_create_collection()
                self.is_mock = False
            except Exception as e:
                print(f"ChromaDB 초기화 실패, Mock 모드로 전환: {e}")
                self.is_mock = True
        else:
            self.is_mock = True
            print("Mock 모드로 ChromaDBService 실행됩니다.")
    
    def _get_or_create_collection(self):
        """
        컬렉션 가져오기 또는 생성
        """
        if not HAS_CHROMADB or self.is_mock:
            return None
        
        # 1.x에서 권장되는 단일 호출
        return self.client.get_or_create_collection(name=self.collection_name)
    
    async def add_documents(self, documents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None):
        """
        문서들을 ChromaDB에 추가
        """
        try:
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in documents]
            
            if metadatas is None:
                metadatas = [{"source": "user_input"} for _ in documents]
            
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            return {"message": f"{len(documents)}개의 문서가 추가되었습니다.", "ids": ids}
        except Exception as e:
            raise Exception(f"문서 추가 실패: {str(e)}")
    
    async def search_documents(self, query: str, n_results: int = 5, where: Optional[Dict[str, Any]] = None):
        """
        문서 검색
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            return {
                "query": query,
                "results": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "distances": results["distances"][0] if results["distances"] else []
            }
        except Exception as e:
            raise Exception(f"문서 검색 실패: {str(e)}")
    
    async def get_document_by_id(self, document_id: str):
        """
        ID로 문서 조회
        """
        try:
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
    
    async def update_document(self, document_id: str, document: str, metadata: Optional[Dict[str, Any]] = None):
        """
        문서 업데이트
        """
        try:
            self.collection.update(
                ids=[document_id],
                documents=[document],
                metadatas=[metadata] if metadata else None
            )
            return {"message": "문서가 업데이트되었습니다.", "id": document_id}
        except Exception as e:
            raise Exception(f"문서 업데이트 실패: {str(e)}")
    
    async def delete_document(self, document_id: str):
        """
        문서 삭제
        """
        try:
            self.collection.delete(ids=[document_id])
            return {"message": "문서가 삭제되었습니다.", "id": document_id}
        except Exception as e:
            raise Exception(f"문서 삭제 실패: {str(e)}")
    
    async def get_collection_info(self):
        """
        컬렉션 정보 조회
        """
        try:
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
            if self.is_mock:
                return self.mock_guidelines
            
            # ChromaDB에서 모든 문서 조회
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
            # 이미 초기화된 경우 스킵
            if hasattr(self, '_initialized') and self._initialized:
                return
            
            # 가이드라인 로드
            await self.load_initial_guidelines()
            self._initialized = True
            
        except Exception as e:
            print(f"ChromaDB 서비스 초기화 실패: {e}")
            raise
    
    def add_guidelines(self, guidelines_data: List[Dict[str, Any]]):
        """
        가이드라인 데이터를 벡터DB에 추가 (VectorDBManager 호환)
        """
        if self.is_mock:
            # Mock 모드: 단순히 리스트에 저장
            for guideline in guidelines_data:
                self.mock_guidelines.append({
                    'id': guideline['id'],
                    'content': guideline['content'],
                    'metadata': {
                        'category': guideline.get('category', 'general'),
                        'type': guideline.get('type', 'guideline'),
                        'source': guideline.get('source', 'manual'),
                        **guideline.get('metadata', {})
                    }
                })
            return
        
        documents = []
        metadatas = []
        ids = []
        
        for guideline in guidelines_data:
            documents.append(guideline['content'])
            metadatas.append({
                'category': guideline.get('category', 'general'),
                'type': guideline.get('type', 'guideline'),
                'source': guideline.get('source', 'manual'),
                **guideline.get('metadata', {})
            })
            ids.append(guideline['id'])
        
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        except Exception as e:
            print(f"가이드라인 추가 실패: {e}")
    
    def search_similar(self, 
                      query: str, 
                      n_results: int = 5,
                      category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        유사한 가이드라인 검색 (VectorDBManager 호환)
        """
        if self.is_mock:
            # Mock 모드: 간단한 키워드 매칭으로 시뮬레이션
            formatted_results = []
            query_lower = query.lower()
            
            for guideline in self.mock_guidelines:
                # 간단한 키워드 매칭 점수 계산
                content_lower = guideline['content'].lower()
                common_words = set(query_lower.split()) & set(content_lower.split())
                similarity = len(common_words) / max(len(query_lower.split()), 1) * 0.7
                
                # 카테고리 필터 적용
                if category_filter and guideline['metadata'].get('category') != category_filter:
                    continue
                
                if similarity > 0.1:  # 최소 임계값
                    formatted_results.append({
                        'id': guideline['id'],
                        'content': guideline['content'],
                        'metadata': guideline['metadata'],
                        'distance': 1 - similarity,
                        'similarity': similarity
                    })
            
            # 유사도 순으로 정렬하고 n_results 개수만큼 반환
            formatted_results.sort(key=lambda x: x['similarity'], reverse=True)
            return formatted_results[:n_results]
        
        try:
            # 메타데이터 필터 설정
            where_filter = {}
            if category_filter:
                where_filter['category'] = category_filter
            
            # 검색 실행
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter if where_filter else None
            )
            
            # 결과 포맷팅
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i],
                        'similarity': 1 - results['distances'][0][i]  # 유사도 계산
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"검색 실패: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """컬렉션 통계 정보 반환 (VectorDBManager 호환)"""
        try:
            if self.is_mock:
                return {
                    "total_documents": len(self.mock_guidelines),
                    "collection_name": self.collection_name,
                    "mode": "mock",
                    "db_path": self.db_path
                }
            else:
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
        """
        초기 가이드라인 데이터 로드 (이제 ChromaDB에서 직접 로드)
        """
        try:
            # 기존 데이터 확인
            if self.is_mock:
                if len(self.mock_guidelines) == 0:
                    print("Mock DB에 가이드라인이 없습니다. ChromaDB에서 로드하거나 수동으로 추가해주세요.")
                else:
                    print(f"기존 가이드라인 {len(self.mock_guidelines)}개가 Mock DB에 있습니다.")
            else:
                existing_count = self.collection.count()
                if existing_count == 0:
                    print("ChromaDB에 가이드라인이 없습니다. 수동으로 추가해주세요.")
                else:
                    print(f"기존 가이드라인 {existing_count}개가 벡터DB에 있습니다.")
                
        except Exception as e:
            print(f"가이드라인 로드 중 오류: {e}")
    
    def get_collection(self, collection_name: str):
        """특정 컬렉션 가져오기"""
        if not HAS_CHROMADB or self.is_mock:
            return None
        return self.client.get_or_create_collection(name=collection_name)
    
    def get_blacklist_templates(self) -> List[Dict[str, Any]]:
        """블랙리스트 템플릿 조회"""
        try:
            if self.is_mock:
                return []
            
            blacklist_collection = self.get_collection("blacklist")
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
            print(f"블랙리스트 템플릿 조회 실패: {e}")
            return []
    
    def get_whitelist_templates(self) -> List[Dict[str, Any]]:
        """화이트리스트 템플릿 조회"""
        try:
            if self.is_mock:
                return []
            
            whitelist_collection = self.get_collection("whitelist")
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
            print(f"화이트리스트 템플릿 조회 실패: {e}")
            return []
    
    def get_approved_templates(self) -> List[Dict[str, Any]]:
        """승인된 템플릿 조회"""
        try:
            if self.is_mock:
                return []
            
            approved_collection = self.get_collection("approved")
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
            print(f"승인된 템플릿 조회 실패: {e}")
            return []
    
    def add_template_to_collection(self, collection_name: str, template_data: Dict[str, Any]):
        """특정 컬렉션에 템플릿 추가"""
        try:
            if self.is_mock:
                print(f"Mock 모드: {collection_name} 컬렉션에 템플릿 추가 시뮬레이션")
                return
            
            collection = self.get_collection(collection_name)
            collection.add(
                documents=[template_data.get('content', '')],
                metadatas=[template_data.get('metadata', {})],
                ids=[template_data.get('id', '')]
            )
            print(f"템플릿이 {collection_name} 컬렉션에 추가되었습니다.")
        except Exception as e:
            print(f"템플릿 추가 실패: {e}")
    
    def search_templates_in_collection(self, collection_name: str, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """특정 컬렉션에서 템플릿 검색"""
        try:
            if self.is_mock:
                return []
            
            collection = self.get_collection(collection_name)
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
            print(f"{collection_name} 컬렉션 검색 실패: {e}")
            return []
