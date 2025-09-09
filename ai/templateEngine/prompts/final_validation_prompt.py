"""
최종 검증용 GPT 프롬프트 템플릿
"""
import json
from typing import Dict, Any, List


class FinalValidationPromptBuilder:
    def __init__(self, template_data: Dict[str, Any], det_report_summary: Dict[str, Any], 
                 rag_guidelines: List[Dict[str, Any]], template_pk: str = None):
        self.template_data = template_data
        self.det_report_summary = det_report_summary
        self.rag_guidelines = rag_guidelines
        self.template_pk = template_pk
    
    def build(self) -> str:
        """최종 검증용 프롬프트 생성"""
        # RAG 가이드라인 문서 구성
        rag_context = self._build_rag_context()
        
        return f"""[system]
너는 카카오 알림톡 최종 검증 담당자이다.
- 정책적 검사 결과(det_report)와 정책 컨텍스트(RAG 문서)가 구체 공지.
- 결과는 '통력' 스키마의 JSON만 반환(설명/마크업 그런 공지).
- 기능적인 자동 수정(autofix.patch_body)을 제안하되, 원문의 의미는 유지한다.

[user]
# template_pk
{self.template_pk or self.template_data.get('template_pk', self.template_data.get('id', 'unknown'))}

# 접점 대상 템플릿(JSON)
{json.dumps(self.template_data, ensure_ascii=False, indent=2)}

# 정책적 검사 요약(2차 검증 코드 결과)  
{json.dumps(self.det_report_summary, ensure_ascii=False, indent=2)}

# 정책/가이드 컨텍스트 (RAG Top-K))
{rag_context}

# 평가 기준
- CRITICAL 0건 AND MAJOR ≤ 1건이면 passed=true, 그 외 false.

# 출력 스키마(JSON만 출력)
{{
"passed": boolean,
"summary": "string", 
"violations": [
  {{
    "rule_id": "string",
    "severity": "CRITICAL|MAJOR|MINOR",
    "evidence": "string",
    "policy_ref": "string",
    "span": [startIndex, endIndex]
  }}
],
"autofix": {{
  "enabled": boolean,
  "patch_body": "string", 
  "notes": "string"
}},
"policy_refs": ["string"]
}}"""
    
    def _build_rag_context(self) -> str:
        """RAG 가이드라인 문서 구성"""
        if self.rag_guidelines:
            rag_docs = []
            for i, guideline in enumerate(self.rag_guidelines[:5]):
                title = guideline.get('title', guideline.get('metadata', {}).get('category', '정책'))
                content = guideline.get('content', '')[:100]
                doc_type = guideline.get('metadata', {}).get('type', 'policy')
                
                rag_docs.append(
                    f"[DOC:pol-{i+231}] type={doc_type}, title=\"{title}\", excerpt=\"{content}...\""
                )
            return "\n".join(rag_docs)
        else:
            # 기본 예시 문서
            return """[DOC:pol-231] type=policy, title="심사가이드 5장", excerpt="과장·기만 금지..."
[DOC:tpl-882] type=approved_template, title="승인된-배송완료", excerpt="주문하신 상품이 배송완료되었습니다..."
{order_no}..."""


def create_final_validation_prompt(
    template_data: Dict[str, Any],
    det_report_summary: Dict[str, Any], 
    rag_guidelines: List[Dict[str, Any]],
    template_pk: str = None
) -> str:
    """
    최종 검증용 프롬프트 생성 (기존 함수 호환성 유지)
    
    Args:
        template_data: 검증할 템플릿 데이터
        det_report_summary: 2차 검증 결과 요약
        rag_guidelines: RAG에서 가져온 가이드라인 목록
        template_pk: 템플릿 Primary Key
        
    Returns:
        str: 완성된 프롬프트
    """
    builder = FinalValidationPromptBuilder(template_data, det_report_summary, rag_guidelines, template_pk)
    return builder.build()


def get_prompt_examples():
    """프롬프트 사용 예시"""
    
    # 예시 템플릿 데이터
    example_template = {
        "template_pk": "TPL_20241201_001",
        "channel": "alimtalk",
        "title": "주문 배송 완료 안내",
        "body": "안녕하세요 #{customer_name}님,\n\n주문하신 상품이 배송 완료되었습니다.\n주문번호: #{order_no}\n\n감사합니다.",
        "variables": {
            "customer_name": "홍길동",
            "order_no": "ORD-20241201-001"
        },
        "category": "transaction",
        "buttons": []
    }
    
    # 예시 2차 검증 결과
    example_det_report = {
        "constraint_passed": True,
        "issues_found": [],
        "warnings": ["변수명 일관성 체크 권장"]
    }
    
    # 예시 RAG 가이드라인
    example_guidelines = [
        {
            "content": "거래성 알림톡은 광고성 표현을 포함해서는 안됩니다. 단순한 거래 정보 전달에 집중해야 합니다.",
            "title": "거래성 알림톡 가이드",
            "metadata": {"category": "transaction", "type": "policy", "priority": "high"}
        },
        {
            "content": "고객명과 주문번호는 변수 처리하여 개인정보를 보호해야 합니다.",
            "title": "개인정보 보호 가이드", 
            "metadata": {"category": "privacy", "type": "policy", "priority": "critical"}
        }
    ]
    
    return {
        "template_data": example_template,
        "det_report_summary": example_det_report,
        "rag_guidelines": example_guidelines,
        "template_pk": "TPL_20241201_001"
    }


if __name__ == "__main__":
    # 테스트 실행
    examples = get_prompt_examples()
    prompt = create_final_validation_prompt(**examples)
    
    print("=== 최종 검증 프롬프트 ===")
    print(prompt)
    print("\n=== 프롬프트 길이 ===")
    print(f"총 길이: {len(prompt)} 문자")
