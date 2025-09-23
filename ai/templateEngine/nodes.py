# templateEngine/nodes.py

import json
import logging
import re
from typing import Dict, Any, Literal, List
import asyncio

from templateEngine.state import TemplateGenerationState
from templateEngine.prompts.builders import (
    TypePromptBuilder,
    TemplateTitlePromptBuilder,
    CategoryPromptBuilder,
    FieldsPromptBuilder,
    NewCategoryPromptBuilder,
    ReferenceBasedTemplatePromptBuilder,
    NewTemplatePromptBuilder
)

logger = logging.getLogger(__name__)

# --- 노드 함수들 ---

async def classify_message_type_node(state: TemplateGenerationState) -> Dict[str, Any]:
    logger.info("=" * 60)
    logger.info("1단계: 메시지 유형 분류 시작")
    try:
        prompt_builder = TypePromptBuilder(state["userMessage"])
        messages = prompt_builder.build()
        openai_service = state["openai_service"]
        response = await openai_service.chat_completion(messages)
        result = json.loads(response)
        logger.info(f"✅ 메시지 유형 분류 성공: {result.get('type')}")
        return {"message_type_result": result}
    except Exception as e:
        logger.error(f"❌ 메시지 유형 분류 실패: {e}", exc_info=True)
        return {"message_type_result": {"type": "BASIC", "explain_type": "분류 실패로 기본값 적용"}}

async def parallel_title_category_node(state: TemplateGenerationState) -> Dict[str, Any]:
    logger.info("=" * 60)
    logger.info("2단계: 제목 생성 및 카테고리 분류 (병렬) 시작")
    try:
        async def generate_title_task():
            title_builder = TemplateTitlePromptBuilder(state["userMessage"])
            messages = title_builder.build()
            return await state["openai_service"].chat_completion(messages)

        async def classify_or_create_category_task():
            logger.info("카테고리 분류/생성 작업 시작")
            logger.info("1차: 기존 카테고리 내에서 분류 시도...")
            category_builder = CategoryPromptBuilder(state["userMessage"], state["category_sub_list"])
            messages = category_builder.build()
            response = await state["openai_service"].chat_completion(messages)
            first_attempt_result = json.loads(response)
            logger.info(f"기존 카테고리 사용 1차 시도 결과: 적합성={first_attempt_result.get('is_appropriate')}, 신뢰도={first_attempt_result.get('confidence')}%")

            CONFIDENCE_THRESHOLD = 70
            if first_attempt_result.get("is_appropriate") and first_attempt_result.get("confidence", 0) >= CONFIDENCE_THRESHOLD:
                logger.info("✅ 1차 분류 성공. 기존 카테고리를 사용합니다.")
                return {
                    "category_sub": first_attempt_result.get("category_sub"), "confidence": first_attempt_result.get("confidence"),
                    "selection_reason": first_attempt_result.get("selection_reason"), "generation_source": "classified_existing"
                }
            else:
                logger.warning("⚠️ 1차 분류 실패 또는 신뢰도 낮음. 신규 카테고리 생성을 시도합니다.")
                logger.info(f"사유: {first_attempt_result.get('selection_reason')}")
                new_category_builder = NewCategoryPromptBuilder(state["userMessage"], state["category_sub_list"])
                messages = new_category_builder.build()
                response = await state["openai_service"].chat_completion(messages)
                new_category_result = json.loads(response)
                new_category = new_category_result.get("new_category")
                logger.info(f"✨ 생성된 신규 카테고리: '{new_category}'")
                return {
                    "category_sub": new_category, "confidence": 95,
                    "selection_reason": f"기존 리스트에 적합한 카테고리가 없어 '{new_category}'를 새로 생성함.", "generation_source": "created_new"
                }

        title_result, category_result = await asyncio.gather(generate_title_task(), classify_or_create_category_task())

        logger.info("병렬 작업 완료")
        logger.info(f"✅ 제목 생성 성공: '{title_result.strip()}'")
        logger.info(f"✅ 카테고리 분류 성공: {category_result.get('category_sub')}")

        return {"generated_title": title_result.strip(), "category_result": category_result}
    except Exception as e:
        logger.error(f"❌ 병렬 처리 실패: {e}", exc_info=True)
        return {"generated_title": "제목 생성 실패", "category_result": {"category_sub": "기타", "selection_reason": "분류 실패"}}


