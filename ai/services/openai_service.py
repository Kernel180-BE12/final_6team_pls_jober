import os
import json
import logging
from typing import TypedDict, List, Literal, Optional, Dict, Any

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

# --- 로깅 설정 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 가상 서비스 및 클래스 (실제 구현으로 대체 필요) ---
# 제공해주신 코드를 기반으로 OpenAIService, ChromaDBService 등을 구현/연결해야 합니다.

class OpenAIService:
    """가상 OpenAI 서비스"""
    def __init__(self):
        # from openai import OpenAI
        # self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        pass

    def chat_completion(self, prompt: List[Dict[str, str]], model: str = "gpt-4o-mini") -> str:
        logger.info(f"OpenAI API 호출 (모델: {model})")
        # response = self.client.chat.completions.create(messages=prompt, model=model)
        # return response.choices[0].message.content

        # --- 테스트용 Mock 응답 ---
        if "메시지 유형" in prompt[0]["content"]:
            return json.dumps({"type": "BASIC", "explain_type": "기본 정보만 포함"})
        if "서브 카테고리" in prompt[0]["content"]:
            return json.dumps({"category_sub": "주문/예약", "explain_category_sub": "주문 관련 내용으로 판단됨"})
        if "제목을 생성" in prompt[0]["content"]:
            return "주문 접수 완료 안내"
        if "템플릿을 생성" in prompt[0]["content"]:
            return "고객님, 소중한 주문이 정상적으로 접수되었습니다.\n- 주문번호: #{주문번호}\n- 주문금액: #{금액}"
        return ""

class ChromaDBService:
    """가상 ChromaDB 서비스"""
    def __init__(self):
        pass

    def search(self, query_text: str, category_sub: str, top_k: int = 1) -> List[Dict[str, Any]]:
        logger.info(f"ChromaDB 검색: 카테고리 '{category_sub}'에서 '{query_text}' 검색")
        # 실제 구현: self.collection.query(...)
        if category_sub == "주문/예약":
            return [{
                "text": "고객님의 주문이 완료되었습니다. 주문번호: #{order_id}",
                "distance": 0.25 # 1 - 0.75 (유사도)
            }]
        return []

# --- 프롬프트 빌더 (제공된 코드 활용) ---
# 실제로는 제공해주신 TypePromptBuilder, CategoryPromptBuilder 등을 사용합니다.
def build_prompt(task_type: str, **kwargs) -> List[Dict[str, str]]:
    if task_type == "type":
        return [{"role": "system", "content": "메시지 유형 판단 프롬프트"}, {"role": "user", "content": kwargs["user_text"]}]
    if task_type == "category":
        return [{"role": "system", "content": "서브 카테고리 판단 프롬프트"}, {"role": "user", "content": kwargs["user_text"]}]
    if task_type == "title":
        return [{"role": "system", "content": "제목을 생성해주세요."}, {"role": "user", "content": kwargs["user_text"]}]
    if task_type == "template":
        hint_text = f"힌트: {kwargs['hint']}" if kwargs.get("hint") else "힌트 없음"
        return [{"role": "system", "content": f"템플릿을 생성해주세요. {hint_text}"}, {"role": "user", "content": kwargs["user_text"]}]
    return []


# --- LangGraph 상태 정의 ---
class TemplateGenerationState(TypedDict):
    user_text: str
    category_main: str
    category_sub_list: List[str]

    # 각 단계에서 채워지는 값
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

# 서비스 인스턴스화
openai_service = OpenAIService()
chromadb_service = ChromaDBService()

def classify_message_type(state: TemplateGenerationState) -> TemplateGenerationState:
    """1. 메시지 4가지 유형 판단"""
    logger.info("--- 1. 메시지 유형 분류 시작 ---")
    prompt = build_prompt(task_type="type", user_text=state["user_text"])
    response = openai_service.chat_completion(prompt)
    result = json.loads(response)
    state["message_type"] = result.get("type")
    logger.info(f"결과: {state['message_type']}")
    return state

def generate_title_and_classify_category(state: TemplateGenerationState) -> TemplateGenerationState:
    """2. 제목 자동 생성 및 2차 카테고리 판단"""
    logger.info("--- 2. 제목 생성 및 카테고리 분류 시작 ---")

    # 제목 생성
    title_prompt = build_prompt(task_type="title", user_text=state["user_text"])
    state["generated_title"] = openai_service.chat_completion(title_prompt)
    logger.info(f"생성된 제목: {state['generated_title']}")

    # 카테고리 분류
    category_prompt = build_prompt(
        task_type="category",
        user_text=state["user_text"],
        category_main=state["category_main"],
        category_sub_list=state["category_sub_list"]
    )
    response = openai_service.chat_completion(category_prompt)
    result = json.loads(response)
    state["category_sub"] = result.get("category_sub")
    logger.info(f"분류된 2차 카테고리: {state['category_sub']}")

    return state

