import json
import re
import requests
import base64
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KakaoOAuthClient:
    """카카오 OAuth 2.0 인증 클라이언트"""
    
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = None
    
    def _create_basic_auth_header(self) -> str:
        """Basic 인증 헤더 생성"""
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return f"Basic {encoded_credentials}"
    
    def get_access_token(self, force_refresh: bool = False) -> str:
        """액세스 토큰 발급/갱신"""
        
        # 토큰이 유효하고 강제 갱신이 아닌 경우 기존 토큰 반환
        if (not force_refresh and 
            self.access_token and 
            self.token_expires_at and 
            datetime.now() < self.token_expires_at):
            return self.access_token
        
        # OAuth 2.0 토큰 요청 URL
        url = f"https://{self.base_url}/v2/oauth/token"
        
        # 헤더 설정 (JavaScript 코드와 동일)
        headers = {
            "Authorization": self._create_basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # 요청 데이터 (JavaScript 코드와 동일)
        data = {
            "grant_type": "client_credentials"
        }
        
        try:
            print(f"=== OAuth 2.0 토큰 요청 ===")
            print(f"URL: {url}")
            print(f"Headers: {headers}")
            print(f"Data: {data}")
            print("=" * 50)
            
            response = requests.post(
                url=url,
                headers=headers,
                data=data,  # application/x-www-form-urlencoded 형식
                timeout=30
            )
            
            print(f"=== OAuth 응답 ===")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                token_data = response.json()
                
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)  # 기본 1시간
                
                # 토큰 만료 시간 설정 (여유를 위해 5분 일찍)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
                
                logger.info(f"액세스 토큰 발급 성공: {self.access_token[:20]}...")
                return self.access_token
            else:
                error_msg = f"OAuth 인증 실패: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"OAuth 요청 실패: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

class KakaoBizMessageAPI:
    """카카오 비즈메시지 API 클라이언트"""
    
    def __init__(self, base_url: str, oauth_client: KakaoOAuthClient):
        self.base_url = base_url
        self.oauth_client = oauth_client
    
    def _get_valid_token(self) -> str:
        """유효한 액세스 토큰 획득"""
        return self.oauth_client.get_access_token()
    
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
        """알림톡 발송"""
        
        # 액세스 토큰 획득
        access_token = self._get_valid_token()
        
        # CID 자동 생성
        if not cid:
            cid = datetime.now().strftime('%Y%m%d%H%M%S') + str(int(time.time() % 1000))
        
        # 전화번호 형식 정리
        clean_phone = re.sub(r'[-\s]', '', phone_number)
        if clean_phone.startswith('010'):
            clean_phone = '82' + clean_phone[1:]
        elif not clean_phone.startswith('82'):
            clean_phone = '82' + clean_phone
            
        # 발신번호 형식 정리
        clean_sender = re.sub(r'[-\s]', '', sender_no)
        
        # API 요청 URL
        url = f"https://{self.base_url}/v2/send/kakao"
        
        # 요청 헤더
        headers = {
            "accept": "*/*",
            "authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # 요청 데이터
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
            print(f"=== 알림톡 발송 요청 ===")
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
            
            print(f"=== 알림톡 발송 응답 ===")
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

class KakaoBizMessageService:
    """카카오 비즈메시지 통합 서비스"""
    
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        self.base_url = base_url
        self.oauth_client = KakaoOAuthClient(base_url, client_id, client_secret)
        self.api_client = KakaoBizMessageAPI(base_url, self.oauth_client)
    
    def send_message(self, 
                    sender_key: str,
                    template_code: str,
                    phone_number: str, 
                    sender_no: str,
                    message: str,
                    **kwargs) -> Dict[str, Any]:
        """메시지 발송 (OAuth 인증 자동 처리)"""
        
        try:
            # OAuth 인증 및 알림톡 발송을 한 번에 처리
            result = self.api_client.send_alimtalk(
                sender_key=sender_key,
                template_code=template_code,
                phone_number=phone_number,
                sender_no=sender_no,
                message=message,
                **kwargs
            )
            
            return result
            
        except Exception as e:
            logger.error(f"메시지 발송 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# 템플릿 처리기 (기존과 동일)
class TemplateProcessor:
    """템플릿 처리기"""
    
    def __init__(self):
        self.templates = {
            "휴무안내": {
                "code": "HOLIDAY_001",
                "message": "안녕하세요 {company}입니다.\n\n{date}는 휴무일입니다.\n\n감사합니다."
            },
            "회원가입": {
                "code": "SIGNUP_001",  
                "message": "{name}님의 회원가입이 완료되었습니다.\n\n가입일: {date}\n\n감사합니다."
            },
            "배송시작": {
                "code": "DELIVERY_001",
                "message": "주문하신 상품이 배송시작되었습니다.\n\n주문번호: {order_no}\n송장번호: {tracking_no}\n\n감사합니다."
            }
        }
    
    def process_template(self, template_name: str, variables: Dict[str, str]) -> Tuple[str, str]:
        """템플릿 처리"""
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"템플릿을 찾을 수 없습니다: {template_name}")
        
        message = template["message"]
        for key, value in variables.items():
            message = message.replace(f"{{{key}}}", value)
        
        return template["code"], message

def test_oauth_and_message():
    """OAuth 인증 + 알림톡 발송 통합 테스트"""
    
    # 설정값 - 실제 값으로 변경 필요
    CONFIG = {
        "base_url": "bizmsg-api.kakaoenterprise.com",      # 또는 해당 환경 URL
        "client_id": "5241cdfe06275e36cd297c6b3a556e1d",                # OAuth 클라이언트 ID  
        "client_secret": "fseXoP8GJLFVNwa6LicM02F3ihtv93ui",        # OAuth 클라이언트 시크릿
        "sender_key": "010-3706-9303",              # 발신 프로필 키
        "sender_no": "010-3706-9303",                        # 발신번호
        "template_code": "TEMPLATE_001"                    # 템플릿 코드
    }
    
    # 서비스 초기화
    service = KakaoBizMessageService(
        base_url=CONFIG["base_url"],
        client_id=CONFIG["client_id"],
        client_secret=CONFIG["client_secret"]
    )
    
    # 테스트 케이스들
    test_cases = [
        {
            "name": "기본 알림톡",
            "phone": "010-1234-5678",
            "message": "OAuth 인증 후 알림톡 발송 테스트입니다."
        },
        {
            "name": "대체발송 포함",
            "phone": "010-9876-5432", 
            "message": "대체발송이 포함된 알림톡입니다.",
            "fall_back_yn": True,
            "fall_back_message": "SMS 대체발송 메시지입니다."
        },
        {
            "name": "버튼 포함",
            "phone": "010-5555-6666",
            "message": "버튼이 포함된 알림톡입니다.",
            "buttons": [
                {
                    "name": "자세히보기",
                    "type": "WL",
                    "url_mobile": "https://example.com",
                    "url_pc": "https://example.com"
                }
            ]
        }
    ]
    
    # 각 테스트 실행
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*20} 테스트 {i}: {test_case['name']} {'='*20}")
        
        # 기본 파라미터
        params = {
            "sender_key": CONFIG["sender_key"],
            "template_code": CONFIG["template_code"], 
            "phone_number": test_case["phone"],
            "sender_no": CONFIG["sender_no"],
            "message": test_case["message"]
        }
        
        # 추가 파라미터
        for key in ["fall_back_yn", "fall_back_message", "buttons"]:
            if key in test_case:
                params[key] = test_case[key]
        
        # 메시지 발송
        result = service.send_message(**params)
        
        print(f"\n결과: {json.dumps(result, indent=2, ensure_ascii=False)}")

