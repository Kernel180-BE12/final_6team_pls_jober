from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class BasePromptBuilder(ABC):
    """기본 프롬프트 빌더"""
    def __init__(self, userMessage: str):
        self.userMessage = userMessage
        self.hints: list[dict] = []

    def _apply_security_protection(self, messages: list) -> list:
        """보안 보호 규칙 적용"""
        from .message_analyzer_prompts import PromptDefense
        return PromptDefense.add_system_protection(messages)

    def add_hint(self, description: str, content: str):
        """힌트 추가"""
        self.hints.append({"description": description, "content": content})
        return self

    @abstractmethod
    def build(self) -> List[Dict]:
        """프롬프트 빌드 로직은 구체 빌더가 구현"""
        pass


class AdvancedFieldsPromptBuilder(BasePromptBuilder):
    """고도화된 변수 추출 프롬프트 빌더 - 카카오 가이드라인 완벽 준수"""

    def build(self) -> List[Dict]:
        today_str = datetime.now().strftime('%Y-%m-%d')

        system_prompt = f"""당신은 카카오 알림톡 변수 추출 전문가입니다.

## 핵심 미션
주어진 텍스트에서 템플릿화 가능한 모든 정보를 식별하고, 카카오 가이드라인에 맞는 변수로 매핑하세요.

## 카카오 알림톡 변수 규칙
1. **형식**: #{{변수명}} (중괄호 2개)
2. **명명**: 한글로 명명 (예: 고객명, 주문번호, 금액)
3. **1,300자 제한**: 템플릿 전체 길이 고려
4. **개인정보 보호**: 모든 개인식별정보는 필수 변수화

## 변수 추출 우선순위
### HIGH (필수 변수화)
- 개인정보: 이름, 전화번호, 주소, 이메일
- 식별번호: 주문번호, 예약번호, 회원번호
- 금융정보: 금액, 할인율, 포인트
- 시간정보: 날짜, 시간, 기간

### MEDIUM (권장 변수화)
- 장소정보: 매장명, 지역, 주소
- 상품정보: 상품명, 브랜드명, 모델명
- 호칭: "고객님", "회원님" 등

### LOW (선택적 변수화)
- 일반적인 안내 문구나 고정 텍스트

## 날짜 처리 규칙
- 기준일: {today_str}
- "오늘" → {today_str}
- "내일" → 다음날 계산
- "모레" → 2일 후 계산
- 상대적 표현을 절대 날짜로 변환

## 표준 변수명 매핑 (한글 변수명 사용)
```
개인정보:
- 고객명 (이름)
- 호칭 (고객님, 회원님 등)
- 전화번호
- 이메일
- 주소

식별번호:
- 주문번호
- 예약번호
- 회원번호
- 상품번호

금융정보:
- 금액
- 할인금액
- 포인트
- 적립금

시간정보:
- 주문일시
- 배송일시
- 예약일시
- 처리일시

장소정보:
- 매장명
- 지역명
- 주소

상품정보:
- 상품명
- 브랜드명
- 모델명
```

## 출력 형식
반드시 JSON 형식으로만 응답:
{{
    "extracted_fields": {{
        "원본텍스트": "변수명",
        "홍길동": "고객명",
        "2024-01-15": "주문일시"
    }},
    "confidence": 0.95,
    "reasoning": "추출 근거 설명"
}}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 텍스트에서 변수를 추출해주세요:\n\n{self.userMessage}"}
        ]
        
        return self._apply_security_protection(messages)


class FieldsPromptBuilder(AdvancedFieldsPromptBuilder):
    """기존 FieldsPromptBuilder와 호환성 유지"""
    pass


class ExpertTemplateBuilder(BasePromptBuilder):
    """전문가급 템플릿 생성 빌더 - 구체적이고 실용적인 템플릿 생성"""

    def __init__(self, userMessage: str, extracted_fields: Dict, message_type: str = None, reference_templates: List[Dict] = None):
        super().__init__(userMessage)
        self.extracted_fields = extracted_fields
        self.message_type = message_type
        self.reference_templates = reference_templates or []

    def build(self) -> List[Dict]:
        # 변수 매핑 규칙 생성
        variable_mapping = self._generate_variable_mapping()
        
        # 메시지 타입별 규칙
        type_rules = self._get_message_type_rules()
        
        # 참고 템플릿 컨텍스트
        reference_context = self._build_reference_context()

        system_prompt = f"""
