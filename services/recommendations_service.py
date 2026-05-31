import json
from services.ai_service import ai_service

SYSTEM_PROMPT = """You are SupplySense AI, an expert business strategist. Analyze ALL the data and return JSON.

Return ONLY valid JSON in this exact format:
{
  "key_findings": ["detailed cross-category finding 1", "finding 2", "finding 3", "finding 4"],
  "recommendations": [{"action": "...", "priority": "HIGH/MEDIUM/LOW", "expected_outcome": "..."}],
  "summary": "2-3 sentence strategic summary",
  "metrics": {"total_products": 0, "total_customers": 0, "total_revenue": 0}
}
Rules: Look across ALL categories. Give 5-8 recommendations. HIGH = urgent, MEDIUM = this week, LOW = this month."""

class RecommendationsService:
    async def generate(self, request: dict) -> dict:
        data_parts = []
        if request.get("products"): data_parts.append(f"Products: {len(request['products'])}")
        if request.get("suppliers"): data_parts.append(f"Suppliers: {len(request['suppliers'])}")
        if request.get("customers"): data_parts.append(f"Customers: {len(request['customers'])}")
        if request.get("transactions"): data_parts.append(f"Transactions: {len(request['transactions'])}")

        prompt = f"""Generate business recommendations based on this data: {', '.join(data_parts)}

Full data: {json.dumps(request, indent=2)[:4000]}

{SYSTEM_PROMPT}"""

        result = await ai_service.chat([{"role": "user", "content": prompt}], max_tokens=1500, temperature=0.4)
        tokens_used = result.get("tokens", 0)
        try:
            text = result.get("reply", "{}").replace("```json", "").replace("```", "").strip()
            parsed = json.loads(text)
            parsed["tokens"] = tokens_used
            return parsed
        except:
            return {"key_findings": ["Could not generate recommendations."], "recommendations": [], "summary": "", "metrics": {}, "status": "error", "tokens": tokens_used}

recommendations_service = RecommendationsService()