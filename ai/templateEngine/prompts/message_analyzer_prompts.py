"""
템플릿 수정용 프롬프트 빌더
"""
import re

class UnsuitableMessageError(ValueError):
    """메시지가 템플릿 생성에 부적합할 때 발생하는 예외"""
    pass


class PromptDefense:
    """프롬프트 인젝션 방어 클래스"""

    @staticmethod
    def sanitize_user_input(user_text: str) -> str:
        """사용자 입력 정화"""
        if not user_text:
            return ""

        # 프롬프트 인젝션 패턴 탐지 및 차단
        dangerous_patterns = [
            r'ignore\s+(?:previous|all|above|prior|earlier)\s+(?:instructions?|prompts?|rules?|commands?)',
            r'forget\s+(?:everything|all|what|your|previous|above|instructions?)',
            r'act\s+(?:as|like)\s+(?:a\s+)?(?:different|new|another)',
            r'you\s+are\s+(?:now|a|an)',
            r'system\s*[:：]\s*(?:reset|clear|ignore)',
            r'new\s+(?:role|character|personality|instructions?)',
            r'pretend\s+(?:to\s+be|you\s+are)',
            r'roleplay\s+(?:as|a)',
            r'simulate\s+(?:being|a)',
            r'override\s+(?:previous|your|all)',
            r'disregard\s+(?:previous|all|above)',
            r'\\n\\n.*system.*role',
            r'assistant\s*[:：]\s*i\s+(?:am|will)',
            r'human\s*[:：].*assistant\s*[:：]',
            r'###\s*(?:system|instruction|new|override)',
            r'```\s*(?:system|instruction|prompt)',
            r'카카오.*템플릿.*(?:잊어|무시|버려)',
            r'이전.*(?:명령|지시|규칙).*(?:잊어|무시|따르지)',
            r'다른.*(?:역할|캐릭터|AI).*(?:되어|행동|연기)',
            r'새로운.*(?:지시|명령|역할).*따라',
            r'시스템.*(?:리셋|초기화|무시)',
        ]
        
        # 위험한 패턴이 발견되면 정화
        for pattern in dangerous_patterns:
            if re.search(pattern, user_text, re.IGNORECASE):
                # 위험한 패턴은 제거
                user_text = re.sub(pattern, '[필터링됨]', user_text, flags=re.IGNORECASE)
        
        return user_text




class TemplateGenerationPromptBuilder:
    """템플릿 생성용 프롬프트 빌더"""
    def __init__(self, category: str, user_message: str, context: str = ""):
        # 모든 입력값 정화
        self.category = PromptDefense.sanitize_user_input(category)
        self.user_message = PromptDefense.sanitize_user_input(user_message)
        self.context = PromptDefense.sanitize_user_input(context)

    def build(self) -> str:
        return f"""

카테고리: {self.category}
사용자 요청: {self.user_message}

관련 가이드라인:
{self.context}

위 정보를 바탕으로 알림톡 템플릿을 생성해주세요. 
템플릿에는 변수(예: #{{변수명}})를 포함하고,
변수 목록도 함께 제공해주세요.

템플릿 형식:
- 친근하고 정중한 톤
- 명확한 정보 전달
- 적절한 변수 사용
- 카카오톡 알림톡 가이드라인 준수
"""

class TemplateModificationPromptBuilder:
    """템플릿 수정용 프롬프트 빌더"""
    def __init__(self, current_template: str, user_message: str, chat_context: str = ""):
        # 모든 입력값 정화
        self.current_template = PromptDefense.sanitize_user_input(current_template)
        self.user_message = PromptDefense.sanitize_user_input(user_message)
        self.chat_context = PromptDefense.sanitize_user_input(chat_context)

    def build(self) -> str:
        return f"""

        당신은 카카오톡 알림톡 템플릿 수정 전문가입니다.

        ## 작업 지침
        1. 이전 대화 내용을 참고하여 사용자의 의도를 정확히 파악합니다.
        2. 사용자 요청을 분석하여 템플릿을 적절히 수정합니다.
        3. 변수 형식 `#{{변수명}}`은 반드시 유지합니다.
        4. 템플릿의 기본 구조와 톤앤매너는 유지합니다.
        5. 수정이 필요하지 않으면 현재 템플릿을 그대로 반환합니다.

        ## 현재 템플릿:
        {self.current_template}

        채팅 히스토리:
        {self.chat_context}

        사용자 요청: {self.user_message}

        위 정보를 바탕으로 사용자의 요청에 따라 템플릿을 수정해주세요.

        중요한 규칙:
        1. 기존 템플릿의 구조와 변수는 유지하면서 요청사항을 반영
        2. 변수(#{{변수명}}) 형태는 그대로 유지
        3. 수정된 템플릿만 반환하세요
        4. 설명, 해설, 변경사항 설명 등은 절대 포함하지 마세요
        5. "수정된 템플릿:", "설명:", "변경사항:" 등의 헤더도 사용하지 마세요

        ## 수정된 템플릿:
        응답 형식:
        수정된 템플릿:
        [수정된 템플릿 내용만 여기에 작성]

        예시:
        수정된 템플릿:
        안녕하세요! #{{고객명}}님, 주문이 완료되었습니다. 감사합니다.
        """


