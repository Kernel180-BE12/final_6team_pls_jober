"""
알림톡 템플릿 검증 서비스
"""
import asyncio
import json
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Union

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.chromadb_service import ChromaDBService

try:
    from services.openai_service import OpenAIService
    HAS_OPENAI_SERVICE = True
except ImportError:
    HAS_OPENAI_SERVICE = False
    print("Warning: OpenAI 서비스를 로드할 수 없습니다. Mock 모드로 실행됩니다.")

from models.alimtalk_models import (
    ValidationRequest, ValidationResponse, ValidationResult, ProblemArea
)
from validators.validator_pipeline import ValidationPipeline


class AlimtalkValidationService:
    """알림톡 검증 서비스"""
    
    def __init__(self):
        self.chromadb_service = ChromaDBService()
        self.openai_service = OpenAIService()  # AI 서비스 무조건 사용
        self.validation_pipeline = None
        self.is_initialized = False
        
    async def initialize(self):
        """
        알림톡 검증 서비스 초기화
        
        지연 초기화(Lazy Initialization) 패턴을 사용하여 서버 시작 시간을 단축하고,
        실제 검증 작업이 필요할 때만 무거운 초기화 작업을 수행합니다.
        
        초기화 과정:
        1. ChromaDB 서비스 초기화 - 벡터 데이터베이스 연결 및 컬렉션 준비
        2. 검증 파이프라인 구성 - 1차(제약) → 2차(의미적) 검증 순서 제어
        3. 의존성 주입 - 각 컴포넌트들을 연결하여 검증 워크플로우 구성
        
        중복 초기화 방지를 위해 is_initialized 플래그로 상태를 관리합니다.
        """
        if self.is_initialized:
            return
            
        # ChromaDB 초기화 - 정책 문서 및 승인된 템플릿 데이터 로드
        await self.chromadb_service.initialize()
        
        # 검증 파이프라인 초기화 - LLM 기반 제약 검증기와 의미적 검증기 연결
        from validators.constraint_validator import ConstraintValidator
        constraint_validator = ConstraintValidator()
        self.validation_pipeline = ValidationPipeline(
            chromadb_service=self.chromadb_service,
            constraint_validator=constraint_validator
        )
        
        self.is_initialized = True
        print(">>service<<")
        print("✅ 알림톡 검증 서비스 초기화 완료")
    
    async def validate_template(self, request: ValidationRequest) -> ValidationResponse:
        """템플릿 검증 실행"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 검증 실행
            template_data = request.template.dict()
            result = self.validation_pipeline.validate(template_data)
            
            # 응답 생성
            if result['final_result'].is_valid:
                final_message = " 모든 검증을 통과했습니다. 발송 가능합니다."
                success = True
            else:
                error_count = len(result['final_result'].errors)
                warning_count = len(result['final_result'].warnings)
                final_message = f" 검증 실패: {error_count}개 오류, {warning_count}개 경고"
                success = False
            
            # 결과 필터링 (None이 아닌 것만, 중복 제거)
            validation_results = []
            if result.get('constraint_result'):
                validation_results.append(result['constraint_result'])
            if result.get('semantic_result'):
                validation_results.append(result['semantic_result'])
            # final_result는 constraint_result와 동일하므로 제외
            
            # 문제 영역 생성
            problem_areas = []
            
            # 배치 처리를 위해 모든 오류를 먼저 수집
            all_errors = []
            all_details = []
            
            for result in validation_results:
                if result.details and 'validation_details' in result.details:
                    validation_details = result.details['validation_details']
                    for detail in validation_details:
                        all_details.append((detail, result.stage))
                else:
                    # 기존 방식: errors에서 문제 영역 생성
                    for error in result.errors:
                        all_errors.append((error, result.stage))
            
            # 배치로 대안 생성 (효율성을 위해)
            if all_details:
                # 상세 검증 결과가 있는 경우 배치 처리
                problem_areas.extend(await self._create_problem_areas_batch(all_details, request.template.template_content or ""))
            elif all_errors:
                # 단순 오류가 있는 경우 배치 처리
                problem_areas.extend(await self._create_problem_areas_from_errors_batch(all_errors, request.template.template_content or ""))
            
            # 오류 및 경고 개수 계산
            total_errors = sum(1 for area in problem_areas if area.severity == "error")
            total_warnings = sum(1 for area in problem_areas if area.severity == "warning")
            
            response = ValidationResponse(
                success=success,
                message=final_message,
                problem_areas=problem_areas,
                validation_stage=validation_results[0].stage if validation_results else "1차 검증",
                total_errors=total_errors,
                total_warnings=total_warnings
            )
            
            return response
            
        except Exception as e:
            return ValidationResponse(
                success=False,
                message=f"검증 중 오류가 발생했습니다: {str(e)}",
                problem_areas=[],
                validation_stage="오류",
                total_errors=0,
                total_warnings=0
            )
    
    async def _extract_problem_info(self, error_source: Union[str, Dict[str, Any]], template_content: str) -> Dict[str, Any]:
        """AI를 사용해서 문제 영역을 자동으로 추출"""
        
        # 오류 텍스트 추출
        if isinstance(error_source, dict):
            error_text = error_source.get('reason', '')
        else:
            error_text = error_source
        
        # AI 프롬프트 생성
        from validators.prompts.problem_extraction_prompt import get_problem_extraction_prompt
        prompt = get_problem_extraction_prompt(template_content, error_text)
        
        try:
            response = await self.openai_service.generate_response(prompt)
            print(f"AI 문제 영역 추출 응답: {response[:200]}...")  # 디버깅용 로그
            
            # JSON 파싱
            problem_info = self._parse_ai_response(response)
            print(f"파싱된 문제 정보: {problem_info}")  # 디버깅용 로그
            
            return problem_info
            
        except Exception as e:
            print(f"AI 문제 영역 추출 실패: {e}")
            # AI 실패 시 기본값 반환
            return {
                "area_type": "entire_template",
                "location": "전체",
                "problem_text": template_content[:100] + "..." if len(template_content) > 100 else template_content,
                "start_position": 0,
                "end_position": len(template_content)
            }
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """AI 응답에서 JSON 파싱"""
        try:
            # JSON 블록 추출 (```json ... ``` 형태)
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # JSON 블록이 없으면 전체 응답에서 JSON 부분 찾기
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = response
            
            # JSON 파싱
            data = json.loads(json_str)
            
            # 필수 필드 검증 및 기본값 설정
            search_methods = data.get("search_methods", {})
            
            # 기존 방식과 새로운 방식 모두 지원
            start_pos = data.get("start_position")
            end_pos = data.get("end_position")
            
            # 새로운 search_methods 방식에서 approximate_position 추출
            if not start_pos and search_methods:
                start_pos = search_methods.get("approximate_position")
                if start_pos is not None:
                    # approximate_position을 기반으로 end_position 추출
                    problem_text = data.get("problem_text", "")
                    if problem_text and problem_text != "전체 템플릿":
                        end_pos = start_pos + len(problem_text)
                    else:
                        end_pos = start_pos
            
            # position 정보 검증 및 보정
            if start_pos is not None and end_pos is not None:
                # 정수로 변환 시도
                try:
                    start_pos = int(start_pos)
                    end_pos = int(end_pos)
                    # 유효성 검사
                    if start_pos < 0 or end_pos < start_pos:
                        print(f"유효하지 않은 position 정보: start={start_pos}, end={end_pos}")
                        start_pos = None
                        end_pos = None
                except (ValueError, TypeError):
                    print(f"Position 정보 변환 실패: start={start_pos}, end={end_pos}")
                    start_pos = None
                    end_pos = None
            
            return {
                "area_type": data.get("area_type", "entire_template"),
                "location": data.get("location", "전체"),
                "problem_text": data.get("problem_text", "문제 영역을 찾을 수 없습니다"),
                "start_position": start_pos,
                "end_position": end_pos,
                "search_methods": search_methods  # 새로운 검색 방법들도 포함
            }
            
        except json.JSONDecodeError:
            print("JSON 파싱 실패, 기본값 반환")
            return {
                "area_type": "entire_template",
                "location": "전체",
                "problem_text": "AI 응답 파싱에 실패했습니다",
                "start_position": None,
                "end_position": None
            }
        except Exception as e:
            print(f"AI 응답 파싱 중 오류: {e}")
            return {
                "area_type": "entire_template",
                "location": "전체",
                "problem_text": "AI 응답 처리 중 오류가 발생했습니다",
                "start_position": None,
                "end_position": None
            }
    
    def _get_error_type_from_stage(self, stage: str) -> str:
        """검증 단계에서 오류 타입 추출"""
        if "constraint" in stage:
            return "constraint_validation"
        elif "semantic" in stage:
            return "semantic_validation"
        else:
            return "general_validation"
    
    def _get_severity_from_error(self, error: str) -> str:
        """오류에서 심각도 추출"""
        if "❌" in error or "오류" in error:
            return "error"
        elif "⚠️" in error or "경고" in error:
            return "warning"
        else:
            return "error"  # 기본값
    
    async def _generate_alternatives_batch(self, errors: List[str], stage: str, template_content: str = "") -> Dict[str, List[str]]:
        """여러 오류에 대한 대안을 한 번의 API 호출로 생성 (배치 처리)"""
        try:
            # 배치 프롬프트 가져오기
            from validators.prompts.alternative_generation_prompt import get_batch_alternative_generation_prompt
            
            prompt = get_batch_alternative_generation_prompt(stage, errors, template_content)
            response = await self.openai_service.generate_response(prompt)
            
            print(f"배치 AI 대안 생성 응답: {response[:200]}...")  # 디버깅용 로그
            
            # JSON 응답에서 대안 추출
            alternatives_dict = self._extract_alternatives_from_batch_response(response, errors)
            print(f"추출된 배치 대안: {len(alternatives_dict)}개 오류에 대한 대안")  # 디버깅용 로그
            print(f"대안 상세 내용: {alternatives_dict}")  # 디버깅용 로그
            
            return alternatives_dict
            
        except Exception as e:
            print(f"배치 AI 대안 생성 중 오류 발생: {e}")
            # 실패 시 각 오류별로 기본 메시지 반환
            return {error: ["AI 대안 생성에 실패했습니다. 수동으로 수정해주세요."] for error in errors}
    
    def _extract_alternatives_from_batch_response(self, response: str, errors: List[str]) -> Dict[str, List[str]]:
        """배치 AI 응답에서 오류별 대안 추출 (JSON 형식)"""
        import json
        import re
        
        alternatives_dict = {}
        
        try:
            # JSON 블록 추출 (```json ... ``` 형태)
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # JSON 블록이 없으면 전체 응답에서 JSON 부분 찾기
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = response
            
            # JSON 파싱
            data = json.loads(json_str)
            
            if 'alternatives' in data:
                print(f"JSON에서 alternatives 키 발견: {list(data['alternatives'].keys())}")
                alternative_keys = list(data['alternatives'].keys())
                
                for i, error in enumerate(errors):
                    found_alternatives = None
                    
                    # 1. 정확한 키 매칭 시도
                    for key, alternatives in data['alternatives'].items():
                        if error in key or key in error:
                            found_alternatives = alternatives
                            print(f"오류 '{error}'에 대한 대안 찾음 (정확 매칭): {alternatives}")
                            break
                    
                    # 2. 정확한 매칭이 안되면 순서대로 매칭 (오류 메시지 1, 2, 3...)
                    if not found_alternatives and i < len(alternative_keys):
                        key = alternative_keys[i]
                        found_alternatives = data['alternatives'][key]
                        print(f"오류 '{error}'에 대한 대안 찾음 (순서 매칭): {found_alternatives}")
                    
                    # 3. 여전히 없으면 첫 번째 대안 사용
                    if not found_alternatives and len(alternative_keys) > 0:
                        key = alternative_keys[0]
                        found_alternatives = data['alternatives'][key]
                        print(f"오류 '{error}'에 대한 대안 찾음 (첫 번째 사용): {found_alternatives}")
                    
                    if found_alternatives:
                        alternatives_dict[error] = found_alternatives
                    else:
                        print(f"오류 '{error}'에 대한 대안을 찾을 수 없음")
                        alternatives_dict[error] = ["대안을 찾을 수 없습니다."]
            else:
                # JSON 구조가 예상과 다를 경우
                for error in errors:
                    alternatives_dict[error] = ["JSON 응답 구조 오류"]
                    
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 기본 메시지 반환
            print("JSON 파싱 실패, 기본 메시지 반환")
            for error in errors:
                alternatives_dict[error] = ["응답 파싱에 실패했습니다. 수동으로 수정해주세요."]
                
        except Exception as e:
            print(f"배치 응답 파싱 중 오류: {e}")
            # 최종 실패 시 기본 메시지
            for error in errors:
                alternatives_dict[error] = ["응답 파싱에 실패했습니다."]
        
        return alternatives_dict
    
    async def _create_problem_areas_batch(self, all_details: List[tuple], template_content: str) -> List[ProblemArea]:
        """상세 검증 결과들을 배치로 처리하여 문제 영역 생성"""
        problem_areas = []
        
        # 모든 오류 메시지를 추출
        errors = [detail[0].get('reason', '알 수 없는 오류') for detail in all_details]
        stages = [detail[1] for detail in all_details]
        
        # 가장 많이 나타나는 stage 사용 (보통 모든 오류가 같은 stage)
        main_stage = max(set(stages), key=stages.count) if stages else "unknown"
        
        # 배치로 대안 생성
        try:
            alternatives_dict = await self._generate_alternatives_batch(errors, main_stage, template_content)
        except Exception as e:
            print(f"배치 대안 생성 실패: {e}")
            alternatives_dict = {error: ["AI 대안 생성에 실패했습니다. 수동으로 수정해주세요."] for error in errors}
        
        # 각 상세 결과에 대해 문제 영역 생성
        for i, (detail, stage) in enumerate(all_details):
            try:
                error = detail.get('reason', '알 수 없는 오류')
                alternatives = alternatives_dict.get(error, ["AI 대안 생성에 실패했습니다. 수동으로 수정해주세요."])
                
                # 문제 정보 추출
                problem_info = await self._extract_problem_info(detail, template_content)
                
                # 문제 영역 생성
                area_id = f"{stage}_{detail.get('rule_type', 'unknown')}_{hash(error) % 10000}"
                
                problem_area = ProblemArea(
                    area_id=area_id,
                    area_type=problem_info["area_type"],
                    location=problem_info["location"],
                    problem_text=problem_info["problem_text"],
                    start_position=problem_info.get("start_position"),
                    end_position=problem_info.get("end_position"),
                    error_type=detail.get('rule_type', 'unknown'),
                    severity=detail.get('severity', 'error'),
                    reason=error,
                    suggestion=detail.get('suggestion', '수정이 필요합니다'),
                    alternatives=alternatives
                )
                
                problem_areas.append(problem_area)
                
            except Exception as e:
                print(f"문제 영역 생성 실패: {e}")
                # 실패 시 기본 문제 영역 생성
                error = detail.get('reason', '알 수 없는 오류')
                alternatives = alternatives_dict.get(error, ["AI 대안 생성에 실패했습니다. 수동으로 수정해주세요."])
                
                problem_area = ProblemArea(
                    area_id=f"{stage}_error_{hash(error) % 10000}",
                    area_type="entire_template",
                    location="전체",
                    problem_text=error,
                    start_position=None,
                    end_position=None,
                    error_type=detail.get('rule_type', 'unknown'),
                    severity=detail.get('severity', 'error'),
                    reason=error,
                    suggestion="수정이 필요합니다",
                    alternatives=alternatives
                )
                problem_areas.append(problem_area)
        
        return problem_areas
    
    async def _create_problem_areas_from_errors_batch(self, all_errors: List[tuple], template_content: str) -> List[ProblemArea]:
        """단순 오류들을 배치로 처리하여 문제 영역 생성"""
        problem_areas = []
        
        # 모든 오류 메시지와 stage 추출
        errors = [error_tuple[0] for error_tuple in all_errors]
        stages = [error_tuple[1] for error_tuple in all_errors]
        
        # 가장 많이 나타나는 stage 사용
        main_stage = max(set(stages), key=stages.count) if stages else "unknown"
        
        # 배치로 대안 생성
        try:
            alternatives_dict = await self._generate_alternatives_batch(errors, main_stage, template_content)
        except Exception as e:
            print(f"배치 대안 생성 실패: {e}")
            alternatives_dict = {error: ["AI 대안 생성에 실패했습니다. 수동으로 수정해주세요."] for error in errors}
        
        # 각 오류에 대해 문제 영역 생성
        for i, (error, stage) in enumerate(all_errors):
            try:
                alternatives = alternatives_dict.get(error, ["AI 대안 생성에 실패했습니다. 수동으로 수정해주세요."])
                
                # 문제 정보 추출
                problem_info = await self._extract_problem_info(error, template_content)
                
                # 문제 영역 생성
                area_id = f"{stage}_{len(template_content)}_{hash(error) % 10000}"
                
                problem_area = ProblemArea(
                    area_id=area_id,
                    area_type=problem_info["area_type"],
                    location=problem_info["location"],
                    problem_text=problem_info["problem_text"],
                    start_position=problem_info.get("start_position"),
                    end_position=problem_info.get("end_position"),
                    error_type="general_validation",
                    severity=self._get_severity_from_error(error),
                    reason=error,
                    suggestion="수정이 필요합니다",
                    alternatives=alternatives
                )
                
                problem_areas.append(problem_area)
                
            except Exception as e:
                print(f"문제 영역 생성 실패: {e}")
                # 실패 시 기본 문제 영역 생성
                alternatives = alternatives_dict.get(error, ["AI 대안 생성에 실패했습니다. 수동으로 수정해주세요."])
                
                problem_area = ProblemArea(
                    area_id=f"{stage}_error_{hash(error) % 10000}",
                    area_type="entire_template",
                    location="전체",
                    problem_text=error,
                    start_position=None,
                    end_position=None,
                    error_type="general_validation",
                    severity=self._get_severity_from_error(error),
                    reason=error,
                    suggestion="수정이 필요합니다",
                    alternatives=alternatives
                )
                problem_areas.append(problem_area)
        
        return problem_areas
    

