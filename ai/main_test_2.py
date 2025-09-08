import json
import re
import requests
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KakaoBizMessageAPI:
    """카카오 비즈메시지 API 클라이언트 (curl 명령어와 동일한 방식)"""

    def __init__(self, base_url: str, access_token: str):
        self.base_url = base_url
        self.access_token = access_token

    def send_alimtalk(self,
                      sender_key: str,
                      template_code: str,
                      phone_number: str,
                      sender_no: str,
                      message: str,
                      cid: str = None,
                      fall_back_yn: bool = False,
                      fall_back_message_type: str = None,
                      fall_back_message: str = None,
                      buttons: List[Dict] = None) -> Dict[str, Any]:
        """
        알림톡 발송 (curl 명령어와 동일한 방식)
        """
        # CID 자동 생성
        if not cid:
            cid = datetime.now().strftime('%Y%m%d%H%M%S') + str(int(time.time() % 1000))

        # 전화번호 형식 정리 (하이픈 제거, 국가코드 처리)
        clean_phone = re.sub(r'[-\s]', '', phone_number)
        if clean_phone.startswith('010'):
            clean_phone = '82' + clean_phone[1:]
        elif clean_phone.startswith('82010'):
            pass  # 이미 올바른 형식
        elif not clean_phone.startswith('82'):
            clean_phone = '82' + clean_phone

        # 발신번호 형식 정리
        clean_sender = re.sub(r'[-\s]', '', sender_no)

        # API 요청 URL
        url = f"https://{self.base_url}/v2/send/kakao"

        # 요청 헤더 (curl과 동일)
        headers = {
            "accept": "*/*",
            "authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        # 요청 데이터 (curl과 동일한 구조)
        payload = {
            "message_type": "AT",
            "sender_key": sender_key,
            "cid": cid,
            "template_code": template_code,
            "phone_number": clean_phone,
            "sender_no": clean_sender,
            "message": message,
            "fall_back_yn": fall_back_yn
        }

        # 대체발송 설정
        if fall_back_yn and fall_back_message:
            payload["fall_back_message_type"] = fall_back_message_type or "SM"
            payload["fall_back_message"] = fall_back_message

        # 버튼 추가
        if buttons:
            payload["button"] = buttons

        try:
            print(f"=== API 호출 정보 ===")
            print(f"URL: {url}")
            print(f"Headers: {json.dumps(headers, indent=2)}")
            print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            print("=" * 50)

            response = requests.post(
                url=url,
                headers=headers,
                json=payload,
                timeout=30
            )

            print(f"=== API 응답 ===")
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")

            # 응답 처리
            try:
                result = response.json()
                print(f"Response Body: {json.dumps(result, indent=2, ensure_ascii=False)}")
            except:
                result = {"raw_response": response.text}
                print(f"Raw Response: {response.text}")

            if response.status_code == 200:
                logger.info(f"알림톡 발송 성공: CID={cid}")
                return {
                    "success": True,
                    "cid": cid,
                    "response": result
                }
            else:
                logger.error(f"알림톡 발송 실패: {response.status_code}")
                return {
                    "success": False,
                    "error_code": response.status_code,
                    "error_message": result,
                    "cid": cid
                }

        except requests.exceptions.RequestException as e:
            error_msg = f"네트워크 오류: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "cid": cid
            }