async def search_templates_node(state: TemplateGenerationState) -> Dict[str, Any]:
    logger.info("=" * 60)
    logger.info("3단계: RAG - 스마트 템플릿 검색 시작")

    user_message = state["userMessage"]
    generated_title = state.get("title_result", {}).get("title", "")
    category_sub = state.get("category_result", {}).get("category_sub")
    is_new_category = state.get("category_result", {}).get("is_new_category", False)

    try:
        all_templates = []
        max_similarity = 0.0

        # 신규 카테고리 생성 시 공용 템플릿 우선 검색
        if is_new_category:
            logger.info(f"🆕 신규 카테고리 '{category_sub}' 감지 - 공용 템플릿 우선 검색")

            # 1. 서비스 키워드로 공용 템플릿 검색
            service_keywords = extract_service_keywords(user_message)
            if service_keywords:
                keyword_query = " ".join(service_keywords)
                logger.info(f"1단계: 서비스 키워드 '{keyword_query}'로 공용 템플릿 검색")

                public_templates, public_max_sim = state["chromadb_service"].search_public_templates(
                    query_text=keyword_query,
                    top_k=5
                )
                all_templates.extend(public_templates)
                max_similarity = max(max_similarity, public_max_sim)
                logger.info(f"   공용 템플릿 검색 결과: {len(public_templates)}개, 최대 유사도: {public_max_sim:.3f}")

            # 2. 생성된 제목으로 공용 템플릿 검색
            if generated_title:
                logger.info(f"2단계: 생성 제목 '{generated_title}'로 공용 템플릿 검색")
                title_public_templates, title_public_sim = state["chromadb_service"].search_public_templates(
                    query_text=generated_title,
                    top_k=3
                )
                all_templates.extend(title_public_templates)
                max_similarity = max(max_similarity, title_public_sim)
                logger.info(f"   제목 기반 공용 템플릿 검색 결과: {len(title_public_templates)}개, 최대 유사도: {title_public_sim:.3f}")

        else:
            # 기존 카테고리 매칭 시 승인된 템플릿 우선 검색
            logger.info(f"📁 기존 카테고리 '{category_sub}' 매칭 - 승인된 템플릿 우선 검색")

            # 1. 해당 카테고리 내 승인된 템플릿 검색
            logger.info(f"1단계: 카테고리 '{category_sub}' 내에서 승인된 템플릿 검색")
            category_templates, category_max_sim = state["chromadb_service"].search_approved_templates(
                query_text=user_message,
                category_sub=category_sub,
                top_k=5
            )
            all_templates.extend(category_templates)
            max_similarity = max(max_similarity, category_max_sim)
            logger.info(f"   카테고리 내 검색 결과: {len(category_templates)}개, 최대 유사도: {category_max_sim:.3f}")

            # 2. 제목으로 전체 승인된 템플릿 검색 (보완)
            if generated_title:
                logger.info(f"2단계: 생성 제목 '{generated_title}'로 전체 승인된 템플릿 검색")
                title_templates, title_max_sim = state["chromadb_service"].search_approved_templates(
                    query_text=generated_title,
                    category_sub=None,  # 카테고리 제한 없음
                    top_k=3
                )
                all_templates.extend(title_templates)
                max_similarity = max(max_similarity, title_max_sim)
                logger.info(f"   제목 기반 승인된 템플릿 검색 결과: {len(title_templates)}개, 최대 유사도: {title_max_sim:.3f}")

        # 3. 중복 제거 및 유사도 기준 정렬
        unique_templates = remove_duplicate_templates(all_templates)
        sorted_templates = sorted(unique_templates, key=lambda x: x.get('similarity', 0), reverse=True)
        final_templates = sorted_templates[:5]  # 최대 5개

        template_source = "공용 템플릿" if is_new_category else "승인된 템플릿"
        logger.info(f"✅ 스마트 검색 완료 ({template_source} 우선). 총 {len(final_templates)}개 템플릿, 최대 유사도: {max_similarity:.3f}")

        # 4. 검색 결과 상세 로깅
        for i, template in enumerate(final_templates):
            title = template.get('title', template.get('template_name', '제목 없음'))
            similarity = template.get('similarity', 0)
            category = template.get('category_sub', template.get('category', '카테고리 없음'))
            template_type = "공용" if template.get('type') == 'public_template' else "승인"
            logger.info(f"   {i+1}. [{template_type}][{category}] {title} (유사도: {similarity:.3f})")

        return {"similar_templates": final_templates, "max_similarity": max_similarity}

    except Exception as e:
        logger.error(f"❌ 유사 템플릿 검색 실패: {e}", exc_info=True)
        return {"similar_templates": [], "max_similarity": 0.0}

