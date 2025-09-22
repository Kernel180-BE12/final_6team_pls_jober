try:
    import chromadb
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    print("Warning: ChromaDB 패키지가 설치되지 않았습니다. 테스트를 건너뜁니다.")

# 현재 메타데이터 파악하는 코드 입니다.
# ChromaDB 클라이언트 연결

if HAS_CHROMADB:
    client = chromadb.HttpClient(host='144.24.69.36', port=8001)

"""
# **컬렉션 명**
# 승인된 데이터: approved_templates
# 스팸 관련 정보통신망법 안내서 pdf: spam_prevention_documents
# 공용 템플릿: pulblic_templates
"""

if HAS_CHROMADB:
    collection_name = "pulblic_templates"
    collection = client.get_collection(collection_name)

    # 컬렉션에서 데이터 1개 조회
    # documents
    # metadatas
    sample_data = collection.get(limit=1, include=["documents"])

    # 메타데이터 구조 출력
    print("ChromaDB에 저장된 메타데이터 샘플:")
    print(sample_data['documents'][0])
else:
    print("ChromaDB가 설치되지 않아 메타데이터 조회를 건너뜁니다.")

# approved_templates
# 'priority': 'high',
# 'id': '00',
# 'title': '회사소개서 발송',
# 'source': 'approved_data',
# 'category_1': '서비스이용',
# 'template_type': 'approved_template',
# 'category_2': '이용안내/공지',
# 'button': '소개서

# ChromaDB에 저장된 메타데이터 샘플:
# {'button': '', 'category': '운영안내', 'title': '휴무 안내', 'id': 'template_001'}
