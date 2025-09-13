# main_pipeline.py

import os
import json
import logging
from typing import TypedDict, List, Literal, Optional, Dict, Any, Tuple
from abc import ABC, abstractmethod

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import openai
import chromadb
from chromadb.config import Settings

# --- 로깅 설정 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 환경 변수 로드 ---
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# ##############################################################################
# 제공해주신 코드 통합 시작
# ##############################################################################

# === 1. 프롬프트 빌더 클래스들 (from message_analyzer_prompts.py & template_generator.py) ===

class BasePromptBuilder(ABC):
    def __init__(self, user_text: str):
        self.user_text = user_text
        self.hints: list[dict] = []

    def add_hint(self, description: str, content: str):
        self.hints.append({"description": description, "content": content})
        return self

    def _build_hint_messages(self) -> list[dict]:
        return [{"role": "system", "content": h["content"]} for h in self.hints]

    @abstractmethod
    def build(self) -> list[dict]:
        pass

class TypePromptBuilder(BasePromptBuilder):
    def build(self) -> list[dict]:
        # (내용이 길어 생략) 실제 TypePromptBuilder의 build 메서드 내용이 여기에 들어갑니다.
        return [
            {"role": "system", "content": "메시지 유형을 판정하는 분류기입니다. [BASIC, EXTRA_INFO, CHANNEL_ADD, HYBRID] 중 하나와 이유를 JSON으로 출력합니다."},
            {"role": "user", "content": f"본문: {self.user_text}"}
        ]

class CategoryPromptBuilder(BasePromptBuilder):
    def __init__(self, user_text: str, category_main: str, category_sub_list: list):
        super().__init__(user_text)
        self.category_main = category_main
        self.category_sub_list = category_sub_list

    def build(self) -> list[dict]:
        # (내용이 길어 생략) 실제 CategoryPromptBuilder의 build 메서드 내용이 여기에 들어갑니다.
        return [
            {"role": "system", "content": f"다음 서브 카테고리 리스트 중 가장 적절한 것을 JSON으로 선택하세요: {self.category_sub_list}"},
            {"role": "user", "content": f"본문: {self.user_text}\n대분류: {self.category_main}"}
        ]

class TemplateTitlePromptBuilder:
    def __init__(self, user_text: str):
        self.user_text = user_text

    def build(self) -> list[dict]:
        return [
            {"role": "system", "content": "주어진 본문을 기반으로 10자 이내의 간결한 제목을 생성해주세요. 제목만 출력합니다."},
            {"role": "user", "content": self.user_text}
        ]

class ReferenceBasedTemplatePromptBuilder:
    def __init__(self, user_text: str, reference_template: str):
        self.user_text = user_text
        self.reference_template = reference_template

    def build(self) -> list[dict]:
        return [
            {"role": "system", "content": f"다음 참고 템플릿의 스타일과 구조를 따라, 사용자 요청에 맞는 새 템플릿을 생성해주세요. 템플릿 본문만 출력합니다.\n\n참고 템플릿:\n{self.reference_template}"},
            {"role": "user", "content": f"사용자 요청:\n{self.user_text}"}
        ]

class NewTemplatePromptBuilder:
    def __init__(self, user_text: str):
        self.user_text = user_text

    def build(self) -> list[dict]:
        return [
            {"role": "system", "content": "카카오 알림톡 규정에 맞는 정보성 템플릿을 생성해주세요. 변수는 #{변수명} 형식으로 표현하고, 템플릿 본문만 출력합니다."},
            {"role": "user", "content": f"사용자 요청:\n{self.user_text}"}
        ]

# === 2. 서비스 클래스들 (from openai_service.py, message_analyzer.py, template_generator.py) ===

class OpenAIService:
    """실제 OpenAI 서비스"""
    def __init__(self):
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        self.client = openai.OpenAI()

    def chat_completion(self, prompt: List[Dict[str, str]], model: str = "gpt-4o-mini") -> str:
        logger.info(f"OpenAI API 호출 (모델: {model})")
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=prompt,
                temperature=0.3,
            )
            content = response.choices[0].message.content.strip()
            # LLM 응답이 마크다운 코드 블록을 포함하는 경우 제거
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            return content
        except Exception as e:
            logger.error(f"OpenAI API 호출 중 오류 발생: {e}")
            raise

class MessageAnalyzer:
    """메시지 분석기 (유형, 카테고리 분류)"""
    def __init__(self, service: OpenAIService):
        self.service = service

    def classify_message_type(self, user_text: str) -> Dict:
        prompt = TypePromptBuilder(user_text).build()
        content = self.service.chat_completion(prompt)
        return json.loads(content)

    def classify_message_category(self, user_text: str, category_main: str, category_sub_list: list) -> Dict:
        prompt = CategoryPromptBuilder(user_text, category_main, category_sub_list).build()
        content = self.service.chat_completion(prompt)
        return json.loads(content)