class SimpleTemplateProcessor:
    """간단한 템플릿 처리기"""

    def __init__(self):
        # 기본 템플릿들 (실제 승인받은 템플릿 코드로 변경 필요)
        self.templates = {
            "휴무안내": {
                "code": "HOLIDAY_001",  # 실제 템플릿 코드로 변경
                "message": "안녕하세요.\n\n{date}는 휴무일입니다.\n\n감사합니다."
            },
            "회원가입": {
                "code": "SIGNUP_001",  # 실제 템플릿 코드로 변경
                "message": "{name}님의 회원가입이 완료되었습니다.\n\n가입일: {date}\n\n감사합니다."
            },
            "배송시작": {
                "code": "DELIVERY_001",  # 실제 템플릿 코드로 변경
                "message": "주문하신 상품이 배송시작되었습니다.\n\n주문번호: {order_no}\n송장번호: {tracking_no}\n\n감사합니다."
            }
        }

    def get_template(self, template_name: str) -> Dict:
        """템플릿 정보 조회"""
        return self.templates.get(template_name, {})

    def process_message(self, template_name: str, variables: Dict[str, str]) -> Tuple[str, str]:
        """메시지 처리"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"템플릿을 찾을 수 없습니다: {template_name}")

        message = template["message"]
        for key, value in variables.items():
            message = message.replace(f"{{{key}}}", value)

        return template["code"], message

def test_direct_api_call():
    """직접 API 호출 테스트 (curl과 동일한 방식)"""

    # 설정값들 - 실제 값으로 변경 필요
    CONFIG = {
        "base_url": "bizmsg-web.kakaoenterprise.com",  # 또는 해당 환경의 URL
        "access_token": "5241cdfe06275e36cd297c6b3a556e1d",       # 실제 액세스 토큰
        "sender_key": "010-3706-9303",          # 실제 발신 프로필 키
        "sender_no": "010-3706-9303",                    # 실제 발신번호
        "template_code": "TEMPLATE_001"                # 실제 승인받은 템플릿 코드
    }

    # API 클라이언트 생성
    api = KakaoBizMessageAPI(
        base_url=CONFIG["base_url"],
        access_token=CONFIG["access_token"]
    )

    # 테스트 케이스 1: 기본 알림톡 발송
    print("=== 테스트 1: 기본 알림톡 발송 ===")
    result1 = api.send_alimtalk(
        sender_key=CONFIG["sender_key"],
        template_code=CONFIG["template_code"],
        phone_number="010-1234-5678",  # 테스트용 번호
        sender_no=CONFIG["sender_no"],
        message="알림톡 테스트 메시지입니다.",
        cid="TEST202410181600001"
    )
    print(f"결과 1: {json.dumps(result1, indent=2, ensure_ascii=False)}")

    # 테스트 케이스 2: 대체발송 포함
    print("\n=== 테스트 2: 대체발송 포함 ===")
    result2 = api.send_alimtalk(
        sender_key=CONFIG["sender_key"],
        template_code=CONFIG["template_code"],
        phone_number="010-9876-5432",  # 테스트용 번호
        sender_no=CONFIG["sender_no"],
        message="대체발송 테스트 알림톡 메시지입니다.",
        fall_back_yn=True,
        fall_back_message_type="SM",
        fall_back_message="대체발송 SMS 메시지입니다."
    )
    print(f"결과 2: {json.dumps(result2, indent=2, ensure_ascii=False)}")

    # 테스트 케이스 3: 버튼 포함
    print("\n=== 테스트 3: 버튼 포함 ===")
    buttons = [
        {
            "name": "자세히보기",
            "type": "WL",
            "url_mobile": "https://example.com",
            "url_pc": "https://example.com"
        }
    ]

    result3 = api.send_alimtalk(
        sender_key=CONFIG["sender_key"],
        template_code=CONFIG["template_code"],
        phone_number="010-5555-6666",  # 테스트용 번호
        sender_no=CONFIG["sender_no"],
        message="버튼이 포함된 알림톡 메시지입니다.",
        buttons=buttons
    )
    print(f"결과 3: {json.dumps(result3, indent=2, ensure_ascii=False)}")

def create_simple_sender(base_url: str, access_token: str, sender_key: str, sender_no: str):
    """간단한 발송 함수 생성기"""

    api = KakaoBizMessageAPI(base_url, access_token)

    def send_message(template_code: str, phone_number: str, message: str, **kwargs):
        """메시지 발송 간편 함수"""
        return api.send_alimtalk(
            sender_key=sender_key,
            template_code=template_code,
            phone_number=phone_number,
            sender_no=sender_no,
            message=message,
            **kwargs
        )

    return send_message

# 사용 예시
if __name__ == "__main__":

    # 방법 1: 직접 API 테스트
    print("카카오 비즈메시지 API 직접 호출 테스트")
    print("⚠️ 실제 사용 전에 CONFIG의 모든 값을 실제 값으로 변경하세요!")
    print()

    # 설정 확인 메시지
    print("다음 설정값들을 실제 값으로 변경해야 합니다:")
    print("1. access_token: OAuth 2.0으로 발급받은 액세스 토큰")
    print("2. sender_key: 비즈 사이트에서 발급받은 발신 프로필 키")
    print("3. sender_no: 등록된 발신 전화번호")
    print("4. template_code: 승인받은 알림톡 템플릿 코드")
    print("5. phone_number: 실제 수신할 전화번호")
    print()

    # 설정값이 더미값이 아닌 경우에만 테스트 실행
    test_config = {
        "base_url": "bizmsg-web.kakaoenterprise.com",
        "access_token": "5241cdfe06275e36cd297c6b3a556e1d",  # 여기를 실제 토큰으로 변경
        "sender_key": "01037069303",      # 여기를 실제 발신키로 변경
        "sender_no": "010-3706-9303",                # 여기를 실제 발신번호로 변경
        "template_code": "TEMPLATE_001"            # 여기를 실제 템플릿 코드로 변경
    }

    if "YOUR_" not in test_config["access_token"]:
        # 실제 설정값이 있을 때만 테스트 실행
        test_direct_api_call()
    else:
        print("실제 설정값으로 변경 후 테스트를 진행하세요.")

        # 설정 예시 코드
        print("\n=== 실제 사용 예시 코드 ===")
        example_code = '''
# 실제 사용 시 코드 예시
api = KakaoBizMessageAPI(
    base_url="bizmsg-web.kakaoenterprise.com",
    access_token="실제_액세스_토큰"
)

result = api.send_alimtalk(
    sender_key="실제_발신프로필키",
    template_code="실제_템플릿코드", 
    phone_number="010-1234-5678",
    sender_no="02-1234-5678",
    message="실제 알림톡 메시지 내용"
)

print(result)
        '''
        print(example_code)