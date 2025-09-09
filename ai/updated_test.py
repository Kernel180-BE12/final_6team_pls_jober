#!/usr/bin/env python3
"""
수정된 JSON 형태로 템플릿 생성 테스트
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.alimtalk_service import AlimtalkValidationService
from models.alimtalk_models import ValidationRequest, AlimtalkTemplate

def main():
    print("=" * 60)
    print("알림톡 템플릿 검증 테스트")
    print("=" * 60)
    
    try:
        # 알림톡 검증 서비스 초기화
        validation_service = AlimtalkValidationService()
        
        # 테스트용 템플릿 생성
        test_template = AlimtalkTemplate(
            template_pk="TEST_001",
            channel="alimtalk",
            title="마케팅 특강 안내",
            body="안녕하세요 #{customer_name}님!\n\n마케팅 특강이 시작됩니다.\n- 일시: #{event_date}\n- 장소: #{location}\n\n참석을 원하시면 답장을 주세요.",
            variables={
                "customer_name": "홍길동",
                "event_date": "2024년 1월 15일 18:00",
                "location": "서울 마포구 양화로 186, 6층"
            },
            category="marketing"
        )
        
        # 검증 요청 생성
        validation_request = ValidationRequest(
            template=test_template,
            user_input="마케팅 특강 일정 및 장소 안내"
        )
        
        print("템플릿 검증 중...")
        result = validation_service.validate_template(validation_request)
        
        print("검증 완료!")
        print(f"검증 성공: {result.success}")
        print(f"최종 메시지: {result.final_message}")
        
        if result.validation_results:
            print(f"검증 결과 수: {len(result.validation_results)}")
            for i, validation_result in enumerate(result.validation_results, 1):
                print(f"  {i}단계 - {validation_result.stage}: {'통과' if validation_result.is_valid else '실패'}")
                if validation_result.errors:
                    print(f"    오류: {validation_result.errors}")
                if validation_result.warnings:
                    print(f"    경고: {validation_result.warnings}")
        
        # 최종 JSON 출력
        output_json = {
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
        
        print(f"\n최종 JSON 출력:")
        print("=" * 60)
        print(json.dumps(output_json, ensure_ascii=False, indent=2))
        print("=" * 60)
        
    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()