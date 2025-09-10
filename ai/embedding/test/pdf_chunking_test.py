# PDF 로드
import fitz  # PyMuPDF
from langchain.docstore.document import Document
# Embedding 불러오고, 선정한 Vector Store에 저장하기
from langchain_upstage import UpstageEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
import os
from langchain_upstage.chat_models import ChatUpstage
from langchain_core.output_parsers.string import StrOutputParser
os.environ["UPSTAGE_API_KEY"] = "up_1bFNNQg41he9UVkfuNsJmylM3PYVw"

# 1. PDF 열기
pdf_path = "../../srcFile/불법스팸_방지를_위한_정보통신망법_안내서_제5차_개정판.pdf"
doc = fitz.open(pdf_path)

# 2. PDF 전체 텍스트 → Document 리스트로 변환
documents = []
for page_num, page in enumerate(doc, start=1): # 1번 부터 시작해서 차례로 페이지 처리
    text = page.get_text("text")
    documents.append(
        Document(                              # 페이지 하나 단위
            page_content=text,
            metadata={"page": page_num, "source": pdf_path}
        )
    )

# 2. 텍스트 분할
# text_splitter -> RecursiveCharacterTextSplitter의 인스턴스
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=50
)

# 메서드 시그니처 : split_documents(documents: list[Document]) -> list[Document] : Document 객체 리스트를 받아서 청크 단위로 나누는 역할
splits = text_splitter.split_documents(documents)

# 3. 임베딩 및 벡터 저장소 생성
vectorstore = Chroma.from_documents(
    documents=splits, embedding=UpstageEmbeddings(model="embedding-query")
)

# 4. Dense Retriever 생성
query = "광고성 정보 전송시 명시사항에 대해 알려줘"

# Dense Retriever 생성
retriever = vectorstore.as_retriever(
    search_type= 'mmr',     # default : similarity(유사도) / mmr 알고리즘
    search_kwargs={"k": 5}  # 쿼리와 관련된 chunk를 10개 검색하기 (default : 4)
)

result_docs = retriever.invoke(query) # 쿼리 호출하여 retriever로 검색

# 5. ChatPromptTemplate 정의
# 괄호 하나에 시스템 프롬프트(모델에게 주는 지침 메시지)가 있음.
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            너는 인공지능 챗봇으로, 주어진 문서를 정확하게 이해해서 답변을 해야해.
            문서에 있는 내용으로만 답변하고 내용이 없다면, 잘 모르겠다고 답변해.
            ---
            CONTEXT:
            {context}
            """,
        ),
        ("human", "{input}"),
    ]
)

# 6. LLMChain 정의 StrOutputParser() : 모델의 출력 결과를 문자열 형태로 그대로 가져오는 역할.
llm = ChatUpstage(model='solar-pro2')
chain = prompt | llm | StrOutputParser()

# 예외 처리 : API 장애가 발생했을 때, 코드를 멈추지 않고 3번 자동 재시도.
import time

def safe_invoke(chain, inputs, retries=3, delay=5):
    for attempt in range(retries):
        try:
            return chain.invoke(inputs)
        except Exception as e:
            print(f"⚠️ Upstage API 호출 실패, 재시도 중... ({attempt+1}/{retries})")
            print(f"에러: {e}")
            time.sleep(delay)
    raise RuntimeError("Upstage API 연속 실패, 잠시 후 다시 시도해주세요.")

# 사용 예시
response = safe_invoke(chain, {"context": result_docs, "input": query})
print(response)
