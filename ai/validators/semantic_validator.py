import logging
import re
from typing import Dict, Any, List

from services.chromadb_service import ChromaDBService
from models.alimtalk_models import ValidationResult

from .config import (
    REJECT_THRESHOLD, REVIEW_THRESHOLD, VIOLATION_THRESHOLD,
    REJECTION_REASONS_SEARCH_K, EVIDENCE_LIMIT, VIOLATION_DISPLAY_LIMIT, TEXT_PREVIEW_LENGTH,
    BLACKLIST_PATTERNS
)

logger = logging.getLogger(__name__)


class SemanticValidator:
    """의미적 검증기 (RAG 기반) - 의존성 주입 방식 적용"""
    
    # 하이퍼 파라미터 상수
    REJECT_THRESHOLD = 0.6      # 거부 임계값 (60% 이상)
    REVIEW_THRESHOLD = 0.4      # 검토 임계값 (40% 이상)
    VIOLATION_THRESHOLD = 0.4   # 위반 수집 임계값
    
    APPROVED_SEARCH_K = 6       # 승인 템플릿 검색 개수
    PUBLIC_SEARCH_K = 5         # 공용 템플릿 검색 개수
    EVIDENCE_LIMIT = 3          # evidence 수집 개수
    VIOLATION_DISPLAY_LIMIT = 3 # 위반 사항 표시 개수
    TEXT_PREVIEW_LENGTH = 100   # 텍스트 미리보기 길이

    def __init__(self, chromadb_service: ChromaDBService):
        """
        ChromaDBService를 외부에서 주입받아 초기화합니다.
        """
        self.chromadb_service = chromadb_service
        self.DENIED_REASONS_SEARCH_K = 5  # denied_reasons 검색 시 상위 k개 결과

    def validate(self, template: Dict[str, Any]) -> ValidationResult:
        """
        최상위 엔트리: 두 단계 RAG → 라벨링 → 취합 → (review면 LLM 판정) / (fail이면 LLM 사유 요약)
        항상 동일 스키마의 ValidationResult를 반환.
        """
        print("🔍 SemanticValidator.validate() 시작")
        text = f"{template.get('template_title','')} {template.get('template_content','')}".strip()
        category = template.get("category")
        
        print(f"검증 대상 텍스트: {text[:TEXT_PREVIEW_LENGTH]}...")
        print(f"카테고리: {category}")

        # 1) 두 컬렉션 RAG (rejection_reasons + denied_reasons)
        print("🔍 rejection_reasons 컬렉션 검색 시작...")
        s_rr = self._rag_stage("rejection_reasons", text, k=REJECTION_REASONS_SEARCH_K, category_sub=category)
        # evidence 중복 제거
        s_rr["evidence"] = self._deduplicate_violations(s_rr.get("evidence", []))
        print(f"rejection_reasons 결과: {s_rr}")

        print("🔍 denied_reasons 컬렉션 검색 시작...")
        s_dn = self._rag_stage("denied_reasons", text, k=self.DENIED_REASONS_SEARCH_K)
        print(f"denied_reasons 결과: {s_dn}")

        # 만약 결과가 없다면 카테고리 필터 때문일 수 있으니 로그 출력
        if s_dn.get('score', 0) == 0:
            print(f"⚠️ denied_reasons에서 결과 없음. 카테고리: {category}")

        # 2) 최종 취합 - 실제 RAG 결과를 기반으로 계산
        # 두 단계 결과를 종합하여 최종 판정
        rejection_reasons_score = s_rr.get('score', 0.0)
        denied_reasons_score = s_dn.get('score', 0.0)
        
        # 더 높은 위험도를 최종 위험도로 사용
        final_risk = max(rejection_reasons_score, denied_reasons_score)
        
        # 위험도 기반 최종 라벨 결정
        if final_risk >= REJECT_THRESHOLD:
            final_label = "fail"
        elif final_risk >= REVIEW_THRESHOLD:
            final_label = "review"
        else:
            final_label = "pass"
        
        # 위반 사항 수집
        violations = []

        if s_rr.get('label') in ['fail', 'review']:
            for evidence in s_rr.get('evidence', []):
                if evidence.get('score', 0) >= VIOLATION_THRESHOLD:
                    violations.append({
                        "source": "rejection_reasons",
                        "reason": evidence.get('reason', '반려 사유와 유사'),
                        "evidence": evidence.get('evidence', ''),
                        "score": evidence.get('score', 0)
                    })
        
        if s_dn.get('label') in ['fail', 'review']:
            for evidence in s_dn.get('evidence', []):

                if evidence.get('score', 0) >= VIOLATION_THRESHOLD:
                    violations.append({
                        "source": "blacklist",
                        "reason": evidence.get('reason', '공용 템플릿과 유사'),
                        "evidence": evidence.get('evidence', ''),
                        "score": evidence.get('score', 0)
                    })

        # violations 중복 제거
        violations = self._deduplicate_violations(violations)
        decision_source = "heuristic"
        needs_review: bool = False
        warnings: List[str] = []

        # 3) 분기 - 간단한 구현으로 대체
        if final_label == "review":
            needs_review = True
            warnings.append("LLM 미구성: 사람 검토 필요")
        elif final_label == "fail":
            # 기본 처리만 수행
            pass

        is_valid = (final_label == "pass")

        print(f"\n📋 2차 검증 최종 결과:")
        print(f"   ✅ 통과 여부: {'통과' if is_valid else '실패'}")
        print(f"   🏷️ 최종 라벨: {final_label}")
        print(f"   📊 위험도: {final_risk}")
        print(f"   🤖 판정 방식: {decision_source}")
        print(f"   👥 사람 검토 필요: {'예' if needs_review else '아니오'}")
        if violations:
            print(f"   🚫 위반 사항 상세:")

            for i, v in enumerate(violations[:VIOLATION_DISPLAY_LIMIT], 1):  # 최대 3개만 표시
                print(f"      {i}. {v.get('reason', '알 수 없는 사유')} (출처: {v.get('source', '알 수 없음')})")

        details = {
            "final_label": final_label,             # pass | review | fail
            "final_risk": final_risk,               # 표시/튜닝용
            "decision_source": decision_source,     # heuristic | llm | human
            "needs_review": needs_review,           # true면 운영 큐로 라우팅
            "stage_details": [s_rr, s_dn],          # 각 단계 스코어/라벨/근거
            "violations": violations,               # fail/review 근거
            "rejection_analysis": s_rr.get("analysis", {}),  # 반려 사유 분석 결과
        }
        return ValidationResult(
            is_valid=is_valid,
            stage="semantic",
            errors=[] if is_valid else [v.get("reason") or "정책 위반 의심" for v in violations] or ["검토 필요"],
            warnings=warnings,
            details=details,
        )
    
    # 중복 제거
    def _deduplicate_violations(self, violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = {}
        for v in violations:
            key = (v.get("evidence"), v.get("source"))  # evidence+source 조합으로 중복 판별
            if key in seen:
                # 이미 있으면 score 높은 것만 유지
                if v.get("score", 0) > seen[key].get("score", 0):
                    seen[key] = v
            else:
                seen[key] = v
        return list(seen.values())


    def _rule_based_blacklist_stage(self, text: str) -> Dict[str, Any]:
        """
        룰 기반 블랙리스트 검증
        정규식 패턴 매칭을 통해 금지 패턴을 검출합니다.
        """
        matched_patterns = []
        evidence = []
        
        # 모든 블랙리스트 패턴에 대해 검사
        for pattern, description in BLACKLIST_PATTERNS:
            try:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    matched_text = match.group(0)
                    matched_patterns.append({
                        "pattern": pattern,
                        "description": description,
                        "matched_text": matched_text,
                        "start": match.start(),
                        "end": match.end()
                    })
                    
                    # evidence 추가 (룰 기반이므로 점수는 1.0으로 설정)
                    evidence.append({
                        "source": "blacklist_rule",
                        "policy_ref": description,
                        "reason": f"블랙리스트 패턴 매칭: {description}",
                        "evidence": matched_text,
                        "score": 1.0,  # 룰 기반 매칭은 확실한 위반이므로 1.0
                    })
            except re.error as e:
                logger.warning(f"정규식 패턴 오류: {pattern}, 오류: {e}")
                continue
        
        # 매칭된 패턴이 있으면 fail, 없으면 pass
        if matched_patterns:
            # 매칭된 패턴 수에 따라 위험도 조정 (최대 1.0)
            risk_score = min(len(matched_patterns) * 0.3, 1.0)
            label = "fail"  # 룰 기반 매칭은 확실한 위반
        else:
            risk_score = 0.0
            label = "pass"
        
        return {
            "stage": "blacklist_rule_based",
            "label": label,
            "score": round(risk_score, 4),
            "thresholds": {"reject": REJECT_THRESHOLD, "review": REVIEW_THRESHOLD},
            "evidence": evidence,
            "matched_patterns": matched_patterns,  # 디버깅용
        }

    def _preprocess_template_for_embedding(self, text: str) -> str:
        """
        템플릿을 임베딩을 위한 전처리
        - 변수명을 일반적인 표현으로 치환
        - 불필요한 특수문자 제거
        - 의미있는 키워드 추출
        """
        # 변수 패턴을 일반적인 표현으로 치환
        processed_text = re.sub(r'#\{([^}]+)\}', r'[변수:\1]', text)
        
        # 연속된 공백을 하나로 통일
        processed_text = re.sub(r'\s+', ' ', processed_text)
        
        # 특수문자 정리 (문장 부호는 유지)
        processed_text = re.sub(r'[^\w\s\[\]\(\)\.,!?가-힣]', ' ', processed_text)
        
        # 앞뒤 공백 제거
        processed_text = processed_text.strip()
        
        return processed_text

    def _analyze_rejection_reasons(self, hits: List[Dict[str, Any]], template_text: str) -> Dict[str, Any]:
        """
        반려 사유 검색 결과를 분석하여 위험도와 반려 가능성 평가
        
        Args:
            hits: 반려 사유 DB에서 검색된 결과들
            template_text: 검증 대상 템플릿 텍스트
            
        Returns:
            분석 결과 딕셔너리
        """
        if not hits:
            return {
                "risk_score": 0.0,
                "rejection_likelihood": "low",
                "potential_reasons": [],
                "similarity_analysis": []
            }
        
        # 유사도 점수 분석
        similarities = [hit.get('similarity', 0.0) for hit in hits]
        max_similarity = max(similarities) if similarities else 0.0
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        
        # 위험도 계산 (최고 유사도와 평균 유사도 가중평균)
        risk_score = (max_similarity * 0.7) + (avg_similarity * 0.3)
        
        # 반려 가능성 평가
        if max_similarity >= 0.8:
            rejection_likelihood = "high"
        elif max_similarity >= 0.6:
            rejection_likelihood = "medium"
        elif max_similarity >= 0.4:
            rejection_likelihood = "low"
        else:
            rejection_likelihood = "very_low"
        
        # 잠재적 반려 사유 추출
        potential_reasons = []
        similarity_analysis = []
        
        for hit in hits[:3]:  # 상위 3개만 분석
            similarity = hit.get('similarity', 0.0)
            content = hit.get('content', '')
            metadata = hit.get('metadata', {})
            
            # 반려 사유 정보 추출
            reason_code = metadata.get('reason_code', '')
            reason_description = metadata.get('reason', '')
            category = metadata.get('category', '')
            
            potential_reasons.append({
                "reason_code": reason_code,
                "description": reason_description,
                "category": category,
                "similarity": similarity,
                "evidence": content[:100] + "..." if len(content) > 100 else content
            })
            
            similarity_analysis.append({
                "reason": reason_description,
                "similarity": similarity,
                "risk_level": "high" if similarity >= 0.7 else "medium" if similarity >= 0.5 else "low"
            })
        
        return {
            "risk_score": round(risk_score, 4),
            "rejection_likelihood": rejection_likelihood,
            "potential_reasons": potential_reasons,
            "similarity_analysis": similarity_analysis,
            "max_similarity": max_similarity,
            "avg_similarity": round(avg_similarity, 4)
        }



    # ----------------------------- RAG 단계 -----------------------------------
    def _rag_stage(self, collection: str, text: str, k: int = 5, category_sub: str = None) -> Dict[str, Any]:
        # rejection_reasons 컬렉션 RAG 검색 (반려 사유 DB 기반)
        if collection == "rejection_reasons":
            # 템플릿 전처리 및 임베딩
            processed_text = self._preprocess_template_for_embedding(text)
            
            # 반려 사유 DB에서 유사한 사유 검색
            hits = self.chromadb_service.search_templates(
                collection_name="rejection_reasons",
                query_text=processed_text,
                category_sub=category_sub,
                top_k=k
            )
        elif collection == "approved_templates":
            if not category_sub:
                logger.warning("approved_templates 검색 시 category_sub가 필요합니다.")
                hits = []
            else:
                hits = self.chromadb_service.search_templates(
                    collection_name="approved_templates",
                    query_text=text,
                    category_sub=category_sub,
                    top_k=k
                )
        elif collection == "public_templates":
            hits = self.chromadb_service.search_templates(
                collection_name="public_templates",
                query_text=text,
                top_k=k,
                result_format="legacy"
            )
        else:
            logger.warning(f"알 수 없는 컬렉션 이름입니다: {collection}")
            hits = []
        # 반려 사유 분석 수행
        if collection == "rejection_reasons":
            analysis_result = self._analyze_rejection_reasons(hits, text)
            
            # 분석 결과를 기반으로 점수와 라벨 결정
            risk_score = analysis_result["risk_score"]
            rejection_likelihood = analysis_result["rejection_likelihood"]
            
            # 반려 가능성에 따른 라벨 결정
            if rejection_likelihood == "high":
                label = "fail"
            elif rejection_likelihood == "medium":
                label = "review"
            else:
                label = "pass"
            
            # evidence 생성 (잠재적 반려 사유들)
            evidence = []
            for reason in analysis_result["potential_reasons"]:
                evidence.append({
                    "source": "rejection_reasons",
                    "policy_ref": reason["reason_code"],
                    "reason": reason["description"],
                    "evidence": reason["evidence"],
                    "score": reason["similarity"],
                    "category": reason["category"]
                })
            
            return {
                "stage": f"{collection}_rag",
                "label": label,
                "score": risk_score,
                "thresholds": {"reject": REJECT_THRESHOLD, "review": REVIEW_THRESHOLD},
                "evidence": evidence,
                "analysis": analysis_result,  # 상세 분석 결과 포함
            }
        else:
            # 기존 로직 (다른 컬렉션용)
            top_score = 0.0
            evidence: List[Dict[str, Any]] = []
            
            if hits:
                for h in hits[:EVIDENCE_LIMIT]:
                    similarity = h.get('similarity', 0.0)
                    top_score = max(top_score, similarity)
                    
                    md = (h.get("metadata") or {})
                    evidence.append({
                        "source": collection,
                        "policy_ref": md.get("policy_ref") or md.get("reason_code"),
                        "reason": md.get("reason") or f"Similar {collection}",
                        "evidence": h.get("content") or md.get("chunk") or "",
                        "score": similarity,
                    })
            
            # 점수 기반 라벨 결정
            if top_score >= REJECT_THRESHOLD:
                label = "fail"
            elif top_score >= REVIEW_THRESHOLD:
                label = "review"
            else:
                label = "pass"

            return {
                "stage": f"{collection}_rag",
                "label": label,
                "score": round(top_score, 4),
                "thresholds": {"reject": REJECT_THRESHOLD, "review": REVIEW_THRESHOLD},
                "evidence": evidence,
            }


