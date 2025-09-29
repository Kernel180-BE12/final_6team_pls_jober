from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class BasePromptBuilder(ABC):
    """기본 프롬프트 빌더"""
    def __init__(self, userMessage: str):
        super().__init__(userMessage)
        self.userMessage = userMessage

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
- 전화번호 (연락처)
- 이메일 (이메일 주소)

주문/예약:
- 주문번호 (주문 ID)
- 예약번호 (예약 ID)
- 예약일 (예약 날짜)
- 배송일 (배송 예정일)

금융:
- 금액 (결제 금액)
- 할인율 (할인 비율)
- 포인트 (적립 포인트)

위치:
- 매장명 (지점명)
- 위치 (주소/장소)
- 지점명 (매장 이름)

상품:
- 상품명 (제품명)
- 브랜드명 (브랜드)
- 카테고리 (분류)

시간:
- 시작일 (시작 날짜)
- 종료일 (끝날짜)
- 행사기간 (이벤트 기간)
- 만료일 (유효기간)

기타:
- 공지제목 (공지사항 제목)
- 공지내용 (공지사항 내용)
- 공지일자 (공지 날짜)
```

## 출력 형식
정확한 JSON 객체로만 응답하세요. 변수가 없으면 빈 객체 {{}}.

## 예시
입력: "김철수님, 주문번호 ORD-123의 50,000원 결제가 완료되었습니다."
출력:
{{
    "고객명": "김철수",
    "주문번호": "ORD-123",
    "금액": "50,000원"
}}

입력: "내일 오후 2시에 강남점에서 픽업 가능합니다."
출력:
{{
    "픽업일": "{datetime.now().strftime('%Y-%m-%d') if 'tomorrow' in 'text' else 'CALCULATE'}",
    "픽업시간": "오후 2시",
    "매장명": "강남점"
}}

변수 추출을 시작하세요."""

        messages = [
            {"role": "system", "content": system_prompt},
            *self._build_hint_messages(),
            {"role": "user", "content": f"다음 텍스트에서 변수를 추출해주세요:\n\n{self.userMessage}"}
        ]
        return messages


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

        # 메시지 타입별 특화 규칙
        type_rules = self._get_message_type_rules()

        # 참고 템플릿 컨텍스트
        reference_context = self._build_reference_context()

        system_prompt = f"""# 카카오 알림톡 실전 템플릿 생성 전문가

당신은 실제 비즈니스에서 바로 사용 가능한, 구체적이고 실용적인 카카오 알림톡 템플릿을 생성하는 전문가입니다.

## 핵심 철학: "추상적 ❌ → 구체적 ✅"
- 일반적인 템플릿이 아닌, 실제 상황에 맞는 구체적인 내용 생성
- 사용자가 요청한 상황을 정확히 반영한 실용적 템플릿
- 날짜, 시간, 장소 등 모든 정보를 구체적으로 표현

## 절대 준수 사항 (위반시 심사 반려)
1. **문자 수 제한**: 1,300자 이내 (공백, 줄바꿈 포함)
2. **변수 형식**: #{{한글변수명}} 형식만 사용 (예: #{{고객명}}, #{{주문번호}})
3. **광고성 표현 금지**: 할인, 특가, 이벤트, 프로모션 등 직접 마케팅 용어 금지
4. **발송 근거 필수**: 하단에 *로 시작하는 법적 근거 명시
5. **개인정보 보호**: 모든 개인정보는 변수 처리 필수

## 날짜/시간 처리 원칙 (오늘: {datetime.now().strftime('%Y년 %m월 %d일')})
- **"내일"** → {(datetime.now() + timedelta(days=1)).strftime('%Y년 %m월 %d일')} (구체적 날짜)
- **"모레"** → {(datetime.now() + timedelta(days=2)).strftime('%Y년 %m월 %d일')} (구체적 날짜)
- **상대적 표현** → 절대 날짜로 변환
- **요일 표기**: (월), (화), (수) 등으로 추가

{variable_mapping}

{type_rules}

## 템플릿 구조 프레임워크
```
[인사말] - 친근하고 정중한 시작
안녕하세요, #{{고객명}}님.

[핵심 메시지] - 가장 중요한 내용 우선
[주요 정보가 담긴 문장]

[상세 정보] - 필요시에만 포함
▶ 항목1: #{{변수1}}
▶ 항목2: #{{변수2}}

[추가 안내] - 부가정보형인 경우에만
[주의사항이나 추가 설명]

[마무리 인사] - 긍정적 종료
감사합니다. / 궁금한 점이 있으시면 언제든 문의해 주세요.

