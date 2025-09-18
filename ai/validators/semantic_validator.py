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

# 전역 변수 선언
REJECT = 0.6        # RISK 가 0.6 이상 이면 REJECT
REVIEW = 0.4        # RISK 가 0.4 이상, REJECT 미만 이면 REVIEW
WB, WD = 1.0, 1.0   # 표시/튜닝용 종합 위험도: 가중 평균 계산용 (blacklist와 denied_templates 동등하게 처리)
DMAX = 1.0          # distance 상한(코사인 거리 0~1이면 1.0, 0~2 라이브러리면 2.0)

# =============================================================================
# 유틸: raw(hit) → risk[0..1], 라벨링
# =============================================================================
def _risk_from_hit(hit: Dict[str, Any], dmax: float = DMAX) -> float:
    """
    hit에 'similarity'나 'distance'가 무엇이 오든 risk ∈ [0,1](클수록 위험)로 통일
    - similarity: [-1,1] 또는 [0,1] → 0~1 매핑
    - distance  : [0,dmax] (작을수록 유사) → risk = 1 - (distance/dmax)
    """
    if "similarity" in hit and hit["similarity"] is not None:
        sim = float(hit["similarity"])
        if sim < 0:  # [-1,1] → [0,1]
            sim = (sim + 1.0) / 2.0
        return max(0.0, min(1.0, sim))
    if "distance" in hit and hit["distance"] is not None:
        d = float(hit["distance"])
        return max(0.0, min(1.0, 1.0 - (d / dmax)))
    return 0.0

def _label_from_risk(r: float) -> str:
    if r >= REJECT: return "fail"
    if r >= REVIEW: return "review"
    return "pass"

