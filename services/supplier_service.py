import json
from services.ai_service import ai_service

class SupplierService:
    async def score(self, request: dict) -> dict:
        suppliers = request.get("suppliers", [])

        parts = [f"Score and rank {len(suppliers)} suppliers.", "", "SUPPLIERS:"]
        for s in suppliers[:20]:
            parts.append(f"  • {s.get('name','?')}: Reliability {s.get('reliabilityScore',0)}%, On-time {s.get('onTimeDeliveries',0)}/{s.get('totalOrders',0)}")

        parts.append("""
Return JSON:
{
    "key_findings": "supplier rankings and insights with real names and scores",
    "recommendations": [{"action": "...", "priority": "...", "expected_outcome": "..."}],
    "status": "success"
}""")

        prompt = "\n".join(parts)
        result = await ai_service.chat([{"role": "user", "content": prompt}], max_tokens=600, temperature=0.3)
        try:
            return json.loads(result.get("reply", "{}").replace("```json", "").replace("```", "").strip())
        except:
            return {"key_findings": "Could not score suppliers.", "status": "error"}

supplier_service = SupplierService()