class ReferenceBasedTemplatePromptBuilder:
    def __init__(self, request, reference_template):
        self.request = request
        self.reference_template = reference_template
    
    def build(self) -> str:
        """참고 템플릿 기반 생성 프롬프트"""
        return f"""
        다음은 승인받은 카카오톡 알림톡 템플릿입니다:

        === 참고 템플릿 ===
        제목: {self.reference_template['metadata'].get('auto_generated_title', '')}
        분류: {self.reference_template['metadata'].get('category_primary', '')} > {self.reference_template['metadata'].get('category_secondary', '')}
        템플릿: {self.reference_template['text']}
        업종: {self.reference_template['metadata'].get('industry', '')}
        목적: {self.reference_template['metadata'].get('purpose', '')}

        === 새 템플릿 요청 정보 ===
        카테고리 대분류: {self.request.category_main}
        카테고리 소분류: {self.request.category_sub}
        메시지 유형: {self.request.type}
        채널 링크 여부: {self.request.has_channel_link}
        부가 설명 여부: {self.request.has_extra_info}
        라벨: {self.request.label}
        사용 사례: {self.request.use_case}
        의도 유형: {self.request.intent_type}
        수신자 범위: {self.request.recipient_scope}
        링크 허용: {self.request.links_allowed}
        변수: {self.request.variables}
        원본 사용자 텍스트: {self.request.user_text}

        위 참고 템플릿의 구조와 스타일을 따라하되, 새 요청 정보에 맞게 카카오톡 알림톡 템플릿을 생성해주세요.

        중요 규칙:
        1. 변수는 #{{변수명}} 형태로 표현
        2. 광고성 내용 금지, 정보성/안내성 내용만 포함
        3. 발송 근거를 템플릿 하단에 명시 (*표시로 시작)
        4. 참고 템플릿과 유사한 톤앤매너 유지
        5. 버튼이 필요한 경우 #{{버튼명}} 형태로 표시

        템플릿만 생성해주세요:
        """


class PolicyGuidedTemplatePromptBuilder:
    """정책 가이드 기반 템플릿 빌더"""
    def __init__(self, request, guidelines_text):
        self.request = PromptDefense.sanitize_user_input(request)
        self.guidelines_text = PromptDefense.sanitize_user_input(guidelines_text)

    def build(self) -> str:
        return f"""

        === 알림톡 정책 가이드라인 ===
        {self.guidelines_text}

        === 템플릿 생성 요청 ===
        카테고리: {self.request.category_main} > {self.request.category_sub}
        사용 사례: {self.request.use_case}
        의도 유형: {self.request.intent_type}
        수신자 범위: {self.request.recipient_scope}
        원본 메시지: {self.request.user_text}

        위 정책 가이드라인을 엄격히 준수하여 카카오톡 알림톡 템플릿을 생성해주세요.

        중요 사항:
        1. 가이드라인에 명시된 금지사항 절대 포함 금지
        2. 허용된 카테고리와 목적에만 부합하는 내용
        3. 변수는 #{{변수명}} 형태로 표현
        4. 발송 근거를 템플릿 하단에 명시
        5. **절대 변수 목록이나 변수 설명을 템플릿 내용에 포함하지 마세요**
        6. **템플릿은 실제 발송될 메시지 내용만 포함해야 합니다**

        템플릿만 생성해주세요:
        """


class NewTemplatePromptBuilder:
    def __init__(self, request):
        self.request = request
    
    def build(self) -> str:
        """새 템플릿 생성 프롬프트"""
        return f"""
        다음 정보를 바탕으로 카카오톡 알림톡 템플릿을 생성해주세요:

        === 템플릿 요청 정보 ===
        라벨: {self.request.label}
        카테고리: {self.request.category_main} > {self.request.category_sub}
        사용 사례: {self.request.use_case}
        의도 유형: {self.request.intent_type}
        수신자 범위: {self.request.recipient_scope}
        링크 허용: {self.request.links_allowed}
        변수: {self.request.variables}
        원본 메시지: {self.request.user_text}

        카카오톡 알림톡 규정에 맞는 템플릿을 생성해주세요.

        중요 규칙:
        1. 변수는 #{{변수명}} 형태로 표현
        2. 광고성 내용 금지, 정보성/안내성 내용만 포함
        3. 발송 근거를 템플릿 하단에 명시 (*표시로 시작)
        4. 명확하고 간결한 안내 메시지
        5. 버튼이 필요한 경우 #{{버튼명}} 형태로 표시
        6. 수신자가 요청했거나 관련 서비스를 이용하는 경우에만 발송되는 내용
        7. **절대 변수 목록이나 변수 설명을 템플릿 내용에 포함하지 마세요**
        8. **템플릿은 실제 발송될 메시지 내용만 포함해야 합니다**

        템플릿만 생성해주세요:
        """


class TemplateTitlePromptBuilder: 
    def __init__(self, request, template_text):
        self.request = request
        self.template_text = template_text
    
    def build(self) -> str:
        """템플릿 제목 생성 프롬프트"""
        return f"""
        다음 카카오톡 알림톡 템플릿에 대한 간단한 제목을 생성해주세요:

        템플릿: {self.template_text}
        카테고리: {self.request.category_main} > {self.request.category_sub}
        사용 사례: {self.request.use_case}

        제목 규칙:
        1. 10자 이내의 간단한 제목
        2. 템플릿의 주요 목적을 나타내는 제목
        3. "안내", "알림", "발송" 등의 단어 활용

        제목만 생성해주세요:
        """