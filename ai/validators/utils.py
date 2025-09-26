"""
검증기 유틸리티 함수들
"""
import re
from typing import List


def extract_variables_from_template(template_content: str) -> List[str]:
    """
    템플릿 내용에서 변수를 추출합니다.
    
    Args:
        template_content: 템플릿 텍스트 내용
        
    Returns:
        List[str]: 추출된 변수명 리스트 (중복 제거됨)
    """
    if not template_content:
        return []
    
    # #{변수명} 패턴만 추출 (통일된 형태)
    detected_variables = re.findall(r'#\{([^}]+)\}', template_content)
    return list(set(detected_variables))
