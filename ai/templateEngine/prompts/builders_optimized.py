# # templateEngine/prompts/builders_optimized.py
#
# from abc import ABC, abstractmethod
# from typing import List, Dict, Optional
# from datetime import datetime
# from langchain.prompts import PromptTemplate
# from functools import lru_cache
#
#
# class CachedPromptBuilder(ABC):
#     """캐시된 프롬프트 빌더 기본 클래스"""
#
#     def __init__(self):
#         self._cached_system_prompt = None
#         self._cached_template = None
#
#     @property
#     @lru_cache(maxsize=1)
#     def system_prompt(self) -> str:
#         """정적 시스템 프롬프트를 캐시"""
#         if self._cached_system_prompt is None:
#             self._cached_system_prompt = self._build_system_prompt()
#         return self._cached_system_prompt
#
#     @abstractmethod
#     def _build_system_prompt(self) -> str:
#         """시스템 프롬프트 생성 (한 번만 실행됨)"""
#         pass
#
#     @abstractmethod
#     def build_with_message(self, user_message: str) -> List[Dict]:
#         """사용자 메시지와 함께 최종 프롬프트 생성"""
#         pass
#
#
# class TypePromptBuilder(CachedPromptBuilder):
#     """메시지 유형 분류 - 캐시 최적화 버전"""
#
#     @lru_cache(maxsize=1)
#     def _build_system_prompt(self) -> str:
#         return """
# 너는 카카오 알림 메세지의 유형을 판정하는 분류기다.
# [메세지 유형 정의]
# - BASIC: 핵심 목적(알림/안내/확인 등)만 전달. 링크가 있을 수 있으나, "채널 추가/채널 방문" 목적이 아니면 기본형으로 본다.
# - 고객에게 반드시 전달되어야 하는 정보
# - EXTRA_INFO:핵심 목적 외에 주의사항·정책·문의·절차·상세 가이드 등 실질적인 추가 설명이 붙음.
# - 이용안내 등 보조적인 정보메시지
# - CHANNEL_ADD: 카카오 채널/브랜드 채널/오픈채팅 등을 추가·구독·방문하도록 유도하는 맥락이 존재.
# - HYBRID: 채널 추가형 조건 + 부가 정보형 조건을 동시에 충족.
#
# [메세지 유형 판정 원칙]
# 1) 먼저 채널 추가 유도 여부를 본다. 단순 웹사이트/배송조회/결제 안내는 채널 추가형이 아니다.
# 2) 다음으로 핵심 목적 외에 실질적인 부가 설명이 있는지 본다.
# 3) 최종 결정:
# - 둘 다 있으면 HYBRID
# - 채널 추가만 있으면 CHANNEL_ADD
# - 부가 설명만 있으면 EXTRA_INFO
# - 둘 다 없으면 BASIC
# 4) 애매하면 가장 합리적인 단일 유형을 고르고 이유를 간단히 남긴다.
#
# [출력 형식(JSON만 출력)]
# {
#     "has_channel_link": true/false,
#     "has_extra_info": true/false,
#     "type": "BASIC | EXTRA_INFO | CHANNEL_ADD | HYBRID",
#     "explain_type": "한 줄 이유"
# }
# """
#
#     def build_with_message(self, user_message: str) -> List[Dict]:
#         return [
#             {"role": "system", "content": self.system_prompt},
#             {"role": "user", "content": f"본문: {user_message}"}
#         ]
#
#
# class FieldsPromptBuilder(CachedPromptBuilder):
#     """변수 필드 추출 - 캐시 최적화 버전"""
#
#     @lru_cache(maxsize=1)
#     def _build_system_prompt(self) -> str:
#         today_str = datetime.now().strftime('%Y-%m-%d')
#         return f"""당신은 텍스트에서 변수를 추출하고 정제하는 '데이터 엔지니어'입니다.
# 주어진 본문에서 **템플릿화할 수 있는 모든 정보**를 찾아 변수로 추출해야 합니다.
#
# **오늘 날짜: {today_str}**
#
# **변수 추출 기준:**
# - 개인 정보: 이름, 전화번호, 주소, 주문번호 등
# - 호칭/대명사: "고객님", "회원님", 특정 이름 등 **개인화 가능한 모든 호칭**
# - 날짜/시간: 특정 날짜, 기간, 시간 등
# - 금액/수치: 가격, 할인율, 수량 등
# - 이벤트 정보: 테마, 장소, 상품명, 브랜드명 등
# - 연락처 정보: 전화번호, 이메일 등
# - **템플릿에서 다른 값으로 치환될 가능성이 있는 모든 구체적인 정보**
#
# **변수 추출 및 정제 규칙:**
# 1. **날짜 추론:** '오늘', '내일', '모레'와 같은 상대적인 날짜 표현이 나오면, **오늘 날짜({today_str})를 기준**으로 실제 날짜(YYYY-MM-DD)를 계산하여 값으로 사용해야 합니다.
#
# 2. **변수명 규칙:**
#    - **영문 소문자**와 **스네이크 케이스(snake_case)**만 사용해야 합니다.
#    - 표준 변수명 사용:
#      * 고객 이름: `customer_name`
#      * 고객 호칭: `customer_title` (예: "고객님", "회원님")
#      * 전화번호: `phone_number`
#      * 도착 예정일: `arrival_date`
#      * 주문번호: `order_id`
#      * 금액: `amount`
#      * 할인율: `discount_rate`
#      * 장소: `location`
#      * 테마/제목: `theme` 또는 `title`
#      * 브랜드명: `brand_name`
#      * 기간: `event_period` 또는 `start_date`, `end_date`
#
# 3. **추출 대상:** 이름, 날짜, 시간, 금액, 주문번호, 할인율, 장소, 상품명, 전화번호, 주소, 테마, 브랜드명, 기간 등 **구체적이고 변경 가능한 모든 정보**를 빠짐없이 추출해야 합니다.
#
# **출력 형식:**
# - 추출된 값과 그에 해당하는 변수명을 JSON 형식으로 매핑하세요.
# - 변수화할 필드가 전혀 없으면, 반드시 빈 JSON 객체를 반환하세요: {{}}
#
# **완벽한 예시:**
# - 본문: "김철수님, 주문번호 ORD-123이 50,000원 결제 완료되었습니다."
# - 응답:
# {{
#     "customer_name": "김철수",
#     "order_id": "ORD-123",
#     "amount": "50,000원"
# }}"""
#
#     def build_with_message(self, user_message: str) -> List[Dict]:
#         return [
#             {"role": "system", "content": self.system_prompt},
#             {"role": "user", "content": f"분석할 본문:\n{user_message}"}
#         ]
#
#
# class TemplateTitlePromptBuilder(CachedPromptBuilder):
#     """템플릿 제목 생성 - 캐시 최적화 버전"""
#
#     @lru_cache(maxsize=1)
#     def _build_system_prompt(self) -> str:
#         return """
# 카카오 알림톡 템플릿의 제목을 생성하는 전문가입니다.
# 다음 규칙을 따라 제목을 생성하세요:
#
# 1. 10자 이내로 간결하게
# 2. 메시지의 핵심 내용을 포함
# 3. 사용자가 쉽게 이해할 수 있는 명확한 표현
# 4. 제목만 출력 (추가 설명 불필요)
#
# 예시:
# - "주문완료 안내"
# - "배송출발 알림"
# - "예약확정 통보"
# """
#
#     def build_with_message(self, user_message: str) -> List[Dict]:
#         return [
#             {"role": "system", "content": self.system_prompt},
#             {"role": "user", "content": f"다음 메시지의 제목을 생성해주세요:\n{user_message}"}
#         ]
#
#
# # 기존의 BasePromptBuilder 기반 클래스들 (캐시 미적용)
# class CategoryPromptBuilder:
#     """카테고리 분류 프롬프트 빌더"""
#     def __init__(self, userMessage: str, category_sub_list: List[str]):
#         self.userMessage = userMessage
#         self.category_sub_list = category_sub_list
#
#     def build(self) -> List[Dict]:
#         system_prompt = f"""
# 당신은 카카오 알림톡 카테고리 분류 전문가입니다.
# 주어진 메시지를 분석하여, 아래 '서브 카테고리 후보' 중 가장 적합한 것을 선택하세요.
#
# 서브 카테고리 후보:
# {', '.join(self.category_sub_list)}
#
# 중요: 만약 후보 중에 적합한 카테고리가 **없다고 판단되면**, "is_appropriate" 값을 false로 설정하고 그 이유를 명확히 설명해주세요.
#
# JSON 형식으로 응답하세요:
# {{
#     "is_appropriate": true,
#     "category_sub": "선택된 서브 카테고리",
#     "confidence": 85,
#     "selection_reason": "최종 선택 근거 상세 설명"
# }}
# """
#         return [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": f"분석할 메시지:\n{self.userMessage}"}
#         ]
#
#
# class NewCategoryPromptBuilder:
#     """신규 카테고리 생성 프롬프트 빌더"""
#     def __init__(self, userMessage: str, existing_categories: List[str]):
#         self.userMessage = userMessage
#         self.existing_categories = existing_