# 간편 사용 함수
def create_kakao_sender(base_url: str, client_id: str, client_secret: str, 
                       sender_key: str, sender_no: str):
    """카카오 메시지 발송기 생성"""
    
    service = KakaoBizMessageService(base_url, client_id, client_secret)
    
    def send(template_code: str, phone_number: str, message: str, **kwargs):
        return service.send_message(
            sender_key=sender_key,
            template_code=template_code,
            phone_number=phone_number,
            sender_no=sender_no,
            message=message,
            **kwargs
        )
    
    return send

# 사용 예시
if __name__ == "__main__":
    print("카카오 비즈메시지 OAuth + 알림톡 발송 통합 시스템")
    print("=" * 60)
    print()
    
    print("⚠️ 실제 사용 전 다음 설정값들을 변경하세요:")
    print("1. client_id: OAuth 클라이언트 ID")
    print("2. client_secret: OAuth 클라이언트 시크릿") 
    print("3. sender_key: 발신 프로필 키")
    print("4. sender_no: 발신 전화번호")
    print("5. template_code: 승인받은 템플릿 코드")
    print()
    
    # 실제 설정값 예시
    example_config = {
        "base_url": "bizmsg-web.kakaoenterprise.com", # bizmsg-web.kakaoenterprise.com: 콘솔용 API
        "client_id": "5241cdfe06275e36cd297c6b3a556e1d",        # 실제 클라이언트 ID로 변경
        "client_secret": "fseXoP8GJLFVNwa6LicM02F3ihtv93ui", # 실제 클라이언트 시크릿으로 변경
        "sender_key": "YOUR_SENDER_KEY_HERE",       # 실제 발신 프로필 키로 변경
        "sender_no": "010-3706-9303",                # 실제 발신번호로 변경
        "template_code": "TEMPLATE_001"             # 실제 템플릿 코드로 변경
    }
    
    if "YOUR_" not in example_config["client_id"]:
        # 실제 설정값이 있는 경우 테스트 실행
        test_oauth_and_message()
    else:
        print("=== 사용 예시 코드 ===")
        example_usage = '''
# 1. 서비스 초기화
service = KakaoBizMessageService(
    base_url="bizmsg-api.kakaoenterprise.com",
    client_id="실제_클라이언트_ID",
    client_secret="실제_클라이언트_시크릿"
)

# 2. 메시지 발송 (OAuth 자동 처리)
result = service.send_message(
    sender_key="실제_발신프로필키",
    template_code="실제_템플릿코드",
    phone_number="010-1234-5678",
    sender_no="02-1234-5678", 
    message="알림톡 메시지 내용"
)

# 3. 결과 확인
print(result)

# 4. 간편 사용법
sender = create_kakao_sender(
    base_url="bizmsg-api.kakaoenterprise.com",
    client_id="실제_클라이언트_ID",
    client_secret="실제_클라이언트_시크릿",
    sender_key="실제_발신프로필키", 
    sender_no="02-1234-5678"
)

# 발송
result = sender("TEMPLATE_001", "010-1234-5678", "메시지 내용")
        '''
        print(example_usage)