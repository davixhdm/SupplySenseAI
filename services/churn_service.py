import json
from services.ai_service import ai_service

SYSTEM_PROMPT = """You are SupplySense AI, an expert customer retention analyst. Analyze the data and return JSON.

Return ONLY valid JSON in this exact format:
{
  "key_findings": ["detailed finding 1 with customer names and risk levels", "finding 2", "finding 3"],
  "recommendations": [{"action": "...", "priority": "HIGH/MEDIUM/LOW", "expected_outcome": "..."}],
  "summary": "2-3 sentence churn risk summary",
  "metrics": {"at_risk_customers": 0, "healthy_customers": 0, "avg_churn_risk": 0}
}
Rules: Use actual customer names and numbers. HIGH risk = churn within 30 days."""

class ChurnService:
    async def predict(self, request: dict) -> dict:
        customers = request.get("customers", [])
        parts = [f"Predict churn risk for {len(customers)} customers.", "", "CUSTOMERS:"]
        for c in customers[:20]:
            parts.append(f"  • {c.get('fullName','?')}: Spent {c.get('totalSpent',0)}, {c.get('purchaseCount',0)} purchases, Risk {c.get('churnRisk',0)}%, Last purchase {c.get('lastPurchaseDate','?')}")
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
            return {"key_findings": ["Could not predict churn."], "recommendations": [], "summary": "", "metrics": {}, "status": "error", "tokens": tokens_used}

churn_service = ChurnService()