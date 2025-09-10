#!/usr/bin/env python3
"""
ChromaDB 데이터베이스 정보 확인 스크립트
- 모든 컬렉션 목록 조회
- 각 컬렉션의 문서 수 및 샘플 데이터 확인
- 데이터베이스 경로 및 설정 정보 표시
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    print("❌ ChromaDB 패키지가 설치되지 않았습니다.")
    print("설치 방법: pip install chromadb")
    sys.exit(1)

from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def get_chromadb_client():
    """ChromaDB 클라이언트 생성"""
    persist_dir = os.getenv('CHROMA_PERSIST_DIR', './chroma_db')
    chroma_host = os.getenv('CHROMA_HOST', None)
    chroma_port = os.getenv('CHROMA_PORT', None)
    
    if chroma_host and chroma_port:
        print(f"🔗 원격 ChromaDB 서버에 연결: {chroma_host}:{chroma_port}")
        return chromadb.HttpClient(
            host=chroma_host,
            port=int(chroma_port),
            settings=Settings(anonymized_telemetry=False)
        ), f"{chroma_host}:{chroma_port}"
    else:
        print(f"💾 로컬 ChromaDB에 연결: {persist_dir}")
        return chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        ), persist_dir

def get_collection_info(collection) -> Dict[str, Any]:
    """컬렉션 정보 조회"""
    try:
        count = collection.count()
        
        # 샘플 문서 조회 (최대 3개)
        sample_docs = collection.get(limit=3)
        
        # 메타데이터 통계
        metadata_stats = {}
        if sample_docs.get('metadatas'):
            for metadata in sample_docs['metadatas']:
                for key, value in metadata.items():
                    if key not in metadata_stats:
                        metadata_stats[key] = set()
                    metadata_stats[key].add(str(value))
        
        return {
            'count': count,
            'sample_documents': sample_docs.get('documents', [])[:3],
            'sample_metadatas': sample_docs.get('metadatas', [])[:3],
            'metadata_fields': {k: list(v) for k, v in metadata_stats.items()}
        }
    except Exception as e:
        return {'error': str(e)}

def print_separator(title: str):
    """구분선 출력"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_collection_details(collection_name: str, info: Dict[str, Any]):
    """컬렉션 상세 정보 출력"""
    print(f"\n📁 컬렉션: {collection_name}")
    print("-" * 40)
    
    if 'error' in info:
        print(f"❌ 오류: {info['error']}")
        return
    
    print(f"📊 문서 수: {info['count']}")
    
    if info['metadata_fields']:
        print(f"🏷️  메타데이터 필드:")
        for field, values in info['metadata_fields'].items():
            print(f"   - {field}: {values[:5]}{'...' if len(values) > 5 else ''}")
    
    if info['sample_documents']:
        print(f"\n📄 샘플 문서 (최대 3개):")
        for i, doc in enumerate(info['sample_documents'], 1):
            print(f"   {i}. {doc[:100]}{'...' if len(doc) > 100 else ''}")
    
    if info['sample_metadatas']:
        print(f"\n🏷️  샘플 메타데이터:")
        for i, metadata in enumerate(info['sample_metadatas'], 1):
            print(f"   {i}. {metadata}")

def main():
    """메인 함수"""
    print_separator("ChromaDB 데이터베이스 정보 확인")
    
    try:
        # ChromaDB 클라이언트 생성
        client, db_location = get_chromadb_client()
        
        print(f"📍 데이터베이스 위치: {db_location}")
        
        # 모든 컬렉션 조회
        collections = client.list_collections()
        
        if not collections:
            print("\n❌ 컬렉션이 없습니다.")
            return
        
        print(f"\n📚 총 {len(collections)}개의 컬렉션을 찾았습니다.")
        
        # 각 컬렉션 정보 조회
        total_documents = 0
        expected_collections = ["policy_guidelines", "blacklist", "whitelist", "approved"]
        
        for collection in collections:
            collection_name = collection.name
            info = get_collection_info(collection)
            print_collection_details(collection_name, info)
            if 'count' in info:
                total_documents += info['count']
        
        # 예상 컬렉션 중 없는 것들 표시
        existing_collection_names = [c.name for c in collections]
        missing_collections = [name for name in expected_collections if name not in existing_collection_names]
        
        if missing_collections:
            print(f"\n⚠️  예상 컬렉션 중 없는 것들: {missing_collections}")
            print("   - policy_guidelines: 정책 가이드라인")
            print("   - blacklist: 금지된 템플릿")
            print("   - whitelist: 허용된 템플릿")
            print("   - approved: 승인된 템플릿")
        
        print_separator("요약")
        print(f"📊 총 컬렉션 수: {len(collections)}")
        print(f"📄 총 문서 수: {total_documents}")
        print(f"📍 데이터베이스 위치: {db_location}")
        
        # 데이터베이스 파일 정보 (로컬인 경우)
        if os.path.exists(db_location):
            print(f"\n💾 데이터베이스 파일 정보:")
            for root, dirs, files in os.walk(db_location):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    print(f"   - {file}: {file_size:,} bytes")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
