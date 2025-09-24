# # templateEngine/nodes_optimized.py
#
# import json
# import logging
# import re
# from typing import Dict, Any, Literal, List
# import asyncio
# from functools import lru_cache
#
# from templateEngine.state import TemplateGenerationState
# from templateEngine.prompts.builders_optimized import (
#     TypePromptBuilder,
#     TemplateTitlePromptBuilder,
#     CategoryPromptBuilder,
#     FieldsPromptBuilder,
#     NewCategoryPromptBuilder,
#     ReferenceBasedTemplatePromptBuilder,
#     NewTemplatePromptBuilder
# )
#
# logger = logging.getLogger(__name__)
#
# # 캐시된 프롬프트 빌더들
# @lru_cache(maxsize=128)
# def get_cached_type_builder():
#     return TypePromptBuilder("")
#
# @lru_cache(maxsize=128)
# def get_cached_fields_builder():
#     return FieldsPromptBuilder("")
#
# @lru_cache(maxsize=128)
# def get_cached_title_builder():
#     return TemplateTitlePromptBuilder("")
#
# # --- 병렬 처리된 초기 단계 ---
# async def parallel_initial_processing_node(state: TemplateGenerationState) -> Dict[str, Any]:
#     """1-3단계를 병렬로 처리: 메시지 분류 + 제목/카테고리 생성 + 필드 추출"""
#     logger.info("=" * 60)
#     logger.info("병렬 초기 처리 시작 (1-3단계 통합)")
#
#     try:
#         async def classify_message_type_task():
#             """메시지 유형 분류"""
#             try:
#                 prompt_builder = get_cached_type_builder()
#                 messages = prompt_builder.build_with_message(state["userMessage"])
#                 response = await state["openai_service"].chat_completion(messages)
#                 result = json.loads(response)
#                 logger.info(f"✅ 메시지 유형 분류 완료: {result.get('type')}")
#                 return {"message_type_result": result}
#             except Exception as e:
#                 logger.error(f"❌ 메시지 유형 분류 실패: {e}")
#                 return {"message_type_result": {"type": "BASIC", "explain_type": "분류 실패로 기본값 적용"}}
#
#         async def title_category_task():
#             """제목 생성 및 카테고리 분류"""
#             try:
#                 async def generate_title_subtask():
#                     title_builder = get_cached_title_builder()
#                     messages = title_builder.build_with_message(state["userMessage"])
#                     return await state["openai_service"].chat_completion(messages)
#
#                 async def classify_category_subtask():
#                     logger.info("카테고리 분류 시작...")
#                     category_builder = CategoryPromptBuilder(state["userMessage"], state["category_sub_list"])
#                     messages = category_builder.build()
#                     response = await state["openai_service"].chat_completion(messages)
#                     first_attempt = json.loads(response)
#
#                     CONFIDENCE_THRESHOLD = 70
#                     if first_attempt.get("is_appropriate") and first_attempt.get("confidence", 0) >= CONFIDENCE_THRESHOLD:
#                         logger.info("✅ 기존 카테고리 사용")
#                         return {
#                             "category_sub": first_attempt.get("category_sub"),
#                             "confidence": first_attempt.get("confidence"),
#                             "selection_reason": first_attempt.get("selection_reason"),
#                             "generation_source": "classified_existing"
#                         }
#                     else:
#                         logger.info("⚠️ 신규 카테고리 생성")
#                         new_category_builder = NewCategoryPromptBuilder(state["userMessage"], state["category_sub_list"])
#                         messages = new_category_builder.build()
#                         response = await state["openai_service"].chat_completion(messages)
#                         new_result = json.loads(response)
#                         return {
#                             "category_sub": new_result.get("new_category"),
#                             "confidence": 95,
#                             "selection_reason": f"신규 카테고리 '{new_result.get('new_category')}' 생성",
#                             "generation_source": "created_new"
#                         }
#
#                 title_result, category_result = await asyncio.gather(
#                     generate_title_subtask(), classify_category_subtask()
#                 )
#
#                 logger.info(f"✅ 제목 생성 완료: '{title_result.strip()}'")
#                 logger.info(f"✅ 카테고리 분류 완료: {category_result.get('category_sub')}")
#
#                 return {
#                     "generated_title": title_result.strip(),
#                     "category_result": category_result
#                 }
#             except Exception as e:
#                 logger.error(f"❌ 제목/카테고리 처리 실패: {e}")
#                 return {
#                     "generated_title": "제목 생성 실패",
#                     "category_result": {"category_sub": "기타", "selection_reason": "분류 실패"}
#                 }
#
#         async def extract_fields_task():
#             """변수 필드 추출"""
#             try:
#                 prompt_builder = get_cached_fields_builder()
#                 messages = prompt_builder.build_with_message(state["userMessage"])
#                 response = await state["openai_service"].chat_completion(messages)
#
#                 # JSON 추출 로직
#                 json_match = re.search(r'```json\s*({.*?})\s*```', response, re.DOTALL)
#                 clean_response = json_match.group(1) if json_match else response.strip()
#
#                 if not clean_response:
#                     return {"extracted_fields": {}}
#
#                 result = json.loads(clean_response)
#                 if not isinstance(result, dict):
#                     return {"extracted_fields": {}}
#
#                 logger.info(f"✅ 변수 필드 추출 완료: {len(result)}개")
#                 return {"extracted_fields": result}
#             except Exception as e:
#                 logger.error(f"❌ 변수 필드 추출 실패: {e}")
#                 return {"extracted_fields": {}}
#
#         # 3개 작업을 병렬로 실행
#         type_result, title_category_result, fields_result = await asyncio.gather(
#             classify_message_type_task(),
#             title_category_task(),
#             extract_fields_task()
#         )
#
#         # 결과 통합
#         combined_result = {
#             **type_result,
#             **title_category_result,
#             **fields_result
#         }
#
#         logger.info("✅ 병렬 초기 처리 완료 (1-3단계)")
#         return combined_result
#
#     except Exception as e:
#         logger.error(f"❌ 병렬 초기 처리 실패: {e}", exc_info=True)
#         return {
#             "message_type_result": {"type": "BASIC", "explain_type": "처리 실패"},
#             "generated_title": "제목 생성 실패",
#             "category_result": {"category_sub": "기타", "selection_reason": "분류 실패"},
#             "extracted_fields": {}
#         }
#
# # --- 기존 nodes들 (search_templates_node 등은 그대로 유지) ---
#
# async def search_templates_node(state: TemplateGenerationState) -> Dict[str, Any]:
#     """기존 search_templates_node와 동일"""
#     logger.info("=" * 60)
#     logger.info("4단계: RAG - 스마트 템플릿 검색 시작")
#
#     user_message = state["userMessage"]
#     generated_title = state.get("generated_title", "")
#     category_sub = state.get("category_result", {}).get("category_sub")
#     is_new_category = state.get("category_result", {}).get("generation_source") == "created_new"
#
#     try:
#         all_templates = []
#         max_similarity = 0.0
#
#         if is_new_category:
#             logger.info(f"🆕 신규 카테고리 '{category_sub}' - 공용 템플릿 우선 검색")
#
#             service_keywords = extract_service_keywords(user_message)
#             if service_keywords:
#                 keyword_query = " ".join(service_keywords)
#                 logger.info(f"서비스 키워드 검색: '{keyword_query}'")
#
#                 public_templates, public_max_sim = state["chromadb_service"].search_public_templates(
#                     query_text=keyword_query, top_k=5
#                 )
#                 all_templates.extend(public_templates)
#                 max_similarity = max(max_similarity, public_max_sim)
#
#             if generated_title:
#                 logger.info(f"제목 기반 검색: '{generated_title}'")
#                 title_public_templates, title_public_sim = state["chromadb_service"].search_public_templates(
#                     query_text=generated_title, top_k=3
#                 )
#                 all_templates.extend(title_public_templates)
#                 max_similarity = max(max_similarity, title_public_sim)
#         else:
#             logger.info(f"📁 기존 카테고리 '{category_sub}' - 승인된 템플릿 우선 검색")
#
#             category_templates, category_max_sim = state["chromadb_service"].search_approved_templates(
#                 query_text=user_message, category_sub=category_sub, top_k=5
#             )
#             all_templates.extend(category_templates)
#             max_similarity = max(max_similarity, category_max_sim)
#
#             if generated_title:
#                 title_templates, title_max_sim = state["chromadb_service"].search_approved_templates(
#                     query_text=generated_title, category_sub=None, top_k=3
#                 )
#                 all_templates.extend(title_templates)
#                 max_similarity = max(max_similarity, title_max_sim)
#
#         unique_templates = remove_duplicate_templates(all_templates)
#         sorted_templates = sorted(unique_templates, key=lambda x: x.get('similarity', 0), reverse=True)
#         final_templates = sorted_templates[:5]
#
#         logger.info(f"✅ 템플릿 검색 완료: {len(final_templates)}개, 최대 유사도: {max_similarity:.3f}")
#         return {"similar_templates": final_templates, "max_similarity": max_similarity}
#
#     except Exception as e:
#         logger.error(f"❌ 템플릿 검색 실패: {e}", exc_info=True)
#         return {"similar_templates": [], "max_similarity": 0.0}
#
# # 유틸리티 함수들 (기존과 동일)
# def extract_service_keywords(message: str) -> List[str]:
#     service_patterns = {
#         'A/S': ['A/S', 'AS', '애프터서비스', '수리', '점검'],
#         '서비스': ['서비스', '점검', '관리', '유지보수'],
#         '안내': ['안내', '알림', '공지', '예고'],
#         '고객': ['고객', '회원', '사용자'],
#         '상담': ['상담', '문의', '연락'],
#         '예약': ['예약', '접수', '신청']
#     }
#
#     found_keywords = []
#     message_lower = message.lower()
#
#     for category, keywords in service_patterns.items():
#         for keyword in keywords:
#             if keyword.lower() in message_lower or keyword in message:
#                 found_keywords.append(keyword)
#                 break
#
#     if '장수돌침대' in message:
#         found_keywords.append('장수돌침대')
#     if '침대' in message:
#         found_keywords.append('침대')
#
#     return list(set(found_keywords))
#
# def remove_duplicate_templates(templates: List[Dict]) -> List[Dict]:
#     seen_codes = set()
#     unique_templates = []
#     for template in templates:
#         code = template.get('template_code', template.get('id', ''))
#         if code not in seen_codes:
#             seen_codes.add(code)
#             unique_templates.append(template)
#     return unique_templates
#
# def decide_generation_method(state: TemplateGenerationState) -> Literal["with_reference", "search_public"]:
#     logger.info("=" * 60)
#     logger.info("5단계: 생성 방법 결정")
#     SIMILARITY_THRESHOLD = 0.75
#     if state.get("max_similarity", 0.0) >= SIMILARITY_THRESHOLD:
#         logger.info(f"✅ 참고 템플릿 기반 생성 (유사도: {state['max_similarity']:.3f})")
#         return "with_reference"
#     else:
#         logger.info(f"⚠️ 신규 생성 (유사도: {state['max_similarity']:.3f})")
#         return "search_public"
#
# async def generate_with_reference_node(state: TemplateGenerationState) -> Dict[str, Any]:
#     logger.info("=" * 60)
#     logger.info("6a단계: 참고 템플릿 기반 생성")
#     try:
#         prompt_builder = ReferenceBasedTemplatePromptBuilder(
#             userMessage=state["userMessage"],
#             reference_templates=state["similar_templates"],
#             extracted_fields=state["extracted_fields"]
#         )
#         messages = prompt_builder.build()
#         template = await state["openai_service"].chat_completion(messages)
#         logger.info("✅ 참고 템플릿 기반 생성 완료")
#         return {"generated_template": template, "generation_hint": "reference_based"}
#     except Exception as e:
#         logger.error(f"❌ 참고 템플릿 기반 생성 실패: {e}", exc_info=True)
#         return {"generated_template": "템플릿 생성 중 오류 발생", "generation_hint": "error"}
#
# async def search_public_and_generate_node(state: TemplateGenerationState) -> Dict[str, Any]:
#     logger.info("=" * 60)
#     logger.info("6b단계: 신규 생성")
#     try:
#         public_templates = state["chromadb_service"].search_public_templates(
#             query_text=state["userMessage"], top_k=3
#         )
#         hint = "public_templates_based" if public_templates else "from_scratch"
#
#         prompt_builder = NewTemplatePromptBuilder(
#             userMessage=state["userMessage"],
#             extracted_fields=state["extracted_fields"],
#             public_templates=public_templates
#         )
#         messages = prompt_builder.build()
#         template = await state["openai_service"].chat_completion(messages)
#         logger.info(f"✅ 신규 생성 완료 (방식: {hint})")
#         return {
#             "generated_template": template,
#             "generation_hint": hint,
#             "public_templates": public_templates
#         }
#     except Exception as e:
#         logger.error(f"❌ 신규 생성 실패: {e}", exc_info=True)
#         return {
#             "generated_template": "템플릿 생성 중 오류 발생",
#             "generation_hint": "error",
#             "public_templates": []
#         }
#
# def finalize_result_node(state: TemplateGenerationState) -> Dict[str, Any]:
#     logger.info("=" * 60)
#     logger.info("7단계: 최종 결과 정리")
#
#     variables = extract_variables_from_template(state.get("generated_template", ""))
#     final_result = {
#         "pipeline_success": True,
#         "error_message": None,
#         "template_text": state.get("generated_template", ""),
#         "template_title": state.get("generated_title", "제목 없음"),
#         "variables": variables,
#         "generation_method": state.get("generation_hint", "unknown"),
#         "message_type": state.get("message_type_result", {}).get("type"),
#         "category_sub": state.get("category_result", {}).get("category_sub"),
#         "category_analysis": state.get("category_result"),
#         "similarity_score": state.get("max_similarity", 0.0),
#         "reference_templates": state.get("similar_templates", []),
#         "public_templates": state.get("public_templates", []),
#     }
#
#     logger.info("✅ 파이프라인 최종 완료")
#     logger.info("-" * 60)
#     logger.info(">>> 최종 생성된 템플릿 <<<")
#     logger.info(final_result.get("template_text"))
#     logger.info("-" * 60)
#
#     return {"final_result": final_result}
#
# def extract_variables_from_template(template_text: str) -> List[str]:
#     if not template_text:
#         return []
#     return sorted(list(set(re.findall(r'#\{([^}]+)\}', template_text))))