당신은 15년차 카피라이터이자 카카오 알림톡 템플릿 검수 전문가입니다.
고객에게 전달되는 메시지인 만큼, 친절하며 프로페셔널한 톤앤매너를 유지하되, 알림톡 의도에 벗어나는 내용은 제거하고 간략하고 명확하게 전달되어야 합니다.

{variable_mapping}

{type_rules}

{reference_context}

## 필수 규칙: 템플릿 구조
1. **인사:** "안녕하세요, 고객님." 과 같이 부드러운 문장으로 시작합니다.
2. **핵심 내용:** 전달하려는 가장 중요한 내용을 먼저 제시합니다.
3. **상세 정보 (선택 사항):** 필요시, '▶' 기호를 사용하여 정보를 항목별로 명확하게 구분합니다.
4. **마무리:** "감사합니다." 또는 "많은 이용 부탁드립니다." 와 같은 긍정적인 문장으로 끝맺습니다.
5. **발송 근거:** 템플릿 가장 마지막 줄에는 `*`로 시작하는 발송 근거를 반드시 포함해야 합니다.

## 좋은 템플릿의 조건
1. **친절함:** 딱딱하지 않고 부드러운 문장으로 시작하고 끝냅니다.
2. **명확성:** 핵심 정보를 쉽게 파악할 수 있도록 줄 바꿈과 구성을 활용합니다.
3. **정확성:** 변수 규칙을 포함한 모든 규칙을 100% 준수합니다.

## 생성 예시
- 사용자 요청: "회원가입이 완료되었습니다. 10% 할인 쿠폰을 드립니다."
- **바람직한 생성 결과:**
    안녕하세요, #{{고객명}}님.
    회원가입이 완료되었습니다.
    감사합니다.
    *본 알림은 정보통신망법에 따라 발송되었습니다.

**중요**: 위 예시처럼 간결하고 명확하게 생성하세요.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 내용으로 템플릿을 생성해주세요:\n\n{self.userMessage}"}
        ]
        return messages

    def _generate_variable_mapping(self) -> str:
        """변수 매핑 규칙 생성"""
        if not self.extracted_fields:
            return ""
        
        mapping_rules = "\n## 변수 처리 규칙\n"
        mapping_rules += "아래 규칙에 따라, 원본 메시지의 특정 단어를 `#{변수명}` 형태로 반드시 교체해야 합니다.\n"
        
        for value, var_name in self.extracted_fields.items():
            mapping_rules += f"- '{value}'는 `#{{{var_name}}}`으로 변경하세요.\n"
        
        return mapping_rules

    def _get_message_type_rules(self) -> str:
        """메시지 타입별 규칙"""
        if not self.message_type:
            return ""
        
        type_rules = {
            "notification": "알림형: 중요한 정보나 상태 변화를 명확하게 전달하세요.",
            "guidance": "안내형: 사용자에게 필요한 행동이나 정보를 친절하게 안내하세요.",
            "marketing": "마케팅형: 상품이나 서비스를 매력적으로 홍보하되 과도하지 않게 하세요.",
            "verification": "인증형: 보안 관련 정보를 신뢰할 수 있게 전달하세요."
        }
        
        return f"\n## 메시지 타입 규칙\n{type_rules.get(self.message_type, '')}"

    def _build_reference_context(self) -> str:
        """참고 템플릿 컨텍스트 생성"""
        if not self.reference_templates:
            return ""
        
        context = "\n## 참고 템플릿\n"
        for i, template in enumerate(self.reference_templates[:3], 1):
            context += f"### 참고 템플릿 {i}\n{template.get('text', '')}\n\n"
        
        return context


class CategoryPromptBuilder(BasePromptBuilder):
    """정교한 카테고리 분류 프롬프트 빌더"""

    def __init__(self, userMessage: str, category_sub_list: List[str]):
        super().__init__(userMessage)
        self.category_sub_list = category_sub_list

    def build(self) -> List[Dict]:
        system_prompt = f"""
당신은 카카오 알림톡 템플릿 카테고리 분류 전문가입니다.

## 분류 대상 카테고리
{', '.join(self.category_sub_list)}

## 분류 기준
1. **메시지의 주요 목적** 파악
2. **사용자에게 전달되는 정보의 성격** 분석
3. **기존 카테고리와의 유사성** 고려

## 출력 형식
반드시 JSON 형식으로만 응답:
{{
    "category": "선택된_카테고리명",
    "confidence": 0.0-1.0,
    "reason": "분류 이유를 간단히 설명"
}}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 메시지를 분석하여 적절한 카테고리로 분류해주세요:\n\n{self.userMessage}"}
        ]
        
        return self._apply_security_protection(messages)


class TypePromptBuilder(BasePromptBuilder):
    """고도화된 메시지 타입 분류 빌더"""

    def build(self) -> List[Dict]:
        system_prompt = """
당신은 카카오톡 알림톡 템플릿의 메시지 타입을 분류하는 전문가입니다.
사용자의 요청을 분석하여 다음 중 하나의 타입으로 분류해주세요:

1. **알림형 (notification)**: 중요한 정보나 상태 변화를 알리는 메시지
   - 예: 주문 완료, 배송 시작, 결제 완료, 예약 확인 등

2. **안내형 (guidance)**: 사용자에게 특정 행동이나 정보를 안내하는 메시지
   - 예: 이벤트 참여 방법, 서비스 이용 안내, 정책 변경 안내 등

3. **마케팅형 (marketing)**: 상품이나 서비스를 홍보하는 메시지
   - 예: 할인 쿠폰 발급, 신상품 출시, 이벤트 홍보 등

4. **인증형 (verification)**: 본인 확인이나 보안 관련 메시지
   - 예: 로그인 알림, 비밀번호 변경, 보안 인증 등

5. **기타 (other)**: 위 분류에 속하지 않는 기타 메시지

## 분류 기준
- 메시지의 주요 목적과 의도를 파악
- 사용자가 받을 때 느낄 감정이나 반응 고려
- 카카오톡 알림톡의 일반적인 사용 패턴 참고

## 출력 형식
반드시 JSON 형식으로만 응답:
{
    "message_type": "분류된_타입",
    "confidence": 0.0-1.0,
    "reason": "분류 이유를 간단히 설명"
}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 메시지의 타입을 분류해주세요:\n\n{self.userMessage}"}
        ]
        
        return self._apply_security_protection(messages)


class TemplateTitlePromptBuilder:
    """간결하고 명확한 제목 생성기"""

    def __init__(self, userMessage: str):
        self.userMessage = userMessage

    def build(self) -> List[Dict]:
        system_prompt = """
당신은 카카오 알림톡 템플릿 제목 생성 전문가입니다.

## 제목 생성 규칙
1. **간결성**: 10-20자 내외로 간결하게
2. **명확성**: 메시지의 핵심 내용을 명확하게 표현
3. **직관성**: 사용자가 한눈에 이해할 수 있도록
4. **일관성**: 비슷한 유형의 메시지는 비슷한 패턴 사용

## 제목 예시
- "주문 완료 알림"
- "배송 시작 안내"
- "회원가입 완료"
- "결제 확인 알림"
- "예약 확정 안내"

## 출력 형식
반드시 JSON 형식으로만 응답:
{
    "title": "생성된_제목",
    "confidence": 0.0-1.0,
    "reason": "제목 선택 이유"
}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 메시지에 적합한 제목을 생성해주세요:\n\n{self.userMessage}"}
        ]
        
        return messages


class ComplianceTemplateBuilder:
    """100% 컴플라이언스 보장 템플릿 빌더"""

    def __init__(self, userMessage: str, extracted_fields: Dict, strict_mode: bool = True):
        self.userMessage = userMessage
        self.extracted_fields = extracted_fields
        self.strict_mode = strict_mode

    def build(self) -> List[Dict]:
        system_prompt = """
당신은 카카오 알림톡 컴플라이언스 전문가입니다.
모든 법적 규정과 카카오 가이드라인을 100% 준수하는 템플릿을 생성해야 합니다.

## 컴플라이언스 규칙
1. **정보통신망법 준수**: 발송 근거 명시 필수
2. **개인정보보호법 준수**: 개인정보 변수화 필수
3. **광고성 정보 표시**: 마케팅 메시지 구분
4. **스팸 방지**: 과도한 홍보 금지
5. **명확한 발신자**: 발신자 정보 명시

## 필수 요소
- 발송 근거 문구 (예: *본 알림은 정보통신망법에 따라 발송되었습니다.)
- 개인정보 변수화 (#{고객명}, #{전화번호} 등)
- 명확한 발신자 정보
- 적절한 문구 길이 (1,300자 이내)

## 출력 형식
반드시 JSON 형식으로만 응답:
{
    "template": "생성된_템플릿_내용",
    "compliance_check": {
        "info_act": true/false,
        "privacy_protection": true/false,
        "spam_prevention": true/false,
        "sender_info": true/false
    },
    "reason": "컴플라이언스 준수 사항 설명"
}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 내용으로 컴플라이언스를 100% 준수하는 템플릿을 생성해주세요:\n\n{self.userMessage}"}
        ]
        return messages


