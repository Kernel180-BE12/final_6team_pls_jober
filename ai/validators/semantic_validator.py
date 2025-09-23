import logging
from typing import Dict, Any, List

from services.chromadb_service import ChromaDBService
from models.alimtalk_models import ValidationResult

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

    # ... (validate, _rag_stage, _llm_judge, _llm_fail_reason 등 나머지 메서드는 그대로 유지) ...
    # 단, _rag_stage 내부에서 self._search를 호출하는 부분은 이제 정상적으로 동작합니다.
    def validate(self, template: Dict[str, Any]) -> ValidationResult:
        """
        최상위 엔트리: 두 단계 RAG → 라벨링 → 취합 → (review면 LLM 판정) / (fail이면 LLM 사유 요약)
        항상 동일 스키마의 ValidationResult를 반환.
        """
        print("🔍 SemanticValidator.validate() 시작")
        text = f"{template.get('template_title','')} {template.get('template_content','')}".strip()
        category = template.get("category")
        print(f"검증 대상 텍스트: {text[:self.TEXT_PREVIEW_LENGTH]}...")
        print(f"카테고리: {category}")

        # 1) 두 컬렉션 RAG (병렬 개념, 구현은 순차 호출)
        print("🔍 approved_templates 컬렉션 검색 시작...")
        s_bl = self._rag_stage("approved_templates", text, k=self.APPROVED_SEARCH_K, category_sub=category)
        print(f"approved_templates 결과: {s_bl}")

        print("🔍 pulblic_templates 컬렉션 검색 시작...")
        s_dn = self._rag_stage("pulblic_templates", text, k=self.PUBLIC_SEARCH_K)
        print(f"pulblic_templates 결과: {s_dn}")

        # 만약 결과가 없다면 카테고리 필터 때문일 수 있으니 로그 출력
        if s_dn.get('score', 0) == 0:
            print(f"⚠️ pulblic_templates에서 결과 없음. 카테고리: {category}")

        # 2) 최종 취합 - 실제 RAG 결과를 기반으로 계산
        # 두 단계 결과를 종합하여 최종 판정
        approved_score = s_bl.get('score', 0.0)
        public_score = s_dn.get('score', 0.0)
        
        # 더 높은 위험도를 최종 위험도로 사용
        final_risk = max(approved_score, public_score)
        
        # 위험도 기반 최종 라벨 결정
        if final_risk >= self.REJECT_THRESHOLD:
            final_label = "fail"
        elif final_risk >= self.REVIEW_THRESHOLD:
            final_label = "review"
        else:
            final_label = "pass"
        
        # 위반 사항 수집
        violations = []
        if s_bl.get('label') in ['fail', 'review']:
            for evidence in s_bl.get('evidence', []):
                if evidence.get('score', 0) >= self.VIOLATION_THRESHOLD:
                    violations.append({
                        "source": "approved_templates",
                        "reason": evidence.get('reason', '승인된 템플릿과 유사'),
                        "evidence": evidence.get('evidence', ''),
                        "score": evidence.get('score', 0)
                    })
        
        if s_dn.get('label') in ['fail', 'review']:
            for evidence in s_dn.get('evidence', []):
                if evidence.get('score', 0) >= self.VIOLATION_THRESHOLD:
                    violations.append({
                        "source": "public_templates",
                        "reason": evidence.get('reason', '공용 템플릿과 유사'),
                        "evidence": evidence.get('evidence', ''),
                        "score": evidence.get('score', 0)
                    })
        print(f"\n📋 2차 검증 취합 결과:")
        print(f"   🏷️ 최종 라벨: {final_label}")
        print(f"   📊 위험도 점수: {final_risk}")
        print(f"   🚫 위반 사항: {len(violations)}개")

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
            for i, v in enumerate(violations[:self.VIOLATION_DISPLAY_LIMIT], 1):  # 최대 3개만 표시
                print(f"      {i}. {v.get('reason', '알 수 없는 사유')} (출처: {v.get('source', '알 수 없음')})")

        details = {
            "final_label": final_label,             # pass | review | fail
            "final_risk": final_risk,               # 표시/튜닝용
            "decision_source": decision_source,     # heuristic | llm | human
            "needs_review": needs_review,           # true면 운영 큐로 라우팅
            "stage_details": [s_bl, s_dn],          # 각 단계 스코어/라벨/근거
            "violations": violations,               # fail/review 근거
        }
        return ValidationResult(
            is_valid=is_valid,
            stage="semantic",
            errors=[] if is_valid else [v.get("reason") or "정책 위반 의심" for v in violations] or ["검토 필요"],
            warnings=warnings,
            details=details,
        )

    # ----------------------------- RAG 단계 -----------------------------------
    def _rag_stage(self, collection: str, text: str, k: int = 5, category_sub: str = None) -> Dict[str, Any]:
        # 직접 chromadb_service 메서드 호출
        if collection == "approved_templates":
            if not category_sub:
                logger.warning("approved_templates 검색 시 category_sub가 필요합니다.")
                hits = []
            else:
                hits, _ = self.chromadb_service.search_approved_templates(query_text=text, category_sub=category_sub, top_k=k)
        elif collection == "pulblic_templates":
            hits = self.chromadb_service.search_public_templates(query_text=text, top_k=k)
        else:
            logger.warning(f"알 수 없는 컬렉션 이름입니다: {collection}")
            hits = []
        # 실제 검색 결과를 기반으로 점수와 라벨 계산
        top_score = 0.0
        evidence: List[Dict[str, Any]] = []
        
        # 검색 결과가 있는 경우 실제 유사도 점수 사용
        if hits:
            for h in hits[:self.EVIDENCE_LIMIT]:
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
        if top_score >= self.REJECT_THRESHOLD:
            label = "fail"  # 높은 유사도 = 위험
        elif top_score >= self.REVIEW_THRESHOLD:
            label = "review"  # 중간 유사도 = 검토 필요
        else:
            label = "pass"  # 낮은 유사도 = 안전

        return {
            "stage": f"{collection}_rag",
            "label": label,                              # pass | review | fail
            "score": round(top_score, 4),                      # 위험도(0~1)
            "thresholds": {"reject": self.REJECT_THRESHOLD, "review": self.REVIEW_THRESHOLD},
            "evidence": evidence,
        }

