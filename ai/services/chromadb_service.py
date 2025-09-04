import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class ChromaDBService:
    def __init__(self, collection_name: str = "documents"):
        """
        ChromaDB 서비스 초기화
        """
        # 환경 변수에서 ChromaDB 설정 읽기
        persist_dir = os.getenv('CHROMA_PERSIST_DIR', './chroma_db')
        chroma_host = os.getenv('CHROMA_HOST', None)
        chroma_port = os.getenv('CHROMA_PORT', None)
        
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
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """
        컬렉션 가져오기 또는 생성
        """
        try:
            return self.client.get_collection(name=self.collection_name)
        except:
            return self.client.create_collection(name=self.collection_name)
    
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
