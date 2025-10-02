# templateEngine/nodes.py

import json
from templateEngine.prompts.message_analyzer_prompts import UnsuitableMessageError
import logging
import re
from typing import Dict, Any, Literal, List
import asyncio
from services.category_service import CategoryService

from templateEngine.state import TemplateGenerationState
from templateEngine.prompts.builders import (
    SuitabilityCheckPromptBuilder,
    TypePromptBuilder,
    TemplateTitlePromptBuilder,
    CategoryPromptBuilder,
    NewCategoryPromptBuilder,
    TemplateWriterBuilder,  # [수정] 템플릿 생성 전용 빌더
    FieldsPromptBuilder,      # [수정] 필드/블록 추출 전용 빌더
    IndividualVariableExtractor,
    ReferenceBasedTemplatePromptBuilder # 참고 기반 생성을 위해 유지
)

logger = logging.getLogger(__name__)

# --- [신규] 파이프라인 노드들 ---

async def initial_analysis_node(state: TemplateGenerationState) -> Dict[str, Any]:
    """
    [1단계] 타입, 제목, 카테고리 분류만 병렬 처리하는 노드
    """
    logger.info("=" * 60)
    logger.info("1단계: 초기 분석 (타입, 제목, 카테고리) 시작")

    async def classify_type_task():
        try:
            prompt_builder = TypePromptBuilder(state["userMessage"])
            messages = prompt_builder.build()
            return json.loads(await state["openai_service"].chat_completion(messages))
        except Exception as e:
            logger.error(f"❌ (병렬) 메시지 유형 분류 실패: {e}")
            return {"type": "BASIC", "explain_type": "분류 실패"}

    async def generate_title_task():
        try:
            prompt_builder = TemplateTitlePromptBuilder(state["userMessage"])
            messages = prompt_builder.build()
            title_result = await state["openai_service"].chat_completion(messages)
            # 따옴표 제거
            cleaned_title = title_result.strip().strip('"').strip("'")
            logger.info(f"✅ 제목 생성 성공: {cleaned_title}")
            return cleaned_title
        except Exception as e:
            logger.error(f"❌ (병렬) 제목 생성 실패: {e}")
            return "제목 생성 실패"

    async def classify_category_task():
        try:
            category_service = CategoryService(state["db_session"])
            current_categories = await category_service.get_all_categories()

            category_builder = CategoryPromptBuilder(state["userMessage"], current_categories)
            messages = category_builder.build()
            result = json.loads(await state["openai_service"].chat_completion(messages))

            CONFIDENCE_THRESHOLD = 70
            if result.get("is_appropriate") and result.get("confidence", 0) >= CONFIDENCE_THRESHOLD:
                return {**result, "generation_source": "classified_existing"}
            else:
                new_category_builder = NewCategoryPromptBuilder(state["userMessage"], current_categories)
                messages = new_category_builder.build()
                new_category_result = json.loads(await state["openai_service"].chat_completion(messages))
                new_category_name = new_category_result.get("new_category")
                await category_service.create_category_if_not_exists(new_category_name)
                
                return {
                    "category_sub": new_category_name, "confidence": 95,
                    "selection_reason": f"신규 카테고리 '{new_category_name}' 생성",
                    "generation_source": "created_new"
                }
        except Exception as e:
            logger.error(f"❌ (병렬) 카테고리 분류 실패: {e}")
            return {"category_sub": "기타", "selection_reason": "분류 실패"}

    type_res, title_res, category_res = await asyncio.gather(
        classify_type_task(), generate_title_task(), classify_category_task()
    )

    logger.info("✅ 초기 분석 완료")
    return {
        "message_type_result": type_res,
        "generated_title": title_res.strip(),
        "category_result": category_res,
    }


async def generate_template_node(state: TemplateGenerationState) -> Dict[str, Any]:
    """
    [2단계] '변수 없는' 간결한 템플릿 텍스트를 생성하는 노드
    """
    logger.info("=" * 60)
    logger.info("2단계: 간결한 템플릿 생성 시작")
    try:
        # RAG 검색을 먼저 수행하여 참고 템플릿을 가져올 수 있습니다 (선택적)
        # 여기서는 단순화된 '신규 생성' 로직만 구현합니다.

        # TemplateWriterBuilder를 사용하여 간결한 텍스트 생성
        prompt_builder = TemplateWriterBuilder(state["userMessage"])
        messages = prompt_builder.build()
        generated_text = await state["openai_service"].chat_completion(messages)

        logger.info("✅ 간결한 템플릿 생성 성공")
        return {"generated_template": generated_text}

    except Exception as e:
        logger.error(f"❌ 간결한 템플릿 생성 실패: {e}")
        return {"generated_template": "템플릿 생성에 실패했습니다."}

