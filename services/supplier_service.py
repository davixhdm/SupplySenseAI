import json
from services.ai_service import ai_service

SYSTEM_PROMPT = """You are SupplySense AI, an expert supplier analyst. Analyze the data and return JSON.

Return ONLY valid JSON in this exact format:
{
  "key_findings": ["detailed finding 1 with supplier names and scores", "finding 2", "finding 3"],
  "recommendations": [{"action": "...", "priority": "HIGH/MEDIUM/LOW", "expected_outcome": "..."}],
  "summary": "2-3 sentence supplier performance summary",
  "metrics": {"best_supplier": "", "worst_supplier": "", "avg_reliability": 0}
}
Rules: Use actual names and scores. Rank suppliers from best to worst."""

class SupplierService:
    async def score(self, request: dict) -> dict:
        suppliers = request.get("suppliers", [])
        parts = [f"Score and rank {len(suppliers)} suppliers.", "", "SUPPLIERS:"]
        for s in suppliers[:20]:
            parts.append(f"  • {s.get('name','?')}: Reliability {s.get('reliabilityScore',0)}%, On-time {s.get('onTimeDeliveries',0)}/{s.get('totalOrders',0)}")
        parts.append(f"\n{SYSTEM_PROMPT}")
        prompt = "\n".join(parts)
        result = await ai_service.chat([{"role": "user", "content": prompt}], max_tokens=1000, temperature=0.3)
        tokens_used = result.get("tokens", 0)
        try:
            text = result.get("reply", "{}").replace("```json", "").replace("```", "").strip()
            parsed = json.loads(text)
            parsed["tokens"] = tokens_used
            return parsed
        except:
            return {"key_findings": ["Could not score suppliers."], "recommendations": [], "summary": "", "metrics": {}, "status": "error", "tokens": tokens_used}

supplier_service = SupplierService()