class TemplateGenerator:
    """템플릿 생성기 (RAG 검색 및 생성)"""
    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service
        self.chroma_client = None
        self.collection = None
        self._connect_to_chroma()

    def _connect_to_chroma(self):
        try:
            host = os.getenv('CHROMA_HOST', 'localhost')
            port = int(os.getenv('CHROMA_PORT', '8000'))
            logger.info(f"ChromaDB 연결 시도 중... (Host: {host}:{port})")
            self.chroma_client = chromadb.HttpClient(host=host, port=port)
            self.chroma_client.heartbeat() # 연결 테스트
            self.collection = self.chroma_client.get_or_create_collection('approved')
            logger.info("✅ ChromaDB HTTP 연결 성공")
        except Exception as e:
            logger.warning(f"⚠️ ChromaDB HTTP 연결 실패: {e}. 로컬 모드로 전환합니다.")
            persist_dir = os.getenv('CHROMA_PERSIST_DIR', './chroma_db')
            self.chroma_client = chromadb.PersistentClient(path=persist_dir)
            self.collection = self.chroma_client.get_or_create_collection('approved')
            logger.info(f"✅ 로컬 ChromaDB 연결 성공 (Path: {persist_dir})")
            # 테스트용 데이터 추가
            self.collection.add(
                ids=["test-001"],
                documents=["고객님의 주문이 완료되었습니다. 주문번호: #{order_id}"],
                metadatas=[{"category_sub": "주문/예약"}]
            )


    def search_similar_templates(self, query_text: str, category_sub: str, top_k: int = 1) -> List[Dict[str, Any]]:
        logger.info(f"ChromaDB 검색: 카테고리 '{category_sub}'에서 '{query_text}' 검색")
        if not self.collection:
            logger.error("ChromaDB 컬렉션이 초기화되지 않았습니다.")
            return []

        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k,
            where={"category_sub": category_sub},
            include=['documents', 'distances', 'metadatas']
        )

        if not results['ids'][0]:
            return []

        return [
            {"id": id, "text": doc, "distance": dist, "metadata": meta}
            for id, doc, dist, meta in zip(results['ids'][0], results['documents'][0], results['distances'][0], results['metadatas'][0])
        ]

    def generate_title(self, user_text: str) -> str:
        prompt = TemplateTitlePromptBuilder(user_text).build()
        return self.openai_service.chat_completion(prompt)

    def generate_template_with_reference(self, user_text: str, reference_template: str) -> str:
        prompt = ReferenceBasedTemplatePromptBuilder(user_text, reference_template).build()
        return self.openai_service.chat_completion(prompt)

    def generate_new_template(self, user_text: str) -> str:
        prompt = NewTemplatePromptBuilder(user_text).build()
        return self.openai_service.chat_completion(prompt)

# ##############################################################################
# LangGraph 파이프라인 구성
# ##############################################################################

class TemplateGenerationState(TypedDict):
    # 입력
    user_text: str
    category_main: str
    category_sub_list: List[str]

    # 서비스 객체
    analyzer: MessageAnalyzer
    generator: TemplateGenerator

    # 중간 결과
    message_type: Optional[str]
    category_sub: Optional[str]
    similar_templates: List[Dict]
    similarity_score: float
    generation_hint: Optional[str]
    generated_title: str
    generated_template: str

    # 최종 결과
    final_result: Dict

# --- LangGraph 노드(단계) 정의 ---

def classify_message_type(state: TemplateGenerationState) -> TemplateGenerationState:
    logger.info("--- 1. 메시지 유형 분류 시작 ---")
    analyzer = state["analyzer"]
    result = analyzer.classify_message_type(state["user_text"])
    state["message_type"] = result.get("type")
    logger.info(f"결과: {state['message_type']}")
    return state

def generate_title_and_classify_category(state: TemplateGenerationState) -> TemplateGenerationState:
    logger.info("--- 2. 제목 생성 및 카테고리 분류 시작 ---")
    analyzer = state["analyzer"]
    generator = state["generator"]

    state["generated_title"] = generator.generate_title(state["user_text"])
    logger.info(f"생성된 제목: {state['generated_title']}")

    result = analyzer.classify_message_category(
        state["user_text"], state["category_main"], state["category_sub_list"]
    )
    state["category_sub"] = result.get("category_sub")
    logger.info(f"분류된 2차 카테고리: {state['category_sub']}")
    return state

