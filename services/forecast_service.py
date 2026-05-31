import json
from services.ai_service import ai_service

class ForecastService:
    async def stockout(self, request: dict) -> dict:
        current = request.get("currentStock", 0)
        reorder = request.get("reorderThreshold", 10)
        daily = request.get("dailyDemand", 1)
        lead = request.get("leadTime", 7)
        
        days_left = (current - reorder) / daily if daily > 0 else 999
        risk = "high" if days_left < 7 else "medium" if days_left < 14 else "low"
        reorder_in = max(0, days_left - lead)

        prompt = f"""Analyze stockout risk:
- Current Stock: {current}
- Reorder Threshold: {reorder}
- Daily Demand: {daily}
- Lead Time: {lead} days
- Days Until Stockout: {days_left:.1f}
- Risk Level: {risk}

Return JSON:
{{
    "riskLevel": "{risk}",
    "daysUntilStockout": {days_left:.1f},
    "recommendedReorderDate": "In {reorder_in:.0f} days",
    "key_findings": "analysis with real numbers",
    "recommendations": [{{"action": "...", "priority": "...", "expected_outcome": "..."}}],
    "status": "success"
}}"""

        result = await ai_service.chat([{"role": "user", "content": prompt}], max_tokens=500, temperature=0.2)
        try:
            return json.loads(result.get("reply", "{}").replace("```json", "").replace("```", "").strip())
        except:
            return {"riskLevel": risk, "daysUntilStockout": days_left, "status": "error"}

    async def demand(self, request: dict) -> dict:
        products = request.get("products", [])
        periods = request.get("periods", 7)

        parts = [f"Forecast demand for {len(products)} products over {periods} days.", "", "PRODUCTS:"]
        for p in products[:20]:
            parts.append(f"  • {p.get('name','?')}: Stock {p.get('stockLevel',0)}")

        parts.append("""
Return JSON:
{
    "key_findings": "demand forecast insights",
    "recommendations": [{"action": "...", "priority": "...", "expected_outcome": "..."}],
    "status": "success"
}""")

        prompt = "\n".join(parts)
        result = await ai_service.chat([{"role": "user", "content": prompt}], max_tokens=800, temperature=0.3)
        try:
            return json.loads(result.get("reply", "{}").replace("```json", "").replace("```", "").strip())
        except:
            return {"key_findings": "Could not forecast.", "status": "error"}

forecast_service = ForecastService()