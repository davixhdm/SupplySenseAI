import json
from services.ai_service import ai_service

SYSTEM_PROMPT = """You are SupplySense AI, an expert supply chain analyst. Analyze the provided business data and return a JSON response.

Return ONLY valid JSON in this exact format:
{
  "key_findings": ["detailed finding 1 with specific numbers and business context", "detailed finding 2 with analysis", "detailed finding 3 with trends"],
  "recommendations": [
    {"action": "specific actionable step", "priority": "HIGH/MEDIUM/LOW", "expected_outcome": "what business impact this will have"}
  ],
  "summary": "2-3 sentence executive summary with key numbers and trends",
  "metrics": {"metric_name": numeric_value}
}

Rules:
- Use actual numbers from the data provided
- Be specific and detailed — explain WHY each finding matters to the business
- HIGH priority = urgent action needed now, MEDIUM = this week, LOW = this month
- Give 4-6 key findings with business context
- Give 3-5 specific, actionable recommendations
- Include all relevant metrics with values
- Write like a human business analyst, not a robot
- Mention specific product names, customer names, and numbers when available"""

class InsightsService:
    async def analyze(self, request: dict) -> dict:
        query = request.get("query", "")
        category = request.get("category", "general")
        data = request.get("data", {})

        parts = ["--- REAL BUSINESS DATA ---"]

        if "products" in data:
            parts.append(f"\nPRODUCTS ({len(data['products'])}):")
            for p in data["products"][:15]:
                stock = p.get("stockLevel", 0); reorder = p.get("reorderThreshold", 10)
                status = "⚠️ LOW" if stock <= reorder else "OK"
                parts.append(f"  • {p.get('name','?')}: Stock {stock} (reorder at {reorder}) — {status}, Price {p.get('sellingPrice',0)}, Cost {p.get('unitCost',0)}")

        if "suppliers" in data:
            parts.append(f"\nSUPPLIERS ({len(data['suppliers'])}):")
            for s in data["suppliers"][:10]:
                parts.append(f"  • {s.get('name','?')}: Reliability {s.get('reliabilityScore',0)}%, On-time {s.get('onTimeDeliveries',0)}/{s.get('totalOrders',0)}")

        if "customers" in data:
            parts.append(f"\nCUSTOMERS ({len(data['customers'])}):")
            for c in data["customers"][:10]:
                parts.append(f"  • {c.get('fullName','?')}: Spent {c.get('totalSpent',0)}, {c.get('purchaseCount',0)} purchases, Churn risk {c.get('churnRisk',0)}%, Last purchase {c.get('lastPurchaseDate','?')}")

        if "orders" in data:
            parts.append(f"\nORDERS ({len(data['orders'])}):")
            for o in data["orders"][:10]:
                delayed = " ⚠️ DELAYED" if o.get("isDelayed") else ""
                parts.append(f"  • {o.get('orderNumber','?')}: {o.get('totalAmount',0)} — {o.get('status','?')}{delayed}")

        if "transactions" in data:
            total_amount = sum(t.get("amount", 0) for t in data["transactions"])
            sale_count = len([t for t in data["transactions"] if t.get("type") == "sale"])
            parts.append(f"\nTRANSACTIONS ({len(data['transactions'])}): Total {total_amount}, {sale_count} sales")
            for t in data["transactions"][:10]:
                anomaly = " ⚠️ ANOMALY" if t.get("isAnomaly") else ""
                parts.append(f"  • {t.get('type','?')}: {t.get('amount',0)} on {t.get('transactionDate','?')}{anomaly}")

        if "employees" in data:
            parts.append(f"\nEMPLOYEES ({len(data['employees'])}):")
            for e in data["employees"][:10]:
                parts.append(f"  • {e.get('fullName','?')}: {e.get('department','?')}, Performance {e.get('performanceScore',0)}%, Efficiency {e.get('efficiency',0)}%")

        parts.append(f"""
        
User asked: "{query}"
Category: {category}

{SYSTEM_PROMPT}""")

        prompt = "\n".join(parts)
        result = await ai_service.chat([{"role": "user", "content": prompt}], max_tokens=2000, temperature=0.3)
        tokens_used = result.get("tokens", 0)

        try:
            text = result.get("reply", "{}").replace("```json", "").replace("```", "").strip()
            parsed = json.loads(text)
            parsed["tokens"] = tokens_used
            return parsed
        except:
            return {"query": query, "category": category, "key_findings": ["Could not analyze data."], "recommendations": [], "summary": "Analysis failed.", "metrics": {}, "status": "error", "tokens": tokens_used}

insights_service = InsightsService()