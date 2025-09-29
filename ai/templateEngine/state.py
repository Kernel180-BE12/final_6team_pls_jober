# state.py
from typing import TypedDict, List, Literal, Optional, Dict, Any
from services.chromadb_service import ChromaDBService
from services.openai_service import OpenAIService
class TemplateGenerationState(TypedDict):
    # 입력
    userMessage: str
    category_sub_list: List[str]

    # 서비스 객체
    openai_service: OpenAIService
    chromadb_service: ChromaDBService

    # 처리 결과
    suitability_check_result: Optional[Dict]
    message_type_result: Optional[Dict]
    category_result: Optional[Dict]
    generated_title: Optional[str]
    similar_templates: List[Dict]
    max_similarity: float
    public_templates: List[Dict]
    generation_hint: Optional[str]
    generated_template: str
    extracted_fields: Optional[Dict[str, Any]]  # 👇 변수 추출 결과를 저장할 필드 추가
    # 최종 결과
    final_result: Dict