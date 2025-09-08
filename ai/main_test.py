import json
import re
import requests
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TemplateType(Enum):
    """공용 템플릿 타입"""
    OPERATION_NOTICE = "운영_안내"
    MEMBER_SIGNUP = "회원_가입"
    RESERVATION = "예약_안내"
    DELIVERY = "배송_안내"
    ORDER = "주문_안내"
    NOTICE = "공지_안내"
    SERVICE_CHECK = "서비스_점검"
    DORMANT_ACCOUNT = "휴면_계정"
    PARTICIPATION = "참여_결과"
    POINT = "포인트_안내"
    TERMS = "약관_변경"

@dataclass
class Button:
    """버튼 정보"""
    name: str
    type: str  # WL(웹링크), AL(앱링크), DS(배송조회), BK(봇키워드), MD(메시지전달)
    url_mobile: Optional[str] = None
    url_pc: Optional[str] = None
    scheme_android: Optional[str] = None
    scheme_ios: Optional[str] = None

@dataclass
class QuickReply:
    """바로가기 버튼"""
    name: str
    type: str
    url_mobile: Optional[str] = None
    url_pc: Optional[str] = None
    scheme_android: Optional[str] = None
    scheme_ios: Optional[str] = None

@dataclass
class MessageRequest:
    """메시지 발송 요청 데이터"""
    message_type: str = "AT"
    sender_key: str = ""
    cid: str = ""
    template_code: str = ""
    phone_number: str = ""
    sender_no: str = ""
    message: str = ""
    fall_back_yn: bool = False
    fall_back_message_type: Optional[str] = None
    fall_back_title: Optional[str] = None
    fall_back_message: Optional[str] = None
    buttons: Optional[List[Button]] = None
    quick_replies: Optional[List[QuickReply]] = None
    title: Optional[str] = None
    header: Optional[str] = None
    price: Optional[int] = None
    currency_type: str = "KRW"

class TemplateManager:
    """공용 템플릿 관리"""
    
    def __init__(self):
        self.templates = {
            # 운영 안내
            "休무_안내": {
                "code": "COMMON_HOLIDAY_001",
                "message": "안녕하세요 ${업체명}입니다.\n\n${날짜}은 휴무일로 운영하지 않습니다.\n불편을 드려 죄송합니다.\n\n감사합니다.",
                "variables": ["업체명", "날짜"]
            },
            "운영시간_변경": {
                "code": "COMMON_OPERATION_001", 
                "message": "안녕하세요 ${업체명}입니다.\n\n운영시간이 ${변경일}부터 ${변경시간}으로 변경됩니다.\n\n이용에 참고 부탁드립니다.\n감사합니다.",
                "variables": ["업체명", "변경일", "변경시간"]
            },
            # 회원 가입
            "회원가입_완료": {
                "code": "COMMON_SIGNUP_001",
                "message": "안녕하세요 ${업체명}입니다.\n\n${고객명}님의 회원가입이 완료되었습니다.\n\n가입일: ${가입일}\n\n앞으로도 저희 서비스를 이용해 주세요.\n감사합니다.",
                "variables": ["업체명", "고객명", "가입일"]
            },
            "회원가입_혜택": {
                "code": "COMMON_SIGNUP_002",
                "message": "안녕하세요 ${업체명}입니다.\n\n${고객명}님 회원가입을 축하드립니다!\n\n🎁 신규가입 혜택\n- ${혜택내용}\n\n감사합니다.",
                "variables": ["업체명", "고객명", "혜택내용"]
            },
            # 예약 안내
            "예약_완료": {
                "code": "COMMON_RESERVATION_001",
                "message": "안녕하세요 ${업체명}입니다.\n\n${고객명}님의 예약이 완료되었습니다.\n\n예약일시: ${예약일시}\n예약내용: ${예약내용}\n\n감사합니다.",
                "variables": ["업체명", "고객명", "예약일시", "예약내용"]
            },
            "예약_취소": {
                "code": "COMMON_RESERVATION_002",
                "message": "안녕하세요 ${업체명}입니다.\n\n${고객명}님의 예약이 취소되었습니다.\n\n취소일시: ${취소일시}\n원예약: ${예약내용}\n\n감사합니다.",
                "variables": ["업체명", "고객명", "취소일시", "예약내용"]
            },
            # 배송 안내
            "발송준비": {
                "code": "COMMON_DELIVERY_001",
                "message": "안녕하세요 ${업체명}입니다.\n\n주문하신 상품의 발송준비가 시작되었습니다.\n\n주문번호: ${주문번호}\n상품명: ${상품명}\n\n곧 발송될 예정입니다.\n감사합니다.",
                "variables": ["업체명", "주문번호", "상품명"]
            },
            "배송시작": {
                "code": "COMMON_DELIVERY_002", 
                "message": "안녕하세요 ${업체명}입니다.\n\n주문하신 상품이 배송 시작되었습니다.\n\n주문번호: ${주문번호}\n송장번호: ${송장번호}\n배송업체: ${배송업체}\n\n감사합니다.",
                "variables": ["업체명", "주문번호", "송장번호", "배송업체"]
            },
            "배송완료": {
                "code": "COMMON_DELIVERY_003",
                "message": "안녕하세요 ${업체명}입니다.\n\n주문하신 상품이 배송완료되었습니다.\n\n주문번호: ${주문번호}\n배송완료일: ${배송완료일}\n\n상품을 확인해 주세요.\n감사합니다.",
                "variables": ["업체명", "주문번호", "배송완료일"]
            }
        }
    
    def get_template(self, template_name: str) -> Optional[Dict]:
        """템플릿 정보 조회"""
        return self.templates.get(template_name)
    
    def find_template_by_intent(self, text: str) -> Optional[str]:
        """텍스트 의도 분석으로 템플릿 찾기"""
        text_lower = text.lower()
        
        # 키워드 기반 템플릿 매칭
        keyword_mapping = {
            '휴무': '휴무_안내',
            '운영시간': '운영시간_변경',
            '회원가입': '회원가입_완료',
            '가입': '회원가입_완료',
            '예약완료': '예약_완료',
            '예약': '예약_완료',
            '예약취소': '예약_취소',
            '취소': '예약_취소',
            '발송준비': '발송준비',
            '배송시작': '배송시작',
            '배송완료': '배송완료',
            '배송': '배송시작'
        }
        
        for keyword, template_name in keyword_mapping.items():
            if keyword in text_lower:
                return template_name
        
        return None

