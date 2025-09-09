"""
2차 검증: 의미적 검증 (Semantic + Pre-send Gate)
RAG 기반 최종 검증
"""
import re
import json
from typing import Dict, Any, List, Tuple, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.alimtalk_models import ValidationResult, CategoryType
from services.chromadb_service import ChromaDBService
from templateEngine.prompts.final_validation_prompt import create_final_validation_prompt
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("Warning: OpenAI 패키지가 설치되지 않았습니다. GPT 기반 검증은 제한됩니다.")

import os
from jinja2 import Template


class SemanticValidator:
    """의미적 검증기 (RAG 기반)"""
    
    def __init__(self, 
                 vector_db_manager = None,
                 openai_api_key: str = None):
        """
        Args:
            vector_db_manager: 벡터DB 관리자
            openai_api_key: OpenAI API 키
        """
        # 2차 검증용 blacklist 컬렉션 사용
        self.vector_db = vector_db_manager or ChromaDBService(collection_name="blacklist")
        
        # OpenAI 클라이언트 설정
        if HAS_OPENAI:
            try:
                from openai import OpenAI
                api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
                if api_key:
                    self.openai_client = OpenAI(api_key=api_key)
                else:
                    print("Warning: OpenAI API 키가 설정되지 않았습니다. GPT 기반 검증은 제한됩니다.")
                    self.openai_client = None
            except Exception as e:
                print(f"OpenAI 클라이언트 초기화 실패: {e}")
                self.openai_client = None
        else:
            self.openai_client = None
    
    def validate(self, template_data: Dict[str, Any]) -> ValidationResult:
        """
        템플릿 데이터의 의미적 검증을 수행합니다.
        
        Args:
            template_data: 검증할 템플릿 데이터
            
        Returns:
            ValidationResult: 검증 결과
        """
        errors = []
        warnings = []
        details = {}
        
        try:
            # 1. 분류 판별
            classification_result = self._classify_content(template_data)
            details['classification'] = classification_result
            
            # 2. 정책 정렬 검증 (RAG 기반)
            policy_result = self._check_policy_alignment(template_data)
            errors.extend(policy_result['errors'])
            warnings.extend(policy_result['warnings'])
            details['policy_alignment'] = policy_result
            
            # 3. 렌더링 체크 (변수 치환 후 검증)
            rendering_result = self._check_rendering(template_data)
            errors.extend(rendering_result['errors'])
            warnings.extend(rendering_result['warnings'])
            details['rendering_check'] = rendering_result
            
            # 4. 채널 규정 검증
            channel_result = self._check_channel_requirements(template_data)
            errors.extend(channel_result['errors'])
            warnings.extend(channel_result['warnings'])
            details['channel_requirements'] = channel_result
            
            # 5. 컨텍스트 기반 금지 표현 검출
            contextual_result = self._check_contextual_violations(template_data)
            errors.extend(contextual_result['errors'])
            warnings.extend(contextual_result['warnings'])
            details['contextual_check'] = contextual_result
            
            is_valid = len(errors) == 0
            
            return ValidationResult(
                is_valid=is_valid,
                stage="semantic",
                errors=errors,
                warnings=warnings,
                details=details
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                stage="semantic",
                errors=[f"의미적 검증 중 오류 발생: {str(e)}"],
                warnings=[],
                details={"exception": str(e)}
            )
    
    def _classify_content(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """내용 분류 판별"""
        body = template_data.get('body', '')
        title = template_data.get('title', '')
        content = f"{title} {body}".strip()
        
        # 거래성 키워드
        transaction_keywords = [
            '주문', '결제', '배송', '구매', '거래', '승인', '완료', '확인',
            '발송', '도착', '픽업', '예약', '취소', '환불', '교환'
        ]
        
        # 마케팅 키워드
        marketing_keywords = [
            '할인', '이벤트', '프로모션', '특가', '세일', '쿠폰', 
            '무료', '혜택', '선착순', '당첨', '기회', '마지막'
        ]
        
        transaction_score = sum(1 for keyword in transaction_keywords if keyword in content)
        marketing_score = sum(1 for keyword in marketing_keywords if keyword in content)
        
        # 분류 결정
        if transaction_score > marketing_score and transaction_score > 0:
            predicted_category = CategoryType.TRANSACTION
            confidence = transaction_score / (transaction_score + marketing_score + 1)
        elif marketing_score > transaction_score and marketing_score > 0:
            predicted_category = CategoryType.MARKETING
            confidence = marketing_score / (transaction_score + marketing_score + 1)
        elif transaction_score == marketing_score and transaction_score > 0:
            predicted_category = CategoryType.MIXED
            confidence = 0.5
        else:
            predicted_category = CategoryType.REVIEW
            confidence = 0.0
        
        return {
            'predicted_category': predicted_category.value,
            'confidence': confidence,
            'transaction_score': transaction_score,
            'marketing_score': marketing_score,
            'needs_manual_review': confidence < 0.7
        }
    
    def _check_policy_alignment(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """정책 정렬 검증 (RAG 기반)"""
        errors = []
        warnings = []
        
        body = template_data.get('body', '')
        title = template_data.get('title', '')
        content = f"{title} {body}".strip()
        
        # 관련 가이드라인 검색
        relevant_guidelines = self.vector_db.search_similar(
            query=content,
            n_results=10
        )
        
        alignment_score = 0
        violated_guidelines = []
        
        for guideline in relevant_guidelines:
            if guideline['similarity'] > 0.7:  # 높은 유사도
                # 가이드라인 위반 검사
                violation_check = self._check_guideline_violation(
                    content, 
                    guideline['content'],
                    guideline['metadata']
                )
                
                if violation_check['violated']:
                    violated_guidelines.append({
                        'guideline': guideline['content'],
                        'reason': violation_check['reason'],
                        'severity': guideline['metadata'].get('priority', 'medium')
                    })
                else:
                    alignment_score += guideline['similarity']
        
        # 위반 사항을 오류/경고로 분류
        for violation in violated_guidelines:
            severity = violation['severity']
            message = f"가이드라인 위반: {violation['reason']}"
            
            if severity in ['critical', 'high']:
                errors.append(message)
            else:
                warnings.append(message)
        
        return {
            'errors': errors,
            'warnings': warnings,
            'alignment_score': alignment_score / len(relevant_guidelines) if relevant_guidelines else 0,
            'relevant_guidelines_count': len(relevant_guidelines),
            'violated_guidelines': violated_guidelines
        }
    
    def _check_guideline_violation(self, 
                                  content: str, 
                                  guideline: str, 
                                  metadata: Dict[str, Any]) -> Dict[str, Any]:
        """개별 가이드라인 위반 검사"""
        category = metadata.get('category', 'general')
        
        # 카테고리별 특화 검사
        if category == 'length':
            return self._check_length_violation(content, guideline)
        elif category == 'content':
            return self._check_content_violation(content, guideline)
        elif category == 'marketing':
            return self._check_marketing_violation(content, guideline)
        elif category == 'privacy':
            return self._check_privacy_violation(content, guideline)
        elif category == 'financial':
            return self._check_financial_violation(content, guideline)
        elif category == 'medical':
            return self._check_medical_violation(content, guideline)
        else:
            return {'violated': False, 'reason': ''}
    
    def _check_length_violation(self, content: str, guideline: str) -> Dict[str, Any]:
        """길이 관련 가이드라인 검사"""
        if '1000자' in guideline and len(content) > 1000:
            return {
                'violated': True,
                'reason': f'본문이 1000자를 초과했습니다 (현재: {len(content)}자)'
            }
        return {'violated': False, 'reason': ''}
    
    def _check_content_violation(self, content: str, guideline: str) -> Dict[str, Any]:
        """내용 관련 가이드라인 검사"""
        if '거래성' in guideline and '마케팅 용어' in guideline:
            marketing_terms = ['할인', '이벤트', '프로모션', '특가']
            found_terms = [term for term in marketing_terms if term in content]
            if found_terms:
                return {
                    'violated': True,
                    'reason': f'거래성 알림톡에 마케팅 용어가 포함되어 있습니다: {", ".join(found_terms)}'
                }
        return {'violated': False, 'reason': ''}
    
    def _check_marketing_violation(self, content: str, guideline: str) -> Dict[str, Any]:
        """마케팅 관련 가이드라인 검사"""
        if '광고' in guideline:
            if '(광고)' not in content and '광고' not in content:
                return {
                    'violated': True,
                    'reason': '마케팅 알림톡에 광고 표기가 없습니다'
                }
        return {'violated': False, 'reason': ''}
    
    def _check_privacy_violation(self, content: str, guideline: str) -> Dict[str, Any]:
        """개인정보 관련 가이드라인 검사"""
        # 개인정보 패턴 검사
        privacy_patterns = [
            r'\d{6}-\d{7}',  # 주민번호
            r'\d{4}-\d{4}-\d{4}-\d{4}',  # 카드번호
            r'\d{3}-\d{2,3}-\d{6}',  # 계좌번호
        ]
        
        for pattern in privacy_patterns:
            if re.search(pattern, content):
                return {
                    'violated': True,
                    'reason': '개인정보가 포함된 것으로 의심됩니다'
                }
        return {'violated': False, 'reason': ''}
    
    def _check_financial_violation(self, content: str, guideline: str) -> Dict[str, Any]:
        """금융 관련 가이드라인 검사"""
        risky_terms = ['100% 보장', '무조건', '반드시', '확실한 수익']
        found_terms = [term for term in risky_terms if term in content]
        if found_terms:
            return {
                'violated': True,
                'reason': f'금융 관련 과장 표현이 포함되어 있습니다: {", ".join(found_terms)}'
            }
        return {'violated': False, 'reason': ''}
    
    def _check_medical_violation(self, content: str, guideline: str) -> Dict[str, Any]:
        """의료 관련 가이드라인 검사"""
        medical_claims = ['치료', '완치', '100% 효과', '즉시 개선']
        found_claims = [claim for claim in medical_claims if claim in content]
        if found_claims:
            return {
                'violated': True,
                'reason': f'의료 관련 단정적 표현이 포함되어 있습니다: {", ".join(found_claims)}'
            }
        return {'violated': False, 'reason': ''}
    
    def _check_rendering(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """렌더링 체크 (변수 치환 후 검증)"""
        errors = []
        warnings = []
        
        try:
            # 변수 치환 수행
            rendered_template = self._render_template(template_data)
            
            # 치환 후 길이 검사
            if 'body' in rendered_template:
                if len(rendered_template['body']) > 1000:
                    errors.append(f"변수 치환 후 본문이 1000자를 초과합니다 (현재: {len(rendered_template['body'])}자)")
            
            # 치환 후 URL 유효성 검사
            if 'buttons' in rendered_template and rendered_template['buttons']:
                for i, button in enumerate(rendered_template['buttons']):
                    for url_field in ['url_mobile', 'url_pc']:
                        if url_field in button and button[url_field]:
                            if not self._is_valid_url(button[url_field]):
                                errors.append(f"버튼 {i+1}의 {url_field}이 유효하지 않습니다: {button[url_field]}")
            
            return {
                'errors': errors,
                'warnings': warnings,
                'rendered_template': rendered_template
            }
            
        except Exception as e:
            return {
                'errors': [f"템플릿 렌더링 중 오류: {str(e)}"],
                'warnings': [],
                'rendered_template': None
            }
    
    def _render_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """변수 치환을 통한 템플릿 렌더링"""
        variables = template_data.get('variables', {})
        rendered = template_data.copy()
        
        # Jinja2 템플릿 방식으로 변경 (#{변수명} -> {{변수명}})
        def convert_variable_syntax(text: str) -> str:
            return re.sub(r'#{([^}]+)}', r'{{\1}}', text)
        
        # 본문 렌더링
        if 'body' in rendered:
            template_text = convert_variable_syntax(rendered['body'])
            template = Template(template_text)
            rendered['body'] = template.render(**variables)
        
        # 제목 렌더링
        if 'title' in rendered and rendered['title']:
            template_text = convert_variable_syntax(rendered['title'])
            template = Template(template_text)
            rendered['title'] = template.render(**variables)
        
        # 버튼 URL 렌더링
        if 'buttons' in rendered and rendered['buttons']:
            for button in rendered['buttons']:
                for url_field in ['url_mobile', 'url_pc']:
                    if url_field in button and button[url_field]:
                        template_text = convert_variable_syntax(button[url_field])
                        template = Template(template_text)
                        button[url_field] = template.render(**variables)
        
        return rendered
    
    def _check_channel_requirements(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """채널 규정에 따른 필수 태그/고지문 확인"""
        errors = []
        warnings = []
        
        channel = template_data.get('channel')
        category = template_data.get('category')
        body = template_data.get('body', '')
        
        # 마케팅 알림톡 광고 표기 검사
        if category == 'marketing' or channel == 'friendtalk':
            if '(광고)' not in body and '광고' not in body:
                errors.append("마케팅성 메시지에는 '(광고)' 표기가 필요합니다")
        
        # 수신거부 안내 검사 (마케팅의 경우)
        if category == 'marketing':
            unsubscribe_patterns = ['수신거부', '거부', '080']
            if not any(pattern in body for pattern in unsubscribe_patterns):
                warnings.append("마케팅 메시지에는 수신거부 안내를 포함하는 것을 권장합니다")
        
        return {
            'errors': errors,
            'warnings': warnings
        }
    
    def _check_contextual_violations(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """컨텍스트 기반 금지 표현 검출 (최종 GPT 검증)"""
        errors = []
        warnings = []
        
        content = f"{template_data.get('title', '')} {template_data.get('body', '')}".strip()
        
        # GPT 기반 최종 검증 (API 키가 있는 경우)
        if HAS_OPENAI and self.openai_client:
            try:
                # RAG에서 관련 가이드라인 검색
                relevant_guidelines = self.vector_db.search_similar(
                    query=content,
                    n_results=5
                )
                
                # 새로운 프롬프트 구조로 GPT 분석 실행
                final_analysis = self._analyze_with_gpt(
                    content, 
                    template_data=template_data, 
                    rag_guidelines=relevant_guidelines
                )
                
                # 결과 파싱하여 errors/warnings로 변환
                if not final_analysis.get('passed', True):
                    for violation in final_analysis.get('violations', []):
                        severity = violation.get('severity', 'MINOR')
                        message = f"정책 위반 [{violation.get('rule_id', 'unknown')}]: {violation.get('evidence', '')}"
                        
                        if severity == 'CRITICAL':
                            errors.append(message)
                        elif severity == 'MAJOR':
                            errors.append(message)
                        else:  # MINOR
                            warnings.append(message)
                
                # autofix 제안이 있는 경우 경고로 추가
                if final_analysis.get('autofix', {}).get('enabled'):
                    autofix_note = final_analysis['autofix'].get('notes', '')
                    suggested_body = final_analysis['autofix'].get('patch_body', '')
                    if suggested_body:
                        warnings.append(f"자동 수정 제안: {autofix_note}")
                        
            except Exception as e:
                warnings.append(f"AI 기반 최종 검증 중 오류: {str(e)}")
        
        return {
            'errors': errors,
            'warnings': warnings
        }
    
    def _analyze_with_gpt(self, content: str, template_data: Dict[str, Any] = None, rag_guidelines: List[Dict] = None) -> Dict[str, Any]:
        """GPT를 사용한 최종 검증 분석"""
        
        # 2차 검증 결과 (간단한 통과/실패 정보)
        det_report_summary = {
            "constraint_passed": True,  # 이전 단계에서 여기까지 온 경우
            "issues_found": [],
            "warnings": []
        }
        
        # 새로운 프롬프트 템플릿 사용
        prompt = create_final_validation_prompt(
            template_data=template_data or {},
            det_report_summary=det_report_summary,
            rag_guidelines=rag_guidelines or [],
            template_pk=template_data.get('template_pk') or template_data.get('id') if template_data else None
        )
        
        try:
            if not HAS_OPENAI:
                return {
                    "passed": True,
                    "summary": "OpenAI 패키지가 없어 Mock 검증을 수행했습니다.",
                    "violations": [],
                    "autofix": {"enabled": False, "patch_body": "", "notes": ""},
                    "policy_refs": []
                }
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # JSON 추출 (마크다운 코드블록 제거)
            if result_text.startswith('```'):
                lines = result_text.split('\n')
                start_idx = 1 if lines[0].startswith('```') else 0
                end_idx = len(lines)
                for i in range(len(lines) - 1, -1, -1):
                    if lines[i].strip() == '```':
                        end_idx = i
                        break
                result_text = '\n'.join(lines[start_idx:end_idx])
            
            return json.loads(result_text)
            
        except Exception as e:
            # 기본 응답 구조
            return {
                "passed": False,
                "summary": f"AI 분석 중 오류 발생: {str(e)}",
                "violations": [{
                    "rule_id": "system_error",
                    "severity": "MAJOR",
                    "evidence": str(e),
                    "policy_ref": "system",
                    "span": [0, len(content)]
                }],
                "autofix": {
                    "enabled": False,
                    "patch_body": "",
                    "notes": "시스템 오류로 인해 자동 수정 불가"
                },
                "policy_refs": []
            }
    
    def _is_valid_url(self, url: str) -> bool:
        """URL 유효성 검사"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