def extract_service_keywords(message: str) -> List[str]:
    """서비스 관련 핵심 키워드 추출"""
    service_patterns = {
        'A/S': ['A/S', 'AS', '애프터서비스', '수리', '점검', '사전점검'],
        '서비스': ['서비스', '점검', '관리', '유지보수'],
        '안내': ['안내', '알림', '공지', '예고'],
        '고객': ['고객', '회원', '사용자'],
        '상담': ['상담', '문의', '연락'],
        '예약': ['예약', '접수', '신청']
    }

    found_keywords = []
    message_lower = message.lower()

    for category, keywords in service_patterns.items():
        for keyword in keywords:
            if keyword.lower() in message_lower or keyword in message:
                found_keywords.append(keyword)
                break  # 카테고리당 하나씩만

    # 브랜드명, 제품명 추출
    if '장수돌침대' in message:
        found_keywords.append('장수돌침대')
    if '침대' in message:
        found_keywords.append('침대')

    return list(set(found_keywords))


def extract_keywords_from_message(message: str) -> List[str]:
    """메시지에서 핵심 키워드 추출"""
    import re

    # 브랜드명, 행사명, 장소명 등 고유명사 우선 추출
    patterns = [
        r'[가-힣]{2,8}(?:행사|이벤트|세일|할인)',  # 행사 관련
        r'[가-힣]{2,10}(?:백화점|마트|몰|점)',    # 장소 관련
        r'[가-힣]{2,8}(?:브랜드|제품)',           # 브랜드 관련
        r'\d{1,3}%(?:~\d{1,3}%)?',               # 할인율
        r'\d{4}년\s*\d{1,2}월\s*\d{1,2}일',     # 날짜
    ]

    keywords = []
    for pattern in patterns:
        matches = re.findall(pattern, message)
        keywords.extend(matches)

    # 일반적인 명사도 추출 (간단한 방식)
    common_keywords = ['할인', '행사', '이벤트', '세일', '브랜드', '상품', '고객', '혜택']
    for keyword in common_keywords:
        if keyword in message:
            keywords.append(keyword)

    return list(set(keywords))  # 중복 제거

def remove_duplicate_templates(templates: List[Dict]) -> List[Dict]:
    """중복 템플릿 제거 (템플릿 코드 기준)"""
    seen_codes = set()
    unique_templates = []

    for template in templates:
        code = template.get('template_code', template.get('id', ''))
        if code not in seen_codes:
            seen_codes.add(code)
            unique_templates.append(template)

    return unique_templates

