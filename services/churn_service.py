import json
from services.ai_service import ai_service

class ChurnService:
    async def predict(self, request: dict) -> dict:
        customers = request.get("customers", [])

        parts = [f"Predict churn risk for {len(customers)} customers.", "", "CUSTOMERS:"]
        for c in customers[:20]:
            parts.append(f"  • {c.get('fullName','?')}: Spent {c.get('totalSpent',0)}, {c.get('purchaseCount',0)} purchases, Risk {c.get('churnRisk',0)}%, Last purchase {c.get('lastPurchaseDate','?')}")

        parts.append("""
Return JSON:
{
    "key_findings": "churn risk analysis with specific customer names and risk levels",
    "recommendations": [{"action": "...", "priority": "...", "expected_outcome": "..."}],
    "status": "success"
}""")

        prompt = "\n".join(parts)
        result = await ai_service.chat([{"role": "user", "content": prompt}], max_tokens=600, temperature=0.3)
        try:
            return json.loads(result.get("reply", "{}").replace("```json", "").replace("```", "").strip())
        except:
            return {"key_findings": "Could not predict churn.", "status": "error"}

churn_service = ChurnService()