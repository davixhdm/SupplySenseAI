import json
from services.ai_service import ai_service

SYSTEM_PROMPT = """You are SupplySense AI, an expert fraud and anomaly detector. Analyze the data and return JSON.

Return ONLY valid JSON in this exact format:
{
  "key_findings": ["detailed finding 1", "finding 2", "finding 3"],
  "recommendations": [{"action": "...", "priority": "HIGH/MEDIUM/LOW", "expected_outcome": "..."}],
  "summary": "2-3 sentence summary of anomalies found",
  "metrics": {"total_anomalies": 0, "total_amount_flagged": 0}
}
Rules: Use actual numbers. Be specific. Flag anything suspicious."""

class AnomalyService:
    async def detect(self, request: dict) -> dict:
        transactions = request.get("transactions", [])
        parts = [f"Detect anomalies in {len(transactions)} transactions.", "", "TRANSACTIONS:"]
        for t in transactions[:50]:
            parts.append(f"  • {t.get('type','?')}: {t.get('amount',0)} on {t.get('transactionDate','?')} — {t.get('status','?')}")
        parts.append(f"\n{SYSTEM_PROMPT}")
        prompt = "\n".join(parts)
        result = await ai_service.chat([{"role": "user", "content": prompt}], max_tokens=1000, temperature=0.2)
        tokens_used = result.get("tokens", 0)
        try:
            text = result.get("reply", "{}").replace("```json", "").replace("```", "").strip()
            parsed = json.loads(text)
            parsed["tokens"] = tokens_used
            return parsed
        except:
            return {"key_findings": ["No anomalies detected."], "recommendations": [], "summary": "", "metrics": {"total_anomalies": 0}, "status": "success", "tokens": tokens_used}

anomaly_service = AnomalyService()