async def extract_fields_node(state: TemplateGenerationState) -> Dict[str, Any]:
    logger.info("=" * 60)
    logger.info("✨ 추가 단계: 변수 필드 추출 시작")
    response = "" # response 변수 초기화
    clean_response = "" # clean_response 변수 초기화
    try:
        # state에서 userMessage와 openai_service를 안전하게 가져옵니다.
        user_message = state.get("userMessage")
        openai_service = state.get("openai_service")

        if not user_message:
            logger.error("❌ 'userMessage'가 state에 없습니다.")
            return {"extracted_fields": {}}
        if not openai_service:
            logger.error("❌ 'openai_service'가 state에 없습니다.")
            return {"extracted_fields": {}}

        prompt_builder = FieldsPromptBuilder(state["userMessage"])
        messages = prompt_builder.build()
        response = await state["openai_service"].chat_completion(messages)

        logger.debug(f"OpenAI API 원본 응답: {response}")

        # 정규 표현식을 사용하여 가장 바깥쪽 JSON 객체 추출
        # ```json ... ``` 블록 또는 단일 JSON 객체 모두 처리
        json_match = re.search(r'```json\s*({.*?})\s*```', response, re.DOTALL)
        if json_match:
            clean_response = json_match.group(1)
            logger.debug(f"정규식으로 추출된 JSON 블록: {clean_response}")
        else:
            # ```json 블록이 없는 경우, 전체 응답에서 JSON 객체 시도
            clean_response = response.strip()
            logger.debug(f"정규식 매칭 실패, 전체 응답 시도: {clean_response}")

        if not clean_response:
            logger.warning("⚠️ 변수 추출 결과가 비어있습니다. 빈 객체를 반환합니다.")
            return {"extracted_fields": {}}

        result = json.loads(clean_response)

        # 추출된 필드에 대한 간단한 유효성 검사 (선택 사항)
        if not isinstance(result, dict):
            logger.warning(f"⚠️ 추출된 결과가 딕셔너리 형식이 아닙니다: {result}. 빈 객체를 반환합니다.")
            return {"extracted_fields": {}}

        logger.info(f"✅ 추출된 변수 필드: {result}")
        return {"extracted_fields": result}
    except json.JSONDecodeError as e:
        logger.error(f"❌ 변수 필드 추출 JSON 파싱 실패: {e}", exc_info=True)
        logger.error(f"   파싱 실패한 원본 응답: {response}")
        logger.error(f"   파싱 시도한 클린 응답: {clean_response if 'clean_response' in locals() else 'N/A'}")
        return {"extracted_fields": {}}
    except Exception as e:
        logger.error(f"❌ 변수 필드 추출 실패: {e}", exc_info=True)
        logger.error(f"   원본 응답: {response}")
        return {"extracted_fields": {}}

# 필드 잘 뽑아오는 지 테스트 위한 예시 사용법:
async def test_extraction():
    state = TemplateGenerationState({
        "userMessage": """[롯데광주 오일릴리 - 이월행사]

    ■ 테   마 : 오일릴리 이월행사

    ■ 기   간 : 2021년 10월 06일(수) ~ 10월 10일(일),5일간

    ■ 할인율 :  40%~60% + 추가10%

    ■ 장   소 : 롯데백화점 광주점 9층 행사장

    ■ 문   의 : 062-221-1440

    사랑스러운 컬러와 패턴이 가득한 네덜란드 브랜드 오일릴리가
    롯데백화점 광주점에서 특별한 행사를 진행합니다.
    오일릴리의 다양한 상품들을 할인된 가격에 만나보세요!

    오일릴리 공식 수입원 GMI의 발송 메일입니다.
    """
    })
    result = await extract_fields_node(state)
    print(f"최종 결과: {result}")

import asyncio

if __name__ == "__main__":
    asyncio.run(test_extraction())