def search_approved_templates(state: TemplateGenerationState) -> TemplateGenerationState:
    """3. 매핑된 카테고리로 승인된 데이터셋 필터링 (RAG)"""
    logger.info("--- 3. RAG - 유사 템플릿 검색 시작 ---")
    if not state["category_sub"]:
        logger.warning("2차 카테고리가 없어 검색을 건너뜁니다.")
        state["similar_templates"] = []
        state["similarity_score"] = 0.0
        return state

    results = chromadb_service.search(
        query_text=state["user_text"],
        category_sub=state["category_sub"],
        top_k=1
    )

    if results:
        # distance를 유사도로 변환 (0에 가까울수록 유사)
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
    """4. 유사도 0.7 만족 여부 판단"""
    logger.info("--- 4. 힌트 추가 여부 결정 ---")
    SIMILARITY_THRESHOLD = 0.7
    if state["similarity_score"] >= SIMILARITY_THRESHOLD:
        logger.info(f"유사도({state['similarity_score']:.2f})가 기준({SIMILARITY_THRESHOLD}) 이상. 힌트를 추가합니다.")
        return "add_hint"
    else:
        logger.info(f"유사도({state['similarity_score']:.2f})가 기준({SIMILARITY_THRESHOLD}) 미만. 힌트 없이 생성합니다.")
        return "no_hint"

def add_generation_hint(state: TemplateGenerationState) -> TemplateGenerationState:
    """5a. 생성 프롬프트에 필드 관련 힌트 추가"""
    logger.info("--- 5a. 생성 힌트 추가 ---")
    reference_template = state["similar_templates"][0]["text"]
    state["generation_hint"] = f"다음 승인 템플릿의 구조와 스타일을 참고하세요: '{reference_template}'"
    return state

def generate_final_template(state: TemplateGenerationState) -> TemplateGenerationState:
    """6. 생성 프롬프트를 거쳐 템플릿 생성"""
    logger.info("--- 6. 최종 템플릿 생성 시작 ---")
    prompt = build_prompt(
        task_type="template",
        user_text=state["user_text"],
        hint=state.get("generation_hint")
    )
    state["generated_template"] = openai_service.chat_completion(prompt)
    logger.info("최종 템플릿 생성 완료.")

    # 최종 결과 구성
    state["final_result"] = {
        "title": state["generated_title"],
        "template": state["generated_template"],
        "message_type": state["message_type"],
        "category_sub": state["category_sub"],
        "generation_method": "reference_based" if state.get("generation_hint") else "new_creation",
        "similarity_score": state.get("similarity_score", 0.0),
        "reference_templates": state.get("similar_templates", [])
    }
    return state

# --- LangGraph 그래프 구성 ---
workflow = StateGraph(TemplateGenerationState)

# 노드 추가
workflow.add_node("classify_type", classify_message_type)
workflow.add_node("title_and_category", generate_title_and_classify_category)
workflow.add_node("search_templates", search_approved_templates)
workflow.add_node("add_hint", add_generation_hint)
workflow.add_node("generate_template", generate_final_template)

# 엣지(흐름) 연결
workflow.set_entry_point("classify_type")
workflow.add_edge("classify_type", "title_and_category")
workflow.add_edge("title_and_category", "search_templates")

# 조건부 엣지 (유사도에 따른 분기)
workflow.add_conditional_edges(
    "search_templates",
    decide_hint_addition,
    {
        "add_hint": "add_hint",
        "no_hint": "generate_template" # 힌트 없으면 바로 생성으로
    }
)

workflow.add_edge("add_hint", "generate_template")
workflow.add_edge("generate_template", END)

# 그래프 컴파일
app = workflow.compile()

# --- 실행 ---
if __name__ == "__main__":
    # 사용자 입력 예시
    user_input = {
        "user_text": "안녕하세요 라이언님, 주문하신 상품이 정상적으로 접수되었습니다. 주문번호는 12345입니다.",
        # "category_main": "주문",
        "category_sub_list": [
            "구매완료", "구매취소", "기타", "뉴스레터", "리마인드", "방문서비스",
            "배송상태", "배송완료", "배송예정", "배송실패", "상품가입", "신청접수",
            "예약상태", "예약완료", "예약취소", "이용도구", "이용안내/공지",
            "요금청구", "주문/예약", "쿠폰발급", "피드백", "피드백 요청", "회원가입"
        ]
    }

    # 파이프라인 실행
    final_state = app.invoke(user_input)

    print("\n--- 최종 생성 결과 ---")
    print(json.dumps(final_state.get("final_result"), indent=2, ensure_ascii=False))