async def extract_blocks_node(state: TemplateGenerationState) -> Dict[str, Any]:
    """
    [최종 수정] '의미 블록'과 '개별 변수'를 두 단계로 나누어 추출하고 결과를 병합합니다.
    """
    logger.info("=" * 60)
    logger.info("3단계: 의미 블록 및 개별 변수 추출 시작")


    generated_template = state.get("generated_template")
    if not generated_template or "실패" in generated_template:
        logger.warning("⚠️ 템플릿 생성이 실패하여 추출을 건너뜁니다.")
        return {"extracted_fields": {}}

    try:
        # --- 1단계: '의미 블록' 추출 ---
        logger.info("  - (3-1) 의미 블록 추출 중...")
        block_builder = FieldsPromptBuilder(generated_template)
        block_messages = block_builder.build()
        block_response = await state["openai_service"].chat_completion(block_messages)
        block_fields = json.loads(block_response)
        logger.info(f"  ✅ 의미 블록 추출 성공: {list(block_fields.keys())}")

        # --- 2단계: '개별 변수' 추출 ---
        logger.info("  - (3-2) 개별 변수 추출 중...")
        variable_builder = IndividualVariableExtractor(generated_template)
        variable_messages = variable_builder.build()
        variable_response = await state["openai_service"].chat_completion(variable_messages)
        individual_variables = json.loads(variable_response)
        logger.info(f"  ✅ 개별 변수 추출 성공: {list(individual_variables.keys())}")

        # --- 3단계: 두 결과 병합 ---
        # individual_variables를 먼저 두고, block_fields로 덮어씁니다.
        # 이렇게 하면, 만약 중복된 Key가 있더라도 더 큰 범위인 '의미 블록'의 값이 유지됩니다.
        final_extracted_fields = {**individual_variables, **block_fields}

        # '고객님' -> '고객' 후처리 로직은 여전히 유효합니다.
        if "customer_title" in final_extracted_fields:
            original_title = final_extracted_fields["customer_title"]
            if original_title.endswith("님") and len(original_title) > 1:
                final_extracted_fields["customer_title"] = original_title[:-1]
                logger.info("  - (후처리) 'customer_title' 교정 완료.")

        logger.info(f"✅ 최종 필드 병합 완료. 총 {len(final_extracted_fields)}개의 변수/블록 추출.")
        return {"extracted_fields": final_extracted_fields}
    except Exception as e:
        logger.error(f"❌ 블록/변수 추출 과정에서 오류 발생: {e}")
        return {"extracted_fields": {}}


# async def extract_blocks_node(state: TemplateGenerationState) -> Dict[str, Any]:
#     """
#     [3단계] 생성된 템플릿에서 의미 블록과 변수를 추출하고, '후처리'로 결과를 교정합니다.
#     """
#     logger.info("=" * 60)
#     logger.info("3단계: 의미 블록 추출 시작")
#     try:
#         generated_template = state.get("generated_template")
#         if not generated_template or "실패" in generated_template:
#             logger.warning("⚠️ 이전 단계에서 템플릿 생성이 실패하여 블록 추출을 건너뜁니다.")
#             return {"extracted_fields": {}}
#
#         # 1. AI에게 평소처럼 추출을 요청합니다.
#         prompt_builder = FieldsPromptBuilder(generated_template)
#         messages = prompt_builder.build()
#         response = await state["openai_service"].chat_completion(messages)
#         extracted_fields = json.loads(response)
#
#         logger.info(f"✅ (1차) AI의 의미 블록 추출 성공: {len(extracted_fields)}개")
#         logger.debug(f"  - AI 원본 추출 결과: {extracted_fields}")
#
#         # --- [핵심 수정] 후처리(Post-processing) 로직 ---
#         # 2. AI가 추출한 결과에서 'customer_title' 값을 직접 확인하고 교정합니다.
#         if "customer_title" in extracted_fields:
#             original_title = extracted_fields["customer_title"]
#             # 만약 값이 '고객님', '회원님' 등 '님'으로 끝나면, '님'을 제거합니다.
#             if original_title.endswith("님") and len(original_title) > 1:
#                 corrected_title = original_title[:-1] # 마지막 글자('님')를 제거
#                 extracted_fields["customer_title"] = corrected_title
#                 logger.info(f"✅ (2차) 후처리 교정 완료: 'customer_title'을 '{original_title}'에서 '{corrected_title}'(으)로 수정했습니다.")
#         # ----------------------------------------------------
#
#         return {"extracted_fields": extracted_fields}
#     except Exception as e:
#         logger.error(f"❌ 의미 블록 추출 실패: {e}")
#         return {"extracted_fields": {}}


