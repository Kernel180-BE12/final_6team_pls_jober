"""
템플릿 정리 서비스
생성된 템플릿에서 불필요한 부분을 제거하고 실제 템플릿 내용만 추출
"""

import re
import logging

logger = logging.getLogger(__name__)

class TemplateCleanupService:
    """템플릿 정리 서비스"""
    
    @staticmethod
    def clean_template_content(template_content: str) -> str:
        """
        템플릿 내용에서 대안 제안 부분을 제거하고 실제 템플릿 내용만 추출
        
        Args:
            template_content: 원본 템플릿 내용
            
        Returns:
            str: 정리된 템플릿 내용
        """
        if not template_content:
            return template_content
        
        # 대안 제안 패턴들을 제거
        patterns_to_remove = [
            r'대안\d+-\d+:\s*\[구체적인 수정 방향\]\s*-\s*',  # "대안1-1: [구체적인 수정 방향] - " 패턴
            r'대안\d+-\d+:\s*\[.*?\]\s*-\s*',  # "대안1-1: [어떤 내용] - " 패턴
            r'대안\d+-\d+:\s*.*?-\s*',  # "대안1-1: 어떤 내용 - " 패턴
        ]
        
        cleaned_content = template_content
        
        for pattern in patterns_to_remove:
            cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.MULTILINE)
        
        # 연속된 공백과 줄바꿈 정리
        cleaned_content = re.sub(r'\n\s*\n', '\n\n', cleaned_content)
        cleaned_content = re.sub(r'^\s+|\s+$', '', cleaned_content, flags=re.MULTILINE)
        
        logger.info(f"템플릿 정리 완료: {len(template_content)}자 → {len(cleaned_content)}자")
        
        return cleaned_content
    
    @staticmethod
    def extract_clean_template_from_response(response: str) -> str:
        """
        LLM 응답에서 실제 템플릿 내용만 추출
        
        Args:
            response: LLM 응답 텍스트
            
        Returns:
            str: 정리된 템플릿 내용
        """
        if not response:
            return response
        
        # 먼저 대안 제안 부분 제거
        cleaned = TemplateCleanupService.clean_template_content(response)
        
        # 추가적인 정리 작업들
        # 1. JSON 블록 제거 (있다면)
        cleaned = re.sub(r'```json\s*.*?\s*```', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'```\s*.*?\s*```', '', cleaned, flags=re.DOTALL)
        
        # 2. 설명 텍스트 제거 (예: "다음은 수정된 템플릿입니다:")
        explanation_patterns = [
            r'다음은.*?템플릿입니다:?\s*',
            r'수정된.*?템플릿:?\s*',
            r'생성된.*?템플릿:?\s*',
            r'템플릿.*?내용:?\s*',
        ]
        
        for pattern in explanation_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # 3. 최종 정리
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned
