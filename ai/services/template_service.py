from typing import List, Dict, Any, Optional
import re
from chromadb_service import ChromaDBService
import asyncio
class TemplateValidationService:
    def __init__(self):
        """
        템플릿 검증 서비스 초기화
        """
        self.chromadb_service = ChromaDBService(collection_name="template_examples")
        
        # 카카오 알림톡 화이트리스트 키워드 (발송 가능)
        self.whitelist_keywords = [
            "회원가입", "가입완료", "주문완료", "배송완료", "예약확인", "결제완료",
            "포인트적립", "쿠폰지급", "만료안내", "보안인증", "OTP", "임시비밀번호",
            "입금확인", "출금알림", "대출이자", "카드결제", "보험계약", "민방위",
            "학사일정", "약관변경", "서비스중단", "정화조청소", "과태료", "답변등록"
        ]
        
        # 카카오 알림톡 블랙리스트 키워드 (발송 불가)
        self.blacklist_keywords = [
            "장바구니", "특가", "할인", "이벤트", "생일축하", "감사합니다", "안부",
            "뉴스레터", "구독", "무료체험", "당첨", "혜택", "마케팅", "광고",
            "클릭", "바로가기", "다운로드", "설치", "앱설치", "친구추가",
            "카카오톡채널", "수신동의", "추천종목", "급등주", "투자", "대출상품",
            "신용조회", "특별제공", "한정판매", "지금구매", "서둘러"
        ]
        
        # 화이트리스트 카테고리별 패턴
        self.whitelist_patterns = {
            "회원가입": ["가입", "회원", "등록완료", "인증완료"],
            "주문배송": ["주문", "배송", "발송", "도착", "완료", "확인"],
            "예약신청": ["예약", "신청", "접수", "확인", "변경", "취소"],
            "포인트쿠폰": ["적립", "소멸", "만료", "쿠폰", "포인트"],
            "보안금융": ["인증", "OTP", "비밀번호", "입금", "출금", "결제"],
            "안내공지": ["안내", "알림", "변경", "중단", "연기", "일정"]
        }
        
        # 블랙리스트 카테고리별 패턴
        self.blacklist_patterns = {
            "마케팅": ["특가", "할인", "세일", "이벤트", "무료", "증정"],
            "장바구니": ["장바구니", "찜", "관심상품", "저장", "담기"],
            "인사성": ["축하", "생일", "안부", "감사", "수고"],
            "유도성": ["클릭", "다운로드", "설치", "가입하기", "구매하기"],
            "구독성": ["뉴스레터", "구독", "정기발송", "무료제공"],
            "금융유도": ["대출추천", "투자", "수익", "급등", "추천종목"]
        }
        
    def get_guideline_status(self) -> Dict[str, Any]:
        """
        현재 로드된 가이드라인 상태 확인
        """
        return {
            "whitelist_keywords_count": len(self.whitelist_keywords),
            "blacklist_keywords_count": len(self.blacklist_keywords),
            "whitelist_categories": list(self.whitelist_patterns.keys()),
            "blacklist_categories": list(self.blacklist_patterns.keys()),
            "message": "하드코딩된 카카오 가이드라인이 로드되었습니다."
        }
    
    async def search_similar_templates(self, user_message: str, similarity_threshold: float = 0.7) -> Dict[str, Any]:
        """
        ChromaDB에서 유사한 템플릿 검색
        """
        try:
            # 사용자 메시지로 유사한 템플릿 검색
            search_results = await self.chromadb_service.search_documents(
                query=user_message,
                n_results=5
            )
            
            similar_templates = []
            for i, (doc, metadata, distance) in enumerate(zip(
                search_results.get("results", []),
                search_results.get("metadatas", []),
                search_results.get("distances", [])
            )):
                # 거리가 낮을수록 유사함 (0에 가까울수록)
                similarity_score = 1 - distance
                
                if similarity_score >= similarity_threshold:
                    similar_templates.append({
                        "template_text": doc,
                        "metadata": metadata,
                        "similarity_score": similarity_score,
                        "rank": i + 1
                    })
            
            return {
                "query": user_message,
                "similar_templates": similar_templates,
                "total_found": len(similar_templates),
                "search_performed": True
            }
            
        except Exception as e:
            return {
                "query": user_message,
                "similar_templates": [],
                "total_found": 0,
                "search_performed": False,
                "error": f"템플릿 검색 실패: {str(e)}"
            }
    
    async def validate_template_content(self, template_text: str) -> Dict[str, Any]:
        """
        템플릿 내용을 화이트리스트/블랙리스트로 검증
        """
        validation_result = {
            "is_valid": True,
            "whitelist_matches": [],
            "blacklist_violations": [],
            "whitelist_categories": [],
            "blacklist_categories": [],
            "recommendations": [],
            "score": 100,
            "violation_details": []
        }
        
        try:
            text_lower = template_text.lower()
            
            # 1. 블랙리스트 검사 (위반 사항 확인)
            blacklist_violations = []
            violated_categories = []
            violation_details = []
            
            # 키워드 기반 검사
            for keyword in self.blacklist_keywords:
                if keyword in text_lower:
                    blacklist_violations.append(keyword)
                    violation_details.append(f"금지 키워드 '{keyword}' 발견")
            
            # 패턴 기반 검사
            for category, patterns in self.blacklist_patterns.items():
                for pattern in patterns:
                    if pattern in text_lower:
                        if category not in violated_categories:
                            violated_categories.append(category)
                        violation_details.append(f"금지 패턴 '{pattern}' (카테고리: {category}) 발견")
            
            # 2. 화이트리스트 검사 (권장 사항 확인)
            whitelist_matches = []
            matched_categories = []
            
            # 키워드 기반 검사
            for keyword in self.whitelist_keywords:
                if keyword in text_lower:
                    whitelist_matches.append(keyword)
            
            # 패턴 기반 검사
            for category, patterns in self.whitelist_patterns.items():
                for pattern in patterns:
                    if pattern in text_lower:
                        if category not in matched_categories:
                            matched_categories.append(category)
            
            # 3. 특수 규칙 검사
            special_violations = self._check_special_rules(template_text)
            blacklist_violations.extend(special_violations["violations"])
            violation_details.extend(special_violations["details"])
            
            # 4. 결과 설정
            validation_result["whitelist_matches"] = whitelist_matches
            validation_result["blacklist_violations"] = blacklist_violations
            validation_result["whitelist_categories"] = matched_categories
            validation_result["blacklist_categories"] = violated_categories
            validation_result["violation_details"] = violation_details
            
            # 5. 검증 결과 판정
            if blacklist_violations:
                validation_result["is_valid"] = False
                validation_result["score"] = max(0, 100 - len(blacklist_violations) * 15)
                validation_result["recommendations"].append(
                    f"다음 금지 사항을 수정해주세요: {', '.join(blacklist_violations[:5])}..."
                )
                validation_result["recommendations"].append(
                    f"위반 카테고리: {', '.join(violated_categories)}"
                )
            
            if not whitelist_matches and validation_result["is_valid"]:
                validation_result["score"] = max(validation_result["score"] - 20, 0)
                validation_result["recommendations"].append(
                    "화이트리스트 키워드나 패턴을 포함하면 승인 가능성이 높아집니다."
                )
                validation_result["recommendations"].append(
                    f"권장 카테고리: {', '.join(list(self.whitelist_patterns.keys())[:3])}"
                )
            
            # 6. 최종 권장사항
            if validation_result["is_valid"] and whitelist_matches:
                validation_result["recommendations"].append(
                    f"적합한 알림톡 템플릿입니다. 매칭된 화이트리스트 카테고리: {', '.join(matched_categories)}"
                )
            
            return validation_result
            
        except Exception as e:
            return {
                "is_valid": False,
                "error": f"템플릿 검증 실패: {str(e)}",
                "whitelist_matches": [],
                "blacklist_violations": [],
                "recommendations": ["검증 중 오류가 발생했습니다. 수동 검토가 필요합니다."],
                "score": 0
            }
    
    def _check_special_rules(self, template_text: str) -> Dict[str, List[str]]:
        """
        특수 규칙 검사 (블랙리스트의 특별한 조건들)
        """
        violations = []
        details = []
        text_lower = template_text.lower()
        
        # 1. 변수만으로 구성된 메시지 체크
        variable_pattern = r'#\{[^}]+\}'
        variables = re.findall(variable_pattern, template_text)
        text_without_variables = re.sub(variable_pattern, '', template_text).strip()
        
        if len(text_without_variables) < 10 and len(variables) > 2:
            violations.append("변수전용구성")
            details.append("변수만으로 구성된 메시지는 발송 불가능합니다.")
        
        # 2. 광고성 URL 체크
        ad_keywords_in_url = ["event", "sale", "coupon", "discount", "special"]
        if "http" in text_lower:
            for keyword in ad_keywords_in_url:
                if keyword in text_lower:
                    violations.append("광고성URL")
                    details.append(f"광고성 URL 키워드 '{keyword}' 발견")
                    break
        
        # 3. 긴급성/유도성 표현 체크
        urgent_patterns = ["지금", "서둘러", "놓치지마세요", "한정", "마감임박", "오늘만"]
        for pattern in urgent_patterns:
            if pattern in text_lower:
                violations.append("긴급성유도")
                details.append(f"긴급성 유도 표현 '{pattern}' 발견")
        
        return {"violations": violations, "details": details}
    
    def _analyze_message_category(self, message: str) -> Dict[str, Any]:
        """
        메시지 카테고리 분석
        """
        text_lower = message.lower()
        category_scores = {}
        
        # 화이트리스트 카테고리별 점수 계산
        for category, patterns in self.whitelist_patterns.items():
            score = 0
            matched_patterns = []
            for pattern in patterns:
                if pattern in text_lower:
                    score += 1
                    matched_patterns.append(pattern)
            
            if score > 0:
                category_scores[category] = {
                    "score": score,
                    "matched_patterns": matched_patterns,
                    "confidence": min(score / len(patterns), 1.0)
                }
        
        # 최고 점수 카테고리 찾기
        best_category = None
        if category_scores:
            best_category = max(category_scores.keys(), key=lambda k: category_scores[k]["score"])
        
        return {
            "predicted_category": best_category,
            "category_scores": category_scores,
            "total_categories_matched": len(category_scores)
        }
    
    async def process_template_request(self, user_message: str) -> Dict[str, Any]:
        """
        전체 템플릿 처리 프로세스
        1. 유사 템플릿 검색
        2. 검증 수행
        """
        result = {
            "user_message": user_message,
            "similar_templates": {},
            "validation": {},
            "processing_status": "completed"
        }
        
        try:
            # 1. 유사 템플릿 검색
            similar_templates = await self.search_similar_templates(user_message)
            result["similar_templates"] = similar_templates
            
            # 2. 사용자 메시지 자체에 대한 검증 (임시로 사용자 메시지를 템플릿으로 가정)
            validation = await self.validate_template_content(user_message)
            result["validation"] = validation
            
            # 3. 유사 템플릿이 있는 경우 참고 정보 제공
            if similar_templates.get("total_found", 0) > 0:
                result["recommendation"] = {
                    "has_similar": True,
                    "message": "유사한 템플릿이 발견되었습니다. 참고하여 새로운 템플릿을 생성하겠습니다.",
                    "reference_templates": similar_templates["similar_templates"][:3]  # 상위 3개만
                }
            else:
                result["recommendation"] = {
                    "has_similar": False,
                    "message": "유사한 템플릿이 없어 새로운 템플릿을 생성하겠습니다.",
                    "reference_templates": []
                }
            
            return result
            
        except Exception as e:
            result["processing_status"] = "failed"
            result["error"] = f"템플릿 처리 실패: {str(e)}"
            return result


# 예시 템플릿 데이터를 ChromaDB에 추가하는 함수
async def initialize_example_templates():
    """
    예시 템플릿들을 ChromaDB에 초기화
    """
    service = TemplateValidationService()
    
    example_templates = [
        {
            "text": "안녕하세요 #{수신자명}님, 요청하신 서비스 소개서가 발송되었습니다. 아래 버튼을 클릭하시면 자세한 내용을 확인하실 수 있습니다. *서비스 소개서를 요청하신 분들께 발송되는 메시지입니다.",
            "metadata": {
                "분류1차": "서비스이용",
                "분류2차": "이용안내/공지", 
                "자동생성제목": "서비스 소개서 발송",
                "템플릿코드": "Introduction25042902",
                "공용or전용": "공용",
                "업종분류": "서비스업",
                "목적분류": "공지/안내"
            }
        }
    ]
    
    documents = [template["text"] for template in example_templates]
    metadatas = [template["metadata"] for template in example_templates]
    
    result = await service.chromadb_service.add_documents(
        documents=documents,
        metadatas=metadatas
    )
    
    return result