class ParameterExtractor:
    """파라미터 추출기"""
    
    @staticmethod
    def extract_phone_number(text: str) -> Optional[str]:
        """전화번호 추출"""
        patterns = [
            r'(\+82|82)?[-\s]?0?1[0-9][-\s]?\d{3,4}[-\s]?\d{4}',
            r'(\+82|82)?[-\s]?0[2-9][0-9]?[-\s]?\d{3,4}[-\s]?\d{4}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                phone = re.sub(r'[-\s]', '', match.group())
                if not phone.startswith('82'):
                    phone = '82' + phone[1:] if phone.startswith('0') else '82' + phone
                return phone
        return None
    
    @staticmethod
    def extract_variables(text: str, template_variables: List[str]) -> Dict[str, str]:
        """템플릿 변수값 추출"""
        variables = {}
        
        # 일반적인 패턴으로 정보 추출
        patterns = {
            '업체명': r'(?:업체|회사|상호)[:=\s]*([가-힣\w\s]+)',
            '고객명': r'(?:고객|이름|성함)[:=\s]*([가-힣]+)',
            '날짜': r'(\d{4}[-./]\d{1,2}[-./]\d{1,2}|\d{1,2}[-./]\d{1,2}|\d{1,2}일)',
            '시간': r'(\d{1,2}:\d{2}|\d{1,2}시)',
            '주문번호': r'(?:주문번호|주문)[:=\s]*([A-Z0-9]+)',
            '상품명': r'(?:상품|제품)[:=\s]*([가-힣\w\s]+)',
            '송장번호': r'(?:송장번호|송장)[:=\s]*(\d+)',
            '배송업체': r'(?:배송업체|택배)[:=\s]*([가-힣\w]+)'
        }
        
        for var in template_variables:
            if var in patterns:
                match = re.search(patterns[var], text)
                if match:
                    variables[var] = match.group(1).strip()
            else:
                # 기본값 설정
                variables[var] = f"[{var}]"
        
        return variables

class ValidationError(Exception):
    """유효성 검사 오류"""
    pass

class FormValidator:
    """폼 기반 유효성 검사"""
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """전화번호 유효성 검사"""
        if not phone:
            return False
        
        # 82로 시작하는 한국 전화번호 형식
        pattern = r'^(?:\+82|0)(10|11|16|17|18|19)\d{7,8}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_message_length(message: str, max_length: int = 1000) -> bool:
        """메시지 길이 검사"""
        return len(message) <= max_length
    
    @staticmethod
    def validate_variable_length(value: str, max_length: int) -> bool:
        """변수 길이 검사"""
        return len(value) <= max_length
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """URL 유효성 검사"""
        if not url:
            return True
        return url.startswith(('http://', 'https://'))
    
    @classmethod
    def validate_request(cls, request: MessageRequest) -> List[str]:
        """요청 데이터 전체 검증"""
        errors = []
        
        if not request.sender_key:
            errors.append("발신 프로필 키(sender_key)가 필요합니다")
        
        if not request.template_code:
            errors.append("템플릿 코드(template_code)가 필요합니다")
        
        if not cls.validate_phone_number(request.phone_number):
            errors.append("올바른 전화번호 형식이 아닙니다")
        
        if not cls.validate_phone_number(request.sender_no):
            errors.append("올바른 발신번호 형식이 아닙니다")
        
        if not request.message:
            errors.append("메시지 내용이 필요합니다")
        elif not cls.validate_message_length(request.message):
            errors.append("메시지가 너무 깁니다 (최대 1000자)")
        
        if not request.cid:
            errors.append("고객사 정의 ID(cid)가 필요합니다")
        
        return errors

class KakaoBizMessageSender:
    """카카오 비즈메시지 발송기"""
    
    def __init__(self, base_url: str, access_token: str):
        self.base_url = base_url.rstrip('/')
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            'accept': '*/*',
            'authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        })
    
    def send_message(self, request: MessageRequest) -> Dict[str, Any]:
        """메시지 발송"""
        url = f"https://{self.base_url}/v2/send/kakao"
        
        # 요청 데이터 변환
        payload = asdict(request)
        
        # None 값 제거
        payload = {k: v for k, v in payload.items() if v is not None}
        
        # 버튼 정보 변환
        if request.buttons:
            payload['button'] = [asdict(btn) for btn in request.buttons]
            del payload['buttons']
        
        # 바로가기 정보 변환  
        if request.quick_replies:
            payload['quick_reply'] = [asdict(qr) for qr in request.quick_replies]
            del payload['quick_replies']
        
        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"메시지 발송 성공: CID={request.cid}")
            return result
            
        except requests.RequestException as e:
            error_msg = f"메시지 발송 실패: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