class SemanticValidator:
    """의미적 검증기 (RAG 기반)"""
    
    def __init__(self, openai_api_key: str = None):
        """
        Args:
            openai_api_key: OpenAI API 키
        """
        # 2차 검증용 blacklist, denied_templates  컬렉션 병렬 사용
        self.vdb = vector_db_manager
        self.bl = ChromaDBService(collection_name="blacklist")
        self.dn = ChromaDBService(collection_name="denied_templates")

        
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
    
    def validate(self, template: Dict[str, Any]) -> ValidationResult:
        """
        최상위 엔트리: 두 단계 RAG → 라벨링 → 취합 → (review면 LLM 판정) / (fail이면 LLM 사유 요약)
        항상 동일 스키마의 ValidationResult를 반환.
        """
        text = f"{template.get('templateTitle','')} {template.get('templateContent','')}".strip()
        category = template.get("category")

        # 1) 두 컬렉션 RAG (병렬 개념, 구현은 순차 호출)
        s_bl = self._rag_stage("blacklist", text, k=6)
        s_dn = self._rag_stage("denied_templates", text, k=5, where={"category": category} if category else None)

        # 2) 최종 취합
        final_label, final_risk, violations = _aggregate([s_bl, s_dn])

        decision_source = "heuristic"
        needs_review: bool = False
        warnings: List[str] = []

        # 3) 분기
        if final_label == "review":
            if self.openai_client:
                llm_out = self._llm_judge(template, [s_bl, s_dn])
                final_label = "pass" if llm_out.get("is_valid", True) else "fail"
                if llm_out.get("violations"):
                    violations = llm_out["violations"]
                decision_source = "llm"
            else:
                needs_review = True
                warnings.append("LLM 미구성: 사람 검토 필요")
        elif final_label == "fail":
            # 판정은 이미 확정. 선택적으로 LLM에게 '사유 요약/메시지'만 요청
            if self.openai_client:
                llm_reason = self._llm_fail_reason(template, [s_bl, s_dn])
                if llm_reason:
                    violations = llm_reason  # 요약을 violations에 덮어쓰기(또는 extend)

        is_valid = (final_label == "pass")

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
    def _rag_stage(self, collection: str, text: str, k: int = 5, where: Dict[str, Any] | None = None) -> Dict[str, Any]:
        hits = self._search(collection, text, n_results=k, where=where) or []
        scores = [ _risk_from_hit(h) for h in hits ]
        top = max(scores) if scores else 0.0
        label = _label_from_risk(top)

        evidence: List[Dict[str, Any]] = []
        for h, s in list(zip(hits, scores))[:3]:
            md = (h.get("metadata") or {})
            evidence.append({
                "source": collection,
                "policy_ref": md.get("policy_ref") or md.get("reason_code"),
                "reason": md.get("reason") or f"Similar {collection}",
                "evidence": h.get("content") or md.get("chunk") or "",
                "score": round(s, 4),
            })

        return {
            "stage": f"{collection}_rag",
            "label": label,                              # pass | review | fail
            "score": round(top, 4),                      # 위험도(0~1)
            "thresholds": {"reject": REJECT, "review": REVIEW},
            "evidence": evidence,
        }

    def _search(self, collection: str, text: str, n_results: int = 5, where: Dict[str, Any] | None = None) -> List[Dict]:
        # vector_db_manager가 있으면 우선 사용
        if self.vdb:
            try:
                return self.vdb.search_similar(query=text, n_results=n_results, collection=collection, where=where)
            except Exception:
                pass
        # fallback: 컬렉션별 ChromaDBService
        svc = self.bl if collection == "blacklist" else self.dn
        # ChromaDBService는 category_filter 파라미터를 사용
        category_filter = where.get("category") if where else None
        return svc.search_similar(query=text, n_results=n_results, category_filter=category_filter)

    # ----------------------------- LLM 보조 ------------------------------------
    def _llm_judge(self, template: Dict[str, Any], stages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """review 구간: LLM으로 최종 판정(JSON)"""
        if not (HAS_OPENAI and self.openai_client):
            return {"is_valid": False, "violations": [], "rationale": "no LLM configured"}

        # 컨텍스트 구성(두 단계 evidence 합침)
        ctx = []
        for s in stages:
            for e in s.get("evidence", []):
                ctx.append({"content": e["evidence"], "metadata": {"policy_ref": e.get("policy_ref"),
                                                                   "source": e.get("source"),
                                                                   "score": e.get("score")}})
          
        prompt = create_final_validation_prompt(
            template_data=template,
            det_report_summary={"constraint_passed": True, "issues_found": [], "warnings": []},
            rag_guidelines=ctx
        )
        try:
            resp = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_completion_tokens=1000,
            )
            txt = resp.choices[0].message.content.strip()
            if txt.startswith("```"):
                txt = "\n".join(line for line in txt.splitlines() if not line.startswith("```"))
            out = json.loads(txt)
            return out
        except Exception as e:
            return {"is_valid": False, "violations": [{"reason": f"LLM error: {e}"}]}

    def _llm_fail_reason(self, template: Dict[str, Any], stages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """fail 구간: LLM에게 '왜 실패인지' 근거 요약만 받아오고 붙임(판정은 바꾸지 않음)"""
        if not (HAS_OPENAI and self.openai_client):
            # LLM이 없으면 stage evidence를 그대로 반환
            viols: List[Dict[str, Any]] = []
            for s in stages:
                if s["label"] == "fail":
                    viols.extend(s.get("evidence", []))
            return viols[:5]

        snippets = []
        for s in stages:
            if s["label"] == "fail":
                for e in s.get("evidence", []):
                    snippets.append(f"- [{e.get('source')}] {e.get('policy_ref') or ''} :: {e['evidence'][:300]}")

        if not snippets:
            return []

        user_prompt = (
                "아래 근거를 바탕으로 왜 정책 위반(Fail)인지 최대 3가지 이유로 한국어 JSON을 만들어줘. "
                'JSON 스키마: {"violations":[{"policy_ref":"...", "reason":"...", "evidence":"..."}]}.\n\n'
                "근거 스니펫:\n" + "\n".join(snippets)
        )
        try:
            resp = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.2,
                max_completion_tokens=600,
            )
            txt = resp.choices[0].message.content.strip()
            if txt.startswith("```"):
                txt = "\n".join(line for line in txt.splitlines() if not line.startswith("```"))
            out = json.loads(txt)
            return out.get("violations", [])
        except Exception:
            # 실패 시에도 최소한의 근거는 반환
            viols: List[Dict[str, Any]] = []
            for s in stages:
                if s["label"] == "fail":
                    viols.extend(s.get("evidence", []))
            return viols[:5]

# =============================================================================
# 최종 취합 함수(클래스 밖으로 분리: 테스트 용이)
# =============================================================================
def _aggregate(stages: List[Dict[str, Any]]) -> tuple[str, float, List[Dict[str, Any]]]:
    """
    라벨 우선 규칙으로 최종 라벨을 정하고, 표시/튜닝용 final_risk와 violations를 만든다.
    - 하나라도 fail → fail
    - fail 없고 하나라도 review → review
    - 둘 다 pass → pass
    """
    labels = {s["label"] for s in stages}
    if "fail" in labels:
        final = "fail"
    elif "review" in labels:
        final = "review"
    else:
        final = "pass"

    risk_bl = next((s["score"] for s in stages if s["stage"] == "blacklist_rag"), 0.0)
    risk_dn = next((s["score"] for s in stages if s["stage"] == "denied_templates_rag"), 0.0)
    final_risk = round(max(WB * risk_bl, WD * risk_dn), 4)

    violations: List[Dict[str, Any]] = []
    if final in ("review", "fail"):
        for s in stages:
            if s["label"] in ("review", "fail"):
                violations.extend(s.get("evidence", []))

    return final, final_risk, violations