import json
from services.ai_service import ai_service

class RecommendationsService:
    async def generate(self, request: dict) -> dict:
        data_parts = []
        if request.get("products"):
            data_parts.append(f"Products: {len(request['products'])}")
        if request.get("suppliers"):
            data_parts.append(f"Suppliers: {len(request['suppliers'])}")
        if request.get("customers"):
            data_parts.append(f"Customers: {len(request['customers'])}")
        if request.get("transactions"):
            data_parts.append(f"Transactions: {len(request['transactions'])}")

        prompt = f"""Generate business recommendations based on this data: {', '.join(data_parts)}

Full data: {json.dumps(request, indent=2)[:4000]}

Return JSON:
{{
    "key_findings": "cross-category business insights",
    "recommendations": [
        {{"action": "specific actionable recommendation", "priority": "HIGH/MEDIUM/LOW", "expected_outcome": "expected result"}}
    ],
    "status": "success"
}}

Provide 5-10 specific, actionable recommendations based on the real data."""

        result = await ai_service.chat([{"role": "user", "content": prompt}], max_tokens=1200, temperature=0.4)
        try:
            return json.loads(result.get("reply", "{}").replace("```json", "").replace("```", "").strip())
        except:
            return {"key_findings": "Could not generate recommendations.", "recommendations": [], "status": "error"}

recommendations_service = RecommendationsService()