class BizMessagePipeline:
    """비즈메시지 발송 파이프라인"""
    
    def __init__(self, base_url: str, access_token: str, sender_key: str, sender_no: str):
        self.template_manager = TemplateManager()
        self.parameter_extractor = ParameterExtractor()
        self.form_validator = FormValidator()
        self.sender = KakaoBizMessageSender(base_url, access_token)
        self.sender_key = sender_key
        self.sender_no = sender_no
    
    def generate_cid(self) -> str:
        """고유 CID 생성"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        hash_value = hashlib.md5(f"{timestamp}{time.time()}".encode()).hexdigest()[:6]
        return f"{timestamp}{hash_value}"
    
    def process_user_prompt(self, prompt: str, phone_number: str = None) -> Tuple[MessageRequest, List[str]]:
        """사용자 프롬프트 처리"""
        errors = []
        
        # 1. 전화번호 추출
        if not phone_number:
            phone_number = self.parameter_extractor.extract_phone_number(prompt)
        
        if not phone_number:
            errors.append("전화번호를 찾을 수 없습니다")
            return None, errors
        
        # 2. 템플릿 찾기
        template_name = self.template_manager.find_template_by_intent(prompt)
        if not template_name:
            errors.append("적절한 템플릿을 찾을 수 없습니다")
            return None, errors
        
        template_info = self.template_manager.get_template(template_name)
        
        # 3. 변수 추출
        variables = self.parameter_extractor.extract_variables(prompt, template_info['variables'])
        
        # 4. 메시지 생성 (변수 치환)
        message = template_info['message']
        for var, value in variables.items():
            message = message.replace(f'${{{var}}}', value)
        
        # 5. 요청 객체 생성
        request = MessageRequest(
            sender_key=self.sender_key,
            cid=self.generate_cid(),
            template_code=template_info['code'],
            phone_number=phone_number,
            sender_no=self.sender_no,
            message=message,
            fall_back_yn=False
        )
        
        # 6. 유효성 검사
        validation_errors = self.form_validator.validate_request(request)
        errors.extend(validation_errors)
        
        return request, errors
    
    def send_template_message(self, prompt: str, phone_number: str = None) -> Dict[str, Any]:
        """템플릿 메시지 발송"""
        try:
            # 프롬프트 처리
            request, errors = self.process_user_prompt(prompt, phone_number)
            
            if errors:
                return {
                    'success': False,
                    'errors': errors,
                    'message': '유효성 검사 실패'
                }
            
            # 메시지 발송
            result = self.sender.send_message(request)
            
            return {
                'success': True,
                'result': result,
                'cid': request.cid,
                'template_code': request.template_code,
                'message': '메시지 발송 성공'
            }
            
        except Exception as e:
            logger.error(f"파이프라인 오류: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': '메시지 발송 실패'
            }

# 사용 예시
if __name__ == "__main__":
    # 설정 정보
    CONFIG = {
        'base_url': 'bizmsg-web.kakaoenterprise.com',
        'access_token': '5241cdfe06275e36cd297c6b3a556e1d', # 카카오 developers
        'sender_key': '12345678',
        'sender_no': '01037069303'  # 발신번호
    }
    
    # 파이프라인 초기화python
    pipeline = BizMessagePipeline(
        base_url=CONFIG['base_url'],
        access_token=CONFIG['access_token'],
        sender_key=CONFIG['sender_key'],
        sender_no=CONFIG['sender_no']
    )
    
    # 테스트 케이스들
    test_cases = [
        {
            'prompt': '회사명 테크컴퍼니에서 고객 김철수님의 회원가입이 2024-01-15에 완료되었습니다',
            'phone': '01037069303'
        },
        {
            'prompt': '마켓플레이스에서 주문번호 ORDER123 상품명 스마트폰 배송이 시작되었습니다 송장번호 1234567890 배송업체 로젠택배',
            'phone': '010-3706-9303'
        },
        {
            'prompt': '카페베네 2024년 1월 1일 휴무일 안내',
            'phone': '010-3706-9303'
        }
    ]
    
    # 테스트 실행
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== 테스트 케이스 {i} ===")
        print(f"프롬프트: {test_case['prompt']}")
        print(f"전화번호: {test_case['phone']}")
        
        result = pipeline.send_template_message(
            prompt=test_case['prompt'],
            phone_number=test_case['phone']
        )
        
        print(f"결과: {json.dumps(result, indent=2, ensure_ascii=False)}")