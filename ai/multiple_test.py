#!/usr/bin/env python3
"""
여러 시나리오 템플릿 생성 테스트
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.alimtalk_service import AlimtalkValidationService
from models.alimtalk_models import ValidationRequest, AlimtalkTemplate

def main():
    print("=" * 60)
    print("다중 시나리오 알림톡 템플릿 검증 테스트")
    print("=" * 60)
    
    try:
        validation_service = AlimtalkValidationService()
        
        # 테스트 케이스들
        test_cases = [
            {
                "name": "마케팅 특강 안내 (정상 케이스)",
                "template": AlimtalkTemplate(
                    template_pk="TEST_MARKETING_001",
                    channel="alimtalk",
                    title="(광고) 마케팅 특강 안내",
                    body="(광고) 안녕하세요 #{customer_name}님!\n\n마케팅 특강이 시작됩니다.\n- 일시: #{event_date}\n- 장소: #{location}\n\n참석을 원하시면 답장을 주세요.\n\n* 수신거부: 080-000-0000",
                    variables={
                        "customer_name": "홍길동",
                        "event_date": "2024년 1월 15일 18:00",
                        "location": "서울 마포구 양화로 186, 6층"
                    },
                    category="marketing"
                ),
                "user_input": "마케팅 특강 일정 및 장소 안내"
            },
            {
                "name": "배송 완료 안내 (정상 케이스)",
                "template": AlimtalkTemplate(
                    template_pk="TEST_DELIVERY_001",
                    channel="alimtalk",
                    title="배송 완료 안내",
                    body="안녕하세요 #{customer_name}님,\n\n주문하신 상품이 배송 완료되었습니다.\n\n- 상품명: #{product_name}\n- 배송일시: #{delivery_date}\n- 수령인: #{recipient_name}\n\n감사합니다.",
                    variables={
                        "customer_name": "홍길동",
                        "product_name": "스마트폰 케이스",
                        "delivery_date": "2024년 1월 14일 15:30",
                        "recipient_name": "홍길동"
                    },
                    category="transaction"
                ),
                "user_input": "온라인 주문 상품 배송 완료 통지"
            },
            {
                "name": "금칙어 포함 템플릿 (오류 케이스)",
                "template": AlimtalkTemplate(
                    template_pk="TEST_INVALID_001",
                    channel="alimtalk",
                    title="도박 사이트 광고",
                    body="100% 보장된 투자 기회! 무조건 돈을 벌 수 있는 카지노 사이트입니다. 지금 가입하면 무료체험 혜택을 드립니다!",
                    category="marketing"
                ),
                "user_input": "도박 사이트 광고"
            }
        ]
        
        # 각 테스트 케이스 실행
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[테스트 {i}] {test_case['name']}")
            print("-" * 50)
            
            try:
                validation_request = ValidationRequest(
                    template=test_case['template'],
                    user_input=test_case['user_input']
                )
                
                result = validation_service.validate_template(validation_request)
                
                print(f"검증 성공: {result.success}")
                print(f"최종 메시지: {result.final_message}")
                
                if result.validation_results:
                    for j, validation_result in enumerate(result.validation_results, 1):
                        print(f"  {j}단계 - {validation_result.stage}: {'통과' if validation_result.is_valid else '실패'}")
                        if validation_result.errors:
                            print(f"    오류: {validation_result.errors}")
                        if validation_result.warnings:
                            print(f"    경고: {validation_result.warnings}")
                
                # JSON 형태로 출력
                output_json = {
                    "test_name": test_case['name'],
                    "success": result.success,
                    "final_message": result.final_message,
                    "validation_results": [
                        {
                            "stage": vr.stage,
                            "is_valid": vr.is_valid,
                            "errors": vr.errors,
                            "warnings": vr.warnings
                        } for vr in result.validation_results
                    ]
                }
                
                print(f"\nJSON 출력:")
                print(json.dumps(output_json, ensure_ascii=False, indent=2)[:300] + "...")
                
            except Exception as e:
                print(f"오류: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'=' * 60}")
        print("모든 테스트 완료")
        
    except Exception as e:
        print(f"전체 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()