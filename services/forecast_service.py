import json
from services.ai_service import ai_service

SYSTEM_PROMPT = """You are SupplySense AI, an expert supply chain forecaster. Analyze the data and return JSON.

Return ONLY valid JSON in this exact format:
{
  "key_findings": ["detailed finding 1 with numbers", "finding 2", "finding 3"],
  "recommendations": [{"action": "...", "priority": "HIGH/MEDIUM/LOW", "expected_outcome": "..."}],
  "summary": "2-3 sentence forecast summary",
  "metrics": {"metric_name": numeric_value}
}
Rules: Use actual numbers. Be specific. HIGH = urgent now, MEDIUM = this week, LOW = this month."""

class ForecastService:
    async def stockout(self, request: dict) -> dict:
        current = request.get("currentStock", 0); reorder = request.get("reorderThreshold", 10)
        daily = request.get("dailyDemand", 1); lead = request.get("leadTime", 7)
        days_left = (current - reorder) / daily if daily > 0 else 999
        risk = "high" if days_left < 7 else "medium" if days_left < 14 else "low"
        reorder_in = max(0, days_left - lead)

        prompt = f"""Analyze stockout risk:
- Current Stock: {current}, Reorder Threshold: {reorder}
- Daily Demand: {daily}, Lead Time: {lead} days
- Days Until Stockout: {days_left:.1f}, Risk Level: {risk}
- Recommended Reorder: In {reorder_in:.0f} days

{SYSTEM_PROMPT}"""

        result = await ai_service.chat([{"role": "user", "content": prompt}], max_tokens=1000, temperature=0.2)
        tokens_used = result.get("tokens", 0)
        try:
            text = result.get("reply", "{}").replace("```json", "").replace("```", "").strip()
            parsed = json.loads(text)
            parsed["riskLevel"] = risk
            parsed["daysUntilStockout"] = round(days_left, 1)
            parsed["tokens"] = tokens_used
            return parsed
        except:
            return {"riskLevel": risk, "daysUntilStockout": round(days_left, 1), "key_findings": ["Could not analyze."], "recommendations": [], "summary": "", "metrics": {}, "status": "error", "tokens": tokens_used}

    async def demand(self, request: dict) -> dict:
        products = request.get("products", []); periods = request.get("periods", 7)
        parts = [f"Forecast demand for {len(products)} products over {periods} days.", "", "PRODUCTS:"]
        for p in products[:20]:
            parts.append(f"  • {p.get('name','?')}: Stock {p.get('stockLevel',0)}")
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
            return {"key_findings": ["Could not forecast."], "recommendations": [], "summary": "", "metrics": {}, "status": "error", "tokens": tokens_used}

forecast_service = ForecastService()