import json
from services.ai_service import ai_service
from loguru import logger

class InsightsService:
    async def analyze(self, request: dict) -> dict:
        query = request.get("query", "")
        category = request.get("category", "general")
        data = request.get("data", {})

        parts = ["You are SupplySense AI. Analyze this REAL business data and provide insights.", "", "--- REAL DATA ---"]

        if "products" in data:
            parts.append(f"\nPRODUCTS ({len(data['products'])}):")
            for p in data["products"][:15]:
                stock = p.get("stockLevel", 0)
                reorder = p.get("reorderThreshold", 10)
                status = "⚠️ LOW" if stock <= reorder else "OK"
                parts.append(f"  • {p.get('name','?')}: Stock {stock} (reorder at {reorder}) — {status}, Price {p.get('sellingPrice',0)}, Cost {p.get('unitCost',0)}")

        if "suppliers" in data:
            parts.append(f"\nSUPPLIERS ({len(data['suppliers'])}):")
            for s in data["suppliers"][:10]:
                parts.append(f"  • {s.get('name','?')}: Reliability {s.get('reliabilityScore',0)}%, On-time {s.get('onTimeDeliveries',0)}/{s.get('totalOrders',0)}")

        if "customers" in data:
            parts.append(f"\nCUSTOMERS ({len(data['customers'])}):")
            for c in data["customers"][:10]:
                parts.append(f"  • {c.get('fullName','?')}: Spent {c.get('totalSpent',0)}, {c.get('purchaseCount',0)} purchases, Churn risk {c.get('churnRisk',0)}%")

        if "orders" in data:
            parts.append(f"\nORDERS ({len(data['orders'])}):")
            for o in data["orders"][:10]:
                delayed = " ⚠️ DELAYED" if o.get("isDelayed") else ""
                parts.append(f"  • {o.get('orderNumber','?')}: {o.get('totalAmount',0)} — {o.get('status','?')}{delayed}")

        if "transactions" in data:
            total_amount = sum(t.get("amount", 0) for t in data["transactions"])
            parts.append(f"\nTRANSACTIONS ({len(data['transactions'])}): Total {total_amount}")
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

Return ONLY valid JSON (no markdown, no backticks):
{{
    "query": "{query}",
    "category": "{category}",
    "key_findings": "specific insights with real numbers from the data above",
    "supporting_metrics": {{
        "totalRevenue": 0,
        "salesCount": 0,
        "avgSale": 0
    }},
    "recommendations": [
        {{"action": "specific action", "priority": "HIGH/MEDIUM/LOW", "expected_outcome": "..."}}
    ],
    "status": "success"
}}

Calculate supporting_metrics from the real data. Use actual numbers.""")

        prompt = "\n".join(parts)
        result = await ai_service.chat([{"role": "user", "content": prompt}], max_tokens=1500, temperature=0.3)
        tokens_used = result.get("tokens", 0)

        try:
            text = result.get("reply", "{}").replace("```json", "").replace("```", "").strip()
            parsed = json.loads(text)
            parsed["tokens"] = tokens_used
            return parsed
        except:
            return {"query": query, "category": category, "key_findings": "Could not analyze data.", "recommendations": [], "status": "error", "tokens": tokens_used}

insights_service = InsightsService()