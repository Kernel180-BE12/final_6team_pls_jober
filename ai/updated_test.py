#!/usr/bin/env python3
"""
수정된 JSON 형태로 템플릿 생성 테스트
"""

from templateEngine.template_generator import TemplateGenerator, TemplateRequest
import json

def main():
    print("=" * 60)
    print("수정된 JSON 형태 템플릿 생성 테스트")
    print("=" * 60)
    
    try:
        generator = TemplateGenerator()
        
        # 새로운 JSON 형태로 테스트
        request = TemplateRequest(
            category_main="이벤트",
            category_sub="교육/특강",
            type="BASIC",
            has_channel_link=False,
            has_extra_info=True,
            label="특강안내",
            use_case="마케팅 특강 일정 및 장소 안내",
            intent_type="information",
            recipient_scope="신청자",
            links_allowed=True,
            variables=["일시", "장소", "링크"],
            section_path=["서비스이용", "이용안내/공지"],
            source="user_request",
            source_tag=None,
            user_text="안녕하세요. 마케팅 리즈입니다. 지난번 공지드린 마케팅 특강이 이번주에 시작합니다. -일시 : 25.11.11(화) 18시 - 장소: 서울 마포구 양화로 186, 6층 참석을 원하시면 미리 답장을 주세요."
        )
        
        print("템플릿 생성 중...")
        result = generator.generate_template(request)
        
        print("성공!")
        print(f"유사도 점수: {result.similarity_score:.3f}")
        print(f"참고 템플릿 사용: {result.reference_used}")
        print(f"생성 방법: {result.generation_method}")
        print(f"템플릿 제목: {result.template_title}")
        print(f"감지된 변수: {result.variables_detected}")
        
        if result.reference_template_id:
            print(f"참고 템플릿 ID: {result.reference_template_id}")
        
        print("\n생성된 템플릿:")
        print("-" * 50)
        print(result.template_text)
        print("-" * 50)
        
        # 최종 JSON 출력 (후속 팀원용)
        output_json = {
            "template_text": result.template_text,
            "template_title": result.template_title,
            "similarity_score": result.similarity_score,
            "reference_used": result.reference_used,
            "reference_template_id": result.reference_template_id,
            "variables_detected": result.variables_detected,
            "generation_method": result.generation_method,
            "metadata": result.metadata
        }
        
        print(f"\n최종 JSON 출력 (후속 팀원용):")
        print("=" * 60)
        print(json.dumps(output_json, ensure_ascii=False, indent=2))
        print("=" * 60)
        
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    main()