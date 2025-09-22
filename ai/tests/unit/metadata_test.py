import pytest

try:
    import chromadb
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False

def test_chromadb_metadata_structure():
    """
    ChromaDB 메타데이터 구조 확인 테스트
    """
    if not HAS_CHROMADB:
        pytest.skip("ChromaDB 패키지가 설치되지 않았습니다.")
    
    # ChromaDB 클라이언트 연결
    client = chromadb.HttpClient(host='144.24.69.36', port=8001)
    
    # 컬렉션 명
    # 승인된 데이터: approved_templates
    # 스팸 관련 정보통신망법 안내서 pdf: spam_prevention_documents
    # 공용 템플릿: pulblic_templates
    
    collection_name = "pulblic_templates"
    collection = client.get_collection(collection_name)

    # 컬렉션에서 데이터 1개 조회
    sample_data = collection.get(limit=1, include=["documents"])
    
    # 메타데이터 구조 검증
    assert 'documents' in sample_data
    assert len(sample_data['documents']) > 0
    
    # 메타데이터 구조 출력 (디버깅용)
    print("ChromaDB에 저장된 메타데이터 샘플:")
    print(sample_data['documents'][0])
    
    # 기본적인 메타데이터 필드 검증
    document = sample_data['documents'][0]
    assert isinstance(document, dict)
    
    # approved_templates 예상 메타데이터 구조:
    # 'priority': 'high',
    # 'id': '00', 
    # 'title': '회사소개서 발송',
    # 'source': 'approved_data',
    # 'category_1': '서비스이용',
    # 'template_type': 'approved_template',
    # 'category_2': '이용안내/공지',
    # 'button': '소개서'
    
    # pulblic_templates 예상 메타데이터 구조:
    # {'button': '', 'category': '운영안내', 'title': '휴무 안내', 'id': 'template_001'}