def decide_generation_method(state: TemplateGenerationState) -> Literal["with_reference", "search_public"]:
    logger.info("=" * 60)
    logger.info("4단계: 생성 방법 결정")
    SIMILARITY_THRESHOLD = 0.75
    if state.get("max_similarity", 0.0) >= SIMILARITY_THRESHOLD:
        logger.info(f"✅ 결정: 유사도({state['max_similarity']:.3f})가 기준 이상. [참고 템플릿 기반 생성]으로 진행합니다.")
        return "with_reference"
    else:
        logger.info(f"⚠️ 결정: 유사도({state['max_similarity']:.3f})가 기준 미만. [신규 생성]으로 진행합니다.")
        return "search_public"

async def generate_with_reference_node(state: TemplateGenerationState) -> Dict[str, Any]:
    logger.info("=" * 60)
    logger.info("5a단계: 참고 템플릿 기반 생성 시작")
    try:
        prompt_builder = ReferenceBasedTemplatePromptBuilder(
            userMessage=state["userMessage"],
            reference_templates=state["similar_templates"],
            extracted_fields=state["extracted_fields"]
        )
        messages = prompt_builder.build()
        template = await state["openai_service"].chat_completion(messages)
        logger.info("✅ 참고 템플릿 기반 생성 성공")
        return {"generated_template": template, "generation_hint": "reference_based"}
    except Exception as e:
        logger.error(f"❌ 참고 템플릿 기반 생성 실패: {e}", exc_info=True)
        return {"generated_template": "템플릿 생성 중 오류 발생", "generation_hint": "error"}

async def search_public_and_generate_node(state: TemplateGenerationState) -> Dict[str, Any]:
    logger.info("=" * 60)
    logger.info("5b단계: 신규 생성 시작")
    try:
        pulblic_templates = state["chromadb_service"].search_public_templates(
            query_text=state["userMessage"], top_k=3
        )
        hint = "pulblic_templates_based" if pulblic_templates else "from_scratch"

        # 👇 4. user_text -> userMessage로 수정
        prompt_builder = NewTemplatePromptBuilder(
            userMessage=state["userMessage"],
            extracted_fields=state["extracted_fields"],
            public_templates=pulblic_templates
        )
        messages = prompt_builder.build()
        template = await state["openai_service"].chat_completion(messages)
        logger.info(f"✅ 신규 생성 성공 (방식: {hint})")
        return {"generated_template": template, "generation_hint": hint, "pulblic_templates": pulblic_templates}
    except Exception as e:
        logger.error(f"❌ 신규 생성 실패: {e}", exc_info=True)
        return {"generated_template": "템플릿 생성 중 오류 발생", "generation_hint": "error", "pulblic_templates": []}

def finalize_result_node(state: TemplateGenerationState) -> Dict[str, Any]:
    logger.info("=" * 60)
    logger.info("6단계: 최종 결과 정리")
    variables = extract_variables_from_template(state.get("generated_template", ""))
    final_result = {
        "pipeline_success": True,
        "error_message": None,
        "template_text": state.get("generated_template", ""),
        "template_title": state.get("generated_title", "제목 없음"),
        "variables": variables,
        "generation_method": state.get("generation_hint", "unknown"),
        "message_type": state.get("message_type_result", {}).get("type"),
        "category_sub": state.get("category_result", {}).get("category_sub"),
        "category_analysis": state.get("category_result"),
        "similarity_score": state.get("max_similarity", 0.0),
        "reference_templates": state.get("similar_templates", []),
        "pulblic_templates": state.get("pulblic_templates", []),
    }
    logger.info("✅ 파이프라인 최종 결과 생성 완료.")
    # 👇 --- 최종 생성된 템플릿을 터미널에 명확하게 출력 --- 👇
    logger.info("-" * 60)
    logger.info(">>> 최종 생성된 템플릿 본문 <<<")
    logger.info(final_result.get("template_text"))
    logger.info("-" * 60)
    return {"final_result": final_result}

def extract_variables_from_template(template_text: str) -> list[str]:
    if not template_text: return []
    return sorted(list(set(re.findall(r'#\{([^}]+)\}', template_text))))