# def finalize_node(state: TemplateGenerationState) -> Dict[str, Any]:
#     """
#     [4단계] 추출된 블록을 최종 템플릿에 변수 형태로 삽입하고 결과를 정리하는 노드
#     """
#     logger.info("=" * 60)
#     logger.info("4단계: 최종 결과 조립 시작")
#
#     template_text = state.get("generated_template", "")
#     extracted_fields = state.get("extracted_fields", {})
#
#     # 최종 템플릿에 변수 구문(#{...} 또는 {{...}})을 삽입
#     final_template_with_vars = template_text
#     for key, value in extracted_fields.items():
#         # 값에 특수문자가 있을 경우를 대비해 정규식 escape 처리
#         escaped_value = re.escape(value)
#
#         # 의미 블록은 {{key}} 형태로, 개별 변수는 #{key} 형태로 치환
#         if key in ["main_content", "sub_content", "closing_word", "contact_info"]:
#             final_template_with_vars = re.sub(escaped_value, f"{{{{{key}}}}}", final_template_with_vars, count=1)
#         else:
#             final_template_with_vars = re.sub(escaped_value, f"#{{{{{key}}}}}", final_template_with_vars, count=1)
#
#     final_result = {
#         "pipeline_success": True,
#         "template_text": final_template_with_vars,
#         "variable_mapping": extracted_fields,
#         "template_title": state.get("generated_title", "제목 없음"),
#         "message_type": state.get("message_type_result", {}).get("type"),
#         "category_sub": state.get("category_result", {}).get("category_sub"),
#         # ... 기타 필요한 결과들
#     }
#
#     logger.info("✅ 최종 결과 조립 완료.")
#     logger.info("-" * 60)
#     logger.info(">>> 최종 생성된 템플릿 (변수 포함) <<<")
#     logger.info(final_result.get("template_text"))
#     logger.info(">>> 최종 추출된 변수 매핑 <<<")
#     logger.info(final_result.get("variable_mapping"))
#     logger.info("-" * 60)
#
#     return {"final_result": final_result}


import re

def finalize_node(state: TemplateGenerationState) -> Dict[str, Any]:
    """
    [최종 완성] 모든 변수를 안전한 단일 구문 '{{...}}'으로 통일하여 치환합니다.
    """
    logger.info("=" * 60)
    logger.info("4단계: 최종 결과 조립 시작")

    base_template_text = state.get("generated_template", "")
    extracted_fields = state.get("extracted_fields", {})

    if not base_template_text or not extracted_fields:
        # ... (기존 예외 처리 로직) ...
        # 이 부분은 이전 답변의 코드를 그대로 사용하시면 됩니다.
        pass

    # --- [핵심 로직] re.sub 콜백을 이용한 안전한 동시 치환 ---

    value_to_key_map = {str(v): k for k, v in sorted(extracted_fields.items(), key=lambda item: len(str(item[1])), reverse=True)}

    sorted_values = sorted(value_to_key_map.keys(), key=len, reverse=True)
    valid_sorted_values = [re.escape(v) for v in sorted_values if v]

    if not valid_sorted_values:
        # ... (기존 예외 처리 로직) ...
        pass

    pattern = re.compile("|".join(valid_sorted_values))

    # 3. 치환 로직을 수행할 콜백 함수를 정의합니다.
    def create_variable_syntax(match):
        """
        [최종 수정] 모든 변수를 안전한 '{{...}}' 형태로 통일하여 반환합니다.
        """
        matched_value = match.group(0)
        # key = value_to_key_map.get(matched_value) # 이제 key를 찾을 필요도 없습니다.

        # 모든 매칭된 값을 예외 없이 '{{...}}' 형태로 감쌉니다.
        return f"{{{{{matched_value}}}}}"

    # 4. re.sub를 단 한 번만 호출하여 모든 치환을 안전하게 수행합니다.
    final_template_with_vars = pattern.sub(create_variable_syntax, base_template_text)

    final_result = {
        "pipeline_success": True,
        "template_text": final_template_with_vars,
        "variable_mapping": extracted_fields,
        "variables": list(extracted_fields.keys()),
        "template_title": state.get("generated_title", "제목 없음"),
        "message_type": state.get("message_type_result", {}).get("type"),
        "category_sub": state.get("category_result", {}).get("category_sub"),
    }

    logger.info("✅ 최종 결과 조립 완료.")
    logger.info("-" * 60)
    logger.info(">>> 최종 생성된 템플릿 (Value가 변수화된 버전) <<<")
    logger.info(final_result.get("template_text"))
    logger.info(">>> 최종 추출된 변수 매핑 (Key-Value) <<<")
    logger.info(final_result.get("variable_mapping"))
    logger.info("-" * 60)

    return {"final_result": final_result}


