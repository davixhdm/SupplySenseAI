
import json
from services.ai_service import ai_service

class AnomalyService:
    async def detect(self, request: dict) -> dict:
        transactions = request.get("transactions", [])

        parts = [f"Detect anomalies in {len(transactions)} transactions.", "", "TRANSACTIONS:"]
        for t in transactions[:50]:
            parts.append(f"  • {t.get('type','?')}: {t.get('amount',0)} on {t.get('transactionDate','?')} — {t.get('status','?')}")

        parts.append("""
Return JSON:
{
    "key_findings": "anomaly detection results with specific findings",
    "recommendations": [{"action": "...", "priority": "...", "expected_outcome": "..."}],
    "status": "success"
}
If no anomalies, say so.""")

        prompt = "\n".join(parts)
        result = await ai_service.chat([{"role": "user", "content": prompt}], max_tokens=600, temperature=0.2)
        try:
            return json.loads(result.get("reply", "{}").replace("```json", "").replace("```", "").strip())
        except:
            return {"key_findings": "No anomalies detected.", "recommendations": [], "status": "success"}

anomaly_service = AnomalyService()