def search_approved_templates(state: TemplateGenerationState) -> TemplateGenerationState:
    logger.info("--- 3. RAG - 유사 템플릿 검색 시작 ---")
    generator = state["generator"]

    if not state["category_sub"]:
        logger.warning("2차 카테고리가 없어 검색을 건너뜁니다.")
        state["similar_templates"] = []
        state["similarity_score"] = 0.0
        return state

    results = generator.search_similar_templates(
        query_text=state["user_text"],
        category_sub=state["category_sub"],
        top_k=1
    )

    if results:
        similarity = 1 - results[0].get("distance", 1.0)
        state["similar_templates"] = results
        state["similarity_score"] = similarity
        logger.info(f"검색 결과: 유사도 {similarity:.2f}")
    else:
        state["similar_templates"] = []
        state["similarity_score"] = 0.0
        logger.info("유사한 템플릿을 찾지 못했습니다.")
    return state

def decide_hint_addition(state: TemplateGenerationState) -> Literal["add_hint", "no_hint"]:
    logger.info("--- 4. 힌트 추가 여부 결정 ---")
    SIMILARITY_THRESHOLD = 0.7
    if state.get("similarity_score", 0.0) >= SIMILARITY_THRESHOLD:
        logger.info(f"유사도({state['similarity_score']:.2f})가 기준({SIMILARITY_THRESHOLD}) 이상. 힌트를 추가합니다.")
        return "add_hint"
    else:
        logger.info(f"유사도({state.get('similarity_score', 0.0):.2f})가 기준({SIMILARITY_THRESHOLD}) 미만. 힌트 없이 생성합니다.")
        return "no_hint"

def add_generation_hint(state: TemplateGenerationState) -> TemplateGenerationState:
    logger.info("--- 5a. 생성 힌트 추가 ---")
    reference_template = state["similar_templates"][0]["text"]
    state["generation_hint"] = reference_template
    return state

def generate_final_template(state: TemplateGenerationState) -> TemplateGenerationState:
    logger.info("--- 6. 최종 템플릿 생성 시작 ---")
    generator = state["generator"]
    user_text = state["user_text"]
    hint = state.get("generation_hint")

    if hint:
        logger.info("참고 템플릿 기반 생성")
        state["generated_template"] = generator.generate_template_with_reference(user_text, hint)
    else:
        logger.info("신규 템플릿 생성")
        state["generated_template"] = generator.generate_new_template(user_text)

    logger.info("최종 템플릿 생성 완료.")

    state["final_result"] = {
        "title": state["generated_title"],
        "template": state["generated_template"],
        "message_type": state["message_type"],
        "category_sub": state["category_sub"],
        "generation_method": "reference_based" if hint else "new_creation",
        "similarity_score": state.get("similarity_score", 0.0),
        "reference_templates": state.get("similar_templates", [])
    }
    return state

# --- LangGraph 그래프 구성 ---
workflow = StateGraph(TemplateGenerationState)

workflow.add_node("classify_type", classify_message_type)
workflow.add_node("title_and_category", generate_title_and_classify_category)
workflow.add_node("search_templates", search_approved_templates)
workflow.add_node("add_hint", add_generation_hint)
workflow.add_node("generate_template", generate_final_template)

workflow.set_entry_point("classify_type")
workflow.add_edge("classify_type", "title_and_category")
workflow.add_edge("title_and_category", "search_templates")
workflow.add_conditional_edges(
    "search_templates",
    decide_hint_addition,
    {"add_hint": "add_hint", "no_hint": "generate_template"}
)
workflow.add_edge("add_hint", "generate_template")
workflow.add_edge("generate_template", END)

app = workflow.compile()

# --- 실행 ---
if __name__ == "__main__":
    # 서비스 초기화
    openai_service = OpenAIService()
    analyzer = MessageAnalyzer(openai_service)
    generator = TemplateGenerator(openai_service)

    # 사용자 입력 예시
    user_input = {
        "user_text": "안녕하세요 라이언님, 주문하신 상품이 정상적으로 접수되었습니다. 주문번호는 12345입니다.",
        "category_main": "주문",
        "category_sub_list": [
            "구매완료", "구매취소", "기타", "뉴스레터", "리마인드", "방문서비스",
            "배송상태", "배송완료", "배송예정", "배송실패", "상품가입", "신청접수",
            "예약상태", "예약완료", "예약취소", "이용도구", "이용안내/공지",
            "요금청구", "주문/예약", "쿠폰발급", "피드백", "피드백 요청", "회원가입"
        ],
        # 상태에 서비스 객체 전달
        "analyzer": analyzer,
        "generator": generator,
    }

    # 파이프라인 실행
    final_state = app.invoke(user_input)

    print("\n" + "="*50)
    print("--- 최종 생성 결과 ---")
    print("="*50)
    print(json.dumps(final_state.get("final_result"), indent=2, ensure_ascii=False))