[발송 근거] - 필수
*본 알림은 정보통신망법에 따라 발송되었습니다.
```

{reference_context}

## 실전 생성 지침
1. **상황 분석**: 사용자 요청을 정확히 파악하고 실제 비즈니스 상황 반영
2. **구체적 정보**: 추상적 표현 금지, 실제 사용할 수 있는 구체적 내용
3. **완전한 정보**: 관련된 모든 필수 정보 포함 (시간, 장소, 연락처 등)
4. **실용적 구조**: 받는 사람이 바로 이해할 수 있는 명확한 구조
5. **비즈니스 요소**: 문의처, 수신거부, 변경/취소 안내 등 실제 필요한 요소 포함

## 업종별 필수 포함 요소
- **의료**: 예약일시, 진료항목, 위치, 주의사항, 변경/취소 안내
- **배송**: 발송/도착 정보, 운송장번호, 받는 곳, 연락처
- **예약**: 예약일시, 장소, 담당자, 준비물, 변경 규정
- **결제**: 결제 내역, 금액, 일시, 영수증, 문의처
- **공지**: 제목, 내용, 적용일, 문의처, 추가 안내

## 품질 검증 체크리스트
- [ ] 1,300자 이내인가?
- [ ] 모든 변수가 #{{한글변수명}} 형식인가?
- [ ] 광고성 표현이 없는가?
- [ ] 발송 근거가 있는가?
- [ ] 개인정보가 보호되는가?

템플릿만 출력하세요 (설명, 주석, 체크리스트 제외):"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 요청으로 완벽한 카카오 알림톡 템플릿을 생성해주세요:\n\n{self.userMessage}"}
        ]
        return messages

    def _generate_variable_mapping(self) -> str:
        if not self.extracted_fields:
            return "## 변수 매핑\n변수 처리 대상이 없습니다."

        mapping_text = "## 필수 변수 매핑 규칙\n"
        mapping_text += "다음 텍스트를 정확히 #{{변수명}} 형태로 교체하세요:\n\n"

        for original_value, variable_name in self.extracted_fields.items():
            mapping_text += f"- '{original_value}' → #{{{{variable_name}}}}\n"

        return mapping_text

    def _get_message_type_rules(self) -> str:
        if not self.message_type:
            return ""

        rules_map = {
            "BASIC": """## 기본형 메시지 특화 규칙
- 핵심 정보만 간결하게 전달
- 불필요한 부가 설명 최소화
- 명확하고 직관적인 구조
- 변수를 통한 개인화 강화""",

            "EXTRA_INFO": """## 부가정보형 메시지 특화 규칙
- 핵심 내용 + 상세 부가정보 구조
- 주의사항, 이용방법을 하단 배치
- 항목별 구분 기호(▶, ■) 필수 사용
- 부가정보 영역에서는 변수 사용 최소화""",

            "CHANNEL_ADD": """## 채널추가형 메시지 특화 규칙
- 정보 전달 후 자연스러운 채널 유도
- "채널 추가" 버튼 텍스트 포함
- 채널 추가 혜택 간접적 언급
- 강요하지 않는 부드러운 톤""",

            "HYBRID": """## 복합형 메시지 특화 규칙
- 정보 → 부가설명 → 채널유도 순서
- 각 섹션별 명확한 구분
- 정보 밀도 최적화
- 전체 흐름의 자연스러움 확보"""
        }

        return rules_map.get(self.message_type, "")

    def _build_reference_context(self) -> str:
        if not self.reference_templates:
            return ""

        context = "## 참고 템플릿 (구조 학습용)\n"
        context += "아래 승인된 템플릿들의 구조와 패턴을 학습하여 적용하세요:\n\n"

        for i, template in enumerate(self.reference_templates[:2], 1):
            similarity = template.get('similarity', 0)
            text = template.get('text', '')
            metadata = template.get('metadata', {})

            context += f"### 참고 {i} (유사도: {similarity:.2f})\n"
            if metadata.get('title'):
                context += f"제목: {metadata['title']}\n"
            context += f"```\n{text}\n```\n\n"

        return context


class CategoryPromptBuilder(BasePromptBuilder):
    """정교한 카테고리 분류 프롬프트 빌더"""

    def __init__(self, userMessage: str, category_sub_list: List[str]):
        self.userMessage = userMessage
        super().__init__(userMessage)
        self.category_sub_list = category_sub_list

    def build(self) -> List[Dict]:
        system_prompt = f"""# 카카오 알림톡 카테고리 분류 전문가

당신의 임무는 메시지 내용을 분석하여 가장 적합한 서브 카테고리를 선택하는 것입니다.

## 분석 대상
메시지: {self.userMessage}

## 후보 카테고리
{', '.join(self.category_sub_list)}

## 분류 방법론
1. **의미적 분석**: 메시지의 핵심 목적과 내용 파악
2. **맥락 이해**: 발송 시나리오와 사용자 의도 분석
3. **키워드 매칭**: 카테고리별 핵심 키워드 대조
4. **적합성 검증**: 후보 중 최적의 매치 확인

## 판단 기준
- **정확성**: 메시지 내용과 카테고리의 의미적 일치
- **특이성**: 가장 구체적이고 명확한 카테고리 선택
- **완전성**: 메시지의 주요 속성을 모두 포괄

## 출력 형식
반드시 JSON으로만 응답하세요:

적합한 카테고리가 있는 경우:
{{
    "is_appropriate": true,
    "category_sub": "선택된_카테고리",
    "confidence": 85,
    "selection_reason": "선택 근거를 명확하고 구체적으로 설명"
}}

적합한 카테고리가 없는 경우:
{{
    "is_appropriate": false,
    "category_sub": null,
    "confidence": 30,
    "selection_reason": "왜 적합한 카테고리가 없는지 구체적 이유 설명"
}}

분석을 시작하세요."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 메시지를 분류해주세요:\n{self.userMessage}"}
        ]
        return self._apply_security_protection(messages)


class TypePromptBuilder(BasePromptBuilder):
    """고도화된 메시지 타입 분류 빌더"""

    def build(self) -> List[Dict]:
        system_prompt = """# 카카오 알림톡 메시지 타입 분류 엔진

당신은 메시지를 4가지 타입으로 정확히 분류하는 AI입니다.

## 분류 체계
### BASIC (기본형)
- **정의**: 핵심 정보만 전달하는 순수 알림 메시지
- **특징**: 추가 설명이나 채널 유도 없음
- **예시**: 주문 완료, 배송 출발, 예약 확인

### EXTRA_INFO (부가정보형)
- **정의**: 핵심 정보 + 상세 안내/주의사항
- **특징**: 이용방법, 정책, 주의사항 등 부연 설명 포함
- **예시**: 서비스 이용 안내 + 주의사항

### CHANNEL_ADD (채널추가형)
- **정의**: 정보 전달 + 카카오톡 채널 추가 유도
- **특징**: "채널 추가" 버튼이나 유도 문구 포함
- **예시**: 알림 + "채널 추가하고 혜택 받기"

### HYBRID (복합형)
- **정의**: EXTRA_INFO + CHANNEL_ADD 동시 충족
- **특징**: 상세 설명 + 채널 추가 유도 모두 포함
- **예시**: 서비스 안내 + 주의사항 + 채널 추가

## 분류 알고리즘
1. **채널 추가 요소 검사**
   - "채널 추가", "구독", "팔로우" 등 키워드
   - 마케팅 수신 동의 관련 내용

2. **부가 정보 요소 검사**
   - 주의사항, 이용방법, 정책 안내
   - "*", "※", "안내:" 등으로 시작하는 추가 설명

3. **최종 분류 결정**
   ```
   채널 추가 O + 부가 정보 O → HYBRID
   채널 추가 O + 부가 정보 X → CHANNEL_ADD
   채널 추가 X + 부가 정보 O → EXTRA_INFO
   채널 추가 X + 부가 정보 X → BASIC
   ```

## 출력 형식
JSON만 출력:
{{
    "has_channel_link": true/false,
    "has_extra_info": true/false,
    "type": "BASIC|EXTRA_INFO|CHANNEL_ADD|HYBRID",
    "explain_type": "분류 근거 상세 설명"
}}

분류를 시작하세요."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 메시지를 분류해주세요:\n\n{self.userMessage}"}
        ]
        return self._apply_security_protection(messages)


class TemplateTitlePromptBuilder:
    """간결하고 명확한 제목 생성기"""

    def __init__(self, userMessage: str):
        self.userMessage = userMessage

    def build(self) -> List[Dict]:
        system_prompt = """# 카카오 알림톡 제목 생성 전문가

## 미션
메시지 내용을 한눈에 알 수 있는 완벽한 제목을 생성하세요.

## 제목 생성 원칙
1. **길이**: 8자 이내 (한글 기준)
2. **명확성**: 메시지의 핵심을 정확히 표현
3. **직관성**: 누구나 이해할 수 있는 표현
4. **일관성**: 기존 알림톡 제목 패턴 준수

## 제목 패턴
- **완료계**: "주문완료", "결제완료", "예약완료"
- **알림계**: "배송출발", "도착예정", "변경안내"
- **확인계**: "예약확정", "승인완료", "처리완료"
- **안내계**: "이용안내", "정책변경", "서비스안내"

## 금지사항
- 따옴표(" ') 절대 사용 금지
- 마침표(.) 사용 금지
- 불필요한 수식어 금지
- 애매한 표현 금지

## 출력 형식
제목만 출력하세요 (설명이나 부가 텍스트 없이):

예시:
- 좋은 예: 주문완료안내
- 나쁜 예: "주문 완료에 대한 안내입니다."

제목 생성을 시작하세요."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 메시지의 제목을 생성해주세요:\n\n{self.userMessage}"}
        ]
        return messages


class ComplianceTemplateBuilder:
    """100% 컴플라이언스 보장 템플릿 빌더"""

    def __init__(self, userMessage: str, extracted_fields: Dict, strict_mode: bool = True):
        self.userMessage = userMessage
        self.extracted_fields = extracted_fields
        self.strict_mode = strict_mode

    def build(self) -> List[Dict]:
        variable_rules = ""
        if self.extracted_fields:
            variable_rules = "\n## 변수 매핑 (100% 적용 필수)\n"
            for value, var_name in self.extracted_fields.items():
                variable_rules += f"'{value}' → #{{{{var_name}}}}\n"

        compliance_level = "MAXIMUM" if self.strict_mode else "STANDARD"

        system_prompt = f"""# 카카오 심사 100% 통과 보장 템플릿 생성기

당신은 카카오 알림톡 심사팀 수준의 전문성을 가진 템플릿 검수관입니다.

## 컴플라이언스 레벨: {compliance_level}

{variable_rules}

## 절대 준수 규칙 (위반시 즉시 반려)
### 📏 기술적 제약
- **1,300자 엄수**: 공백, 줄바꿈, 특수문자 모두 포함하여 계산
- **변수 형식**: #{{한글변수명}} 중괄호 2개만 허용 (예: #{{고객명}}, #{{주문번호}})
- **인코딩**: UTF-8 한글 완벽 지원

### 🚫 콘텐츠 제약
- **광고 금지**: 할인, 특가, 이벤트, 프로모션, 혜택 등
- **과장 금지**: 최고, 최대, 완전, 100% 등
- **유도 금지**: 지금 구매, 서둘러, 놓치면 안되는 등

### 🔒 개인정보 보호
- **필수 변수화**: 이름, 전화, 주소, 이메일, 주민번호
- **식별번호 보호**: 주문번호, 예약번호, 계좌번호 등
- **민감정보 제외**: 비밀번호, 인증번호 등

### ⚖️ 법적 준수
- **발송근거 필수**: 하단에 법적 근거 명시
- **수신동의 전제**: 수신자가 동의한 내용만 발송
- **명확한 발신자**: 발송 주체 명확히 식별 가능

## 승인 확률 극대화 전략
1. **단순명료**: 복잡한 문장보다 간단하고 명확한 표현
2. **정보중심**: 감정적 어필보다 사실적 정보 전달
3. **구조적 정리**: 논리적이고 체계적인 정보 배치
4. **예의바른 톤**: 정중하면서도 친근한 어조

## 템플릿 품질 검증 프로세스
생성 후 다음을 자체 검증하세요:
- [ ] 문자수 1,300자 이내
- [ ] 한글 변수 형식 정확성 (#{{한글변수명}})
- [ ] 광고성 표현 부재
- [ ] 개인정보 변수화 완료
- [ ] 발송근거 포함
- [ ] 자연스러운 문체

## 출력 지침
- 템플릿 본문만 출력
- 설명이나 주석 일절 포함 금지
- 검증 체크리스트 출력 금지

완벽한 템플릿을 생성하세요:"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 내용으로 심사를 100% 통과할 템플릿을 생성해주세요:\n\n{self.userMessage}"}
        ]
        return messages


# 기존 코드와의 호환성을 위한 클래스들 (deprecated되었지만 참조용으로 유지)
class FieldsPromptBuilder(AdvancedFieldsPromptBuilder):
    """기존 FieldsPromptBuilder와 호환성 유지"""
    pass


class ReferenceBasedTemplatePromptBuilder(ExpertTemplateBuilder):
    """참고 템플릿 기반 생성 빌더 (호환성 유지)"""

    def __init__(self, userMessage: str, reference_templates: List[Dict], extracted_fields: Dict):
        super().__init__(userMessage, extracted_fields, reference_templates=reference_templates)


class NewTemplatePromptBuilder(ExpertTemplateBuilder):
    """신규 템플릿 생성 빌더 (호환성 유지)"""

    def __init__(self, userMessage: str, extracted_fields: Dict, public_templates: Optional[List[Dict]] = None):
        super().__init__(userMessage, extracted_fields, reference_templates=public_templates)


class NewCategoryPromptBuilder(BasePromptBuilder):
    """신규 카테고리 생성 프롬프트 빌더 (기존 로직 유지)"""

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
    "new_category": "생성된_카테고리명"
}}

새로운 카테고리명을 생성하세요:"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 메시지에 대한 새로운 카테고리명을 생성해주세요:\n{self.userMessage}"}
        ]
        return messages