class SuitabilityCheckPromptBuilder(BasePromptBuilder):
    """메시지 적합성 검사 프롬프트 빌더"""
    
    def build(self) -> List[Dict]:
        system_prompt = """
당신은 사용자 요청이 '카카오톡 알림톡 템플릿'을 생성하기에 적합한지 판단하는 '게이트키퍼' AI입니다.
사용자의 메시지가 템플릿 생성을 위한 구체적인 내용(예: 주문 확인, 예약 안내, 배송 알림 등)을 포함하고 있는지, 아니면 단순히 일상적인 대화나 관련 없는 질문(예: '안녕?', '김치찌개 레시피 알려줘')인지 판단해야 합니다.

**판단 기준:**
- **적합 (suitable):** 메시지가 알림, 공지, 정보 전달 등 명확한 목적을 가진 템플릿으로 변환될 수 있는 내용을 담고 있을 때.
  - 예: "고객님, 주문하신 상품이 배송 시작되었습니다.", "내일 3시에 예약하신 미용실 방문 잊지 마세요.", "회원가입을 축하합니다! 10% 할인 쿠폰을 드립니다."
- **부적합 (unsuitable):** 메시지가 일반적인 질문, 감정 표현, 템플릿과 관련 없는 명령, 또는 의미 없는 단어일 때.
  - 예: "오늘 날씨 어때?", "슬프다", "너는 누구야?", "김치찌개 만드는 법", "asdfghjkl"

**출력 형식:**
- 반드시 아래 JSON 형식으로만 응답해야 합니다.
- 추가적인 설명이나 인사는 절대 포함하지 마세요.

{
    "is_suitable": true/false,
    "reason": "판단에 대한 간결한 한 줄 설명"
}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "회원가입이 완료되었습니다. 10% 할인 쿠폰을 드립니다."},
            {"role": "assistant", "content": '{"is_suitable": true, "reason": "회원가입 완료 및 쿠폰 발급이라는 명확한 정보성 목적을 가집니다."}'},
            {"role": "user", "content": "김치찌개 레시피 알려줘"},
            {"role": "assistant", "content": '{"is_suitable": false, "reason": "카카오톡 알림톡 템플릿 생성과 관련 없는 일상적인 질문입니다."}'},
            {"role": "user", "content": f"다음 메시지를 분석해주세요:\n{self.userMessage}"}
        ]
        
        return self._apply_security_protection(messages)


# 기존 코드와의 호환성을 위한 클래스들
class ReferenceBasedTemplatePromptBuilder(ExpertTemplateBuilder):
    """참고 템플릿 기반 생성 빌더 (호환성 유지)"""

    def __init__(self, userMessage: str, reference_templates: List[Dict], extracted_fields: Dict):
        super().__init__(userMessage, extracted_fields, reference_templates=reference_templates)


class NewTemplatePromptBuilder(ExpertTemplateBuilder):
    """신규 템플릿 생성 빌더 (호환성 유지)"""

    def __init__(self, userMessage: str, extracted_fields: Dict, public_templates: Optional[List[Dict]] = None):
        super().__init__(userMessage, extracted_fields, reference_templates=public_templates)


class NewCategoryPromptBuilder(BasePromptBuilder):
    """신규 카테고리 생성 프롬프트 빌더"""

    def __init__(self, userMessage: str, existing_categories: List[str]):
        super().__init__(userMessage)
        self.existing_categories = existing_categories

    def build(self) -> List[Dict]:
        system_prompt = f"""# 카테고리 네이밍 전문가

당신의 임무는 메시지 내용에 가장 적합한 새로운 카테고리명을 생성하는 것입니다.

## 생성 규칙
1. **형식 일치**: 기존 카테고리들의 스타일과 형식을 반드시 따르세요
2. **간결성**: 2~5자 내외로 간결하게
3. **명확성**: 의미가 명확하고 직관적이어야 함
4. **일관성**: 기존 패턴과 일관성 있는 명명

## 기존 카테고리 스타일 참고
{', '.join(self.existing_categories[:10])}

## 출력 형식
JSON 형식으로만 응답:
{{
    "category": "새로운_카테고리명",
    "confidence": 0.0-1.0,
    "reason": "카테고리 선택 이유"
}}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 메시지에 적합한 새로운 카테고리를 생성해주세요:\n\n{self.userMessage}"}
        ]
        
        return self._apply_security_protection(messages)