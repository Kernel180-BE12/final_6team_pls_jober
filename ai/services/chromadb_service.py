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
    def __init__(self, 
                 collection_name: str = "alimtalk_guidelines",
                 db_path: str = None):
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
                    print(f"로컬 ChromaDB에 연결 중: {self.db_path}")
                    self.client = chromadb.PersistentClient(
                        path=self.db_path,
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
    
    async def load_initial_guidelines(self, guidelines_file: str = None):
        """
        초기 가이드라인 데이터 로드
        """
        if guidelines_file is None:
            guidelines_file = Path(__file__).parent.parent / "data" / "alimtalk_guidelines.json"
        
        if not os.path.exists(guidelines_file):
            # 기본 가이드라인 생성
            self._create_default_guidelines(guidelines_file)
        
        try:
            with open(guidelines_file, 'r', encoding='utf-8') as f:
                guidelines_data = json.load(f)
            
            # 기존 데이터 확인
            if self.is_mock:
                if len(self.mock_guidelines) == 0:
                    self.add_guidelines(guidelines_data)
                    print(f"가이드라인 {len(guidelines_data)}개를 Mock DB에 추가했습니다.")
                else:
                    print(f"기존 가이드라인 {len(self.mock_guidelines)}개가 Mock DB에 있습니다.")
            else:
                existing_count = self.collection.count()
                if existing_count == 0:
                    self.add_guidelines(guidelines_data)
                    print(f"가이드라인 {len(guidelines_data)}개를 벡터DB에 추가했습니다.")
                else:
                    print(f"기존 가이드라인 {existing_count}개가 벡터DB에 있습니다.")
                
        except Exception as e:
            print(f"가이드라인 로드 중 오류: {e}")
    
    def _create_default_guidelines(self, file_path: str):
        """기본 가이드라인 데이터 생성"""
        default_guidelines = [
            {
                "id": "guide_001",
                "content": "알림톡 본문은 1000자를 초과할 수 없습니다.",
                "category": "length",
                "type": "rule",
                "metadata": {"priority": "high", "source": "kakaotalk_policy"}
            },
            {
                "id": "guide_002",
                "content": "거래성 알림톡에는 광고성 표현을 포함할 수 없습니다.",
                "category": "content", 
                "type": "policy",
                "metadata": {"priority": "high", "source": "kakaotalk_policy"}
            },
            {
                "id": "guide_003",
                "content": "마케팅 알림톡에는 '(광고)' 표기가 필수입니다.",
                "category": "marketing",
                "type": "rule", 
                "metadata": {"priority": "critical", "source": "kakaotalk_policy"}
            },
            {
                "id": "guide_004",
                "content": "개인정보(주민번호, 카드번호 등)는 템플릿에 직접 포함할 수 없습니다.",
                "category": "privacy",
                "type": "policy",
                "metadata": {"priority": "critical", "source": "privacy_law"}
            },
            {
                "id": "guide_005",
                "content": "금융 관련 과장 표현(100% 보장, 무조건 등)은 사용할 수 없습니다.",
                "category": "financial",
                "type": "policy",
                "metadata": {"priority": "high", "source": "financial_law"}
            },
            {
                "id": "guide_006",
                "content": "의료 관련 단정적 표현(치료, 완치 등)은 사용할 수 없습니다.",
                "category": "medical",
                "type": "policy",
                "metadata": {"priority": "high", "source": "medical_law"}
            },
            {
                "id": "guide_007",
                "content": "버튼은 최대 5개까지만 추가할 수 있습니다.",
                "category": "button",
                "type": "rule",
                "metadata": {"priority": "medium", "source": "kakaotalk_policy"}
            },
            {
                "id": "guide_008",
                "content": "버튼명은 14자를 초과할 수 없습니다.",
                "category": "button",
                "type": "rule",
                "metadata": {"priority": "medium", "source": "kakaotalk_policy"}
            },
            {
                "id": "guide_009",
                "content": "변수명은 본문에서 사용되어야 합니다.",
                "category": "variable",
                "type": "rule",
                "metadata": {"priority": "medium", "source": "best_practice"}
            },
            {
                "id": "guide_010",
                "content": "수신거부 방법을 명시하는 것을 권장합니다.",
                "category": "marketing",
                "type": "recommendation",
                "metadata": {"priority": "low", "source": "best_practice"}
            }
        ]
        
        # 디렉토리 생성
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 파일 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(default_guidelines, f, ensure_ascii=False, indent=2)
