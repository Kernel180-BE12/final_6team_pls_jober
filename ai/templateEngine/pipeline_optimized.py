# # templateEngine/pipeline_optimized.py
#
# import asyncio
# from typing import Dict, List
# from .state import TemplateGenerationState
# from .nodes_optimized import (
#     parallel_initial_processing_node,
#     search_templates_node,
#     decide_generation_method,
#     generate_with_reference_node,
#     search_public_and_generate_node,
#     finalize_result_node
# )
# from services.openai_service import OpenAIService
# from services.chromadb_service import ChromaDBService
# from langgraph.graph import StateGraph, END
# import logging
#
# logger = logging.getLogger(__name__)
#
# async def create_optimized_pipeline() -> StateGraph:
#     """성능 최적화된 파이프라인 생성"""
#     workflow = StateGraph(TemplateGenerationState)
#
#     # 노드 추가 - 병렬 처리로 단계 수 감소
#     workflow.add_node("parallel_initial", parallel_initial_processing_node)  # 1-3단계 통합
#     workflow.add_node("search_templates", search_templates_node)             # 4단계
#     workflow.add_node("generate_with_reference", generate_with_reference_node)    # 5a단계
#     workflow.add_node("search_public_and_generate", search_public_and_generate_node)  # 5b단계
#     workflow.add_node("finalize_result", finalize_result_node)               # 6단계
#
#     # 엣지 설정
#     workflow.set_entry_point("parallel_initial")
#     workflow.add_edge("parallel_initial", "search_templates")
#
#     # 조건부 분기 - 생성 방법 결정
#     workflow.add_conditional_edges(
#         "search_templates",
#         decide_generation_method,
#         {
#             "with_reference": "generate_with_reference",
#             "search_public": "search_public_and_generate"
#         }
#     )
#
#     workflow.add_edge("generate_with_reference", "finalize_result")
#     workflow.add_edge("search_public_and_generate", "finalize_result")
#     workflow.add_edge("finalize_result", END)
#
#     return workflow.compile()
#
# async def run_optimized_template_generation_pipeline(
#         userMessage: str,
#         category_sub_list: List[str],
#         openai_service: OpenAIService,
#         chromadb_service: ChromaDBService
# ) -> Dict:
#     """최적화된 템플릿 생성 파이프라인 실행"""
#     logger.info("=" * 80)
#     logger.info("⚡ 성능 최적화된 알림톡 템플릿 생성 파이프라인 시작")
#
#     import time
#     start_time = time.time()
#
#     try:
#         app = await create_optimized_pipeline()
#
#         initial_state = {
#             "userMessage": userMessage,
#             "category_sub_list": category_sub_list,
#             "openai_service": openai_service,
#             "chromadb_service": chromadb_service,
#             "message_type_result": None,
#             "category_result": None,
#             "generated_title": None,
#             "similar_templates": [],
#             "max_similarity": 0.0,
#             "public_templates": [],
#             "generation_hint": None,
#             "generated_template": "",
#             "extracted_fields": {},
#             "final_result": {}
#         }
#
#         logger.info("🚀 최적화된 파이프라인 실행 시작")
#         final_state = await app.ainvoke(initial_state)
#
#         elapsed_time = time.time() - start_time
#         logger.info("=" * 80)
#         logger.info(f"⚡ 최적화된 파이프라인 실행 완료! 소요시간: {elapsed_time:.2f}초")
#
#         return final_state.get("final_result", {})
#
#     except Exception as e:
#         elapsed_time = time.time() - start_time
#         logger.error(f"❌ 최적화된 파이프라인 실행 실패 (소요시간: {elapsed_time:.2f}초): {e}", exc_info=True)
#         return {
#             "pipeline_success": False,
#             "error_message": f"파이프라인 실행 중 오류 발생: {str(e)}",
#             "template_text": "",
#             "template_title": "생성 실패",
#             "variables": [],
#             "generation_method": "error",
#             "message_type": None,
#             "category_sub": None,
#             "category_analysis": None,
#             "similarity_score": 0.0,
#             "reference_templates": [],
#             "public_templates": [],
#         }
#
# # 성능 비교를 위한 메트릭 수집 함수
# class PipelineMetrics:
#     def __init__(self):
#         self.reset()
#
#     def reset(self):
#         self.total_time = 0
#         self.step_times = {}
#         self.api_calls = 0
#         self.cache_hits = 0
#
#     def record_step(self, step_name: str, duration: float):
#         self.step_times[step_name] = duration
#         self.total_time += duration
#
#     def record_api_call(self):
#         self.api_calls += 1
#
#     def record_cache_hit(self):
#         self.cache_hits += 1
#
#     def get_summary(self) -> Dict:
#         return {
#             "total_time": round(self.total_time, 2),
#             "step_times": {k: round(v, 2) for k, v in self.step_times.items()},
#             "api_calls": self.api_calls,
#             "cache_hits": self.cache_hits,
#             "cache_hit_rate": round(self.cache_hits / max(self.api_calls, 1) * 100, 1)
#         }
#
# # 글로벌 메트릭 인스턴스
# pipeline_metrics = PipelineMetrics()
#
# async def run_pipeline_with_metrics(
#         userMessage: str,
#         category_sub_list: List[str],
#         openai_service: OpenAIService,
#         chromadb_service: ChromaDBService,
#         use_optimized: bool = True
# ) -> tuple[Dict, Dict]:
#     """메트릭 수집과 함께 파이프라인 실행"""
#     pipeline_metrics.reset()
#
#     if use_optimized:
#         result = await run_optimized_template_generation_pipeline(
#             userMessage, category_sub_list, openai_service, chromadb_service
#         )
#     else:
#         # 기존 파이프라인 (비교용)
#         from .pipeline import run_template_generation_pipeline
#         result = await run_template_generation_pipeline(
#             userMessage, category_sub_list, openai_service, chromadb_service
#         )
#
#     metrics = pipeline_metrics.get_summary()
#     return result, metrics