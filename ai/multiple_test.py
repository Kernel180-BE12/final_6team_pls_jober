#!/usr/bin/env python3
"""
여러 시나리오 템플릿 생성 테스트
"""

from templateEngine.template_generator import TemplateGenerator, TemplateRequest
import json

def main():
    print("=" * 60)
    print("다중 시나리오 템플릿 생성 테스트")
    print("=" * 60)
    
    try:
        generator = TemplateGenerator()
        
        # 테스트 케이스들
        test_cases = [
            {
                "name": "마케팅 특강 안내 (유사도 높을 예상)",
                "request": TemplateRequest(
                    label="이벤트/특강안내",
                    category="이벤트",
                    use_case="마케팅 특강 일정 및 장소 안내", 
                    intent_type="information",
                    recipient_scope="신청자",
                    links_allowed=True,
                    variables=["일시", "장소", "링크"],
                    section_path=["서비스이용", "이용안내/공지"],
                    source="user_request",
                    original_message="안녕하세요. 마케팅 리즈입니다. 지난번 공지드린 마케팅 특강이 이번주에 시작합니다. -일시 : 25.11.11(화) 18시 - 장소: 서울 마포구 양화로 186, 6층 참석을 원하시면 미리 답장을 주세요."
                )
            },
            {
                "name": "배송 완료 안내 (유사도 낮을 예상)",
                "request": TemplateRequest(
                    label="배송완료",
                    category="배송",
                    use_case="온라인 주문 상품 배송 완료 통지",
                    intent_type="notification",
                    recipient_scope="주문고객",
                    links_allowed=True,
                    variables=["고객명", "상품명", "운송장번호"],
                    section_path=["주문/배송", "배송현황"],
                    source="delivery_system",
                    original_message="주문하신 상품이 배송 완료되었습니다. 상품명: 스마트폰 케이스 배송일시: 2024.12.14 15:30 받으신 분: 홍길동"
                )
            },
            {
                "name": "예약 완료 안내 (유사도 높을 예상)",
                "request": TemplateRequest(
                    label="예약완료",
                    category="예약",
                    use_case="상담 예약 완료 알림",
                    intent_type="confirmation", 
                    recipient_scope="예약자",
                    links_allowed=False,
                    variables=["고객명", "예약일시", "위치"],
                    section_path=["예약", "예약완료"],
                    source="booking_system",
                    original_message="안녕하세요. 상담 예약을 해주셔서 감사합니다. 예약 내용을 안내드립니다. 일정: 2024.12.15 14시 위치: 서울시 강남구"
                )
            }
        ]
        
        # 각 테스트 케이스 실행
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[테스트 {i}] {test_case['name']}")
            print("-" * 50)
            
            try:
                result = generator.generate_template(test_case['request'])
                
                print(f"유사도 점수: {result.similarity_score:.3f}")
                print(f"참고 템플릿 사용: {result.reference_used}")
                print(f"생성 방법: {result.generation_method}")
                print(f"규정 준수: {result.compliance_status}")
                
                if result.reference_template_id:
                    print(f"참고 템플릿 ID: {result.reference_template_id}")
                
                print(f"\n생성된 템플릿:")
                print(result.template_text[:200] + "..." if len(result.template_text) > 200 else result.template_text)
                
                # JSON 형태로도 출력 (후속 팀원을 위한 형식)
                output_json = {
                    "template_text": result.template_text,
                    "template_title": result.template_title,
                    "similarity_score": result.similarity_score,
                    "reference_used": result.reference_used,
                    "variables_detected": result.variables_detected,
                    "compliance_status": result.compliance_status,
                    "generation_method": result.generation_method
                }
                
                print(f"\nJSON 출력 (후속 팀원용):")
                print(json.dumps(output_json, ensure_ascii=False, indent=2)[:300] + "...")
                
            except Exception as e:
                print(f"오류: {e}")
        
        print(f"\n{'=' * 60}")
        print("모든 테스트 완료")
        
    except Exception as e:
        print(f"전체 오류: {e}")

if __name__ == "__main__":
    main()