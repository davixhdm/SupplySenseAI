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
- ONLY analyze the data categories provided. Do NOT mention categories not in the data.
- Use actual numbers from the data provided
- Be specific and detailed — explain WHY each finding matters to the business
- HIGH priority = urgent action needed now, MEDIUM = this week, LOW = this month
- Give 4-6 key findings with business context (or fewer if limited data)
- Give 3-5 specific, actionable recommendations
- Include all relevant metrics with values
- Write like a human business analyst, not a robot
- Mention specific product names, customer names, and numbers when available"""


class InsightsService:
    
    def _filter_data(self, category: str, data: dict) -> dict:
        """Only include relevant data based on category."""
        # General/revenue/overview queries get everything
        if category in ["general", "revenue", "overview", "summary", "all", "business", "performance", "dashboard"]:
            return data
        
        # Map categories to relevant data keys
        category_map = {
            "products": ["products"],
            "inventory": ["products"],
            "stock": ["products"],
            "suppliers": ["suppliers"],
            "customers": ["customers"],
            "orders": ["orders", "transactions"],
            "sales": ["transactions", "orders"],
            "employees": ["employees"],
            "transactions": ["transactions"],
            "anomalies": ["transactions"],
            "churn": ["customers"],
        }
        
        keys = category_map.get(category, list(data.keys()))
        filtered = {}
        for k in keys:
            if k in data:
                filtered[k] = data[k]
        return filtered if filtered else data
    
    async def analyze(self, request: dict) -> dict:
        query = request.get("query", "")
        category = request.get("category", "general")
        data = request.get("data", {})
        
        # Filter data based on what the user asked
        filtered_data = self._filter_data(category, data)

        parts = ["--- REAL BUSINESS DATA ---"]
        data_categories_used = []

        # Products
        if "products" in filtered_data:
            parts.append(f"\nPRODUCTS ({len(filtered_data['products'])}):")
            data_categories_used.append("products")
            for p in filtered_data["products"][:15]:
                stock = p.get("stockLevel", 0)
                reorder = p.get("reorderThreshold", 10)
                status = "⚠️ LOW" if stock <= reorder else "OK"
                parts.append(f"  • {p.get('name','?')}: Stock {stock} (reorder at {reorder}) — {status}, Price {p.get('sellingPrice',0)}, Cost {p.get('unitCost',0)}")

        # Suppliers
        if "suppliers" in filtered_data:
            parts.append(f"\nSUPPLIERS ({len(filtered_data['suppliers'])}):")
            data_categories_used.append("suppliers")
            for s in filtered_data["suppliers"][:10]:
                parts.append(f"  • {s.get('name','?')}: Reliability {s.get('reliabilityScore',0)}%, On-time {s.get('onTimeDeliveries',0)}/{s.get('totalOrders',0)}")

        # Customers
        if "customers" in filtered_data:
            parts.append(f"\nCUSTOMERS ({len(filtered_data['customers'])}):")
            data_categories_used.append("customers")
            for c in filtered_data["customers"][:10]:
                parts.append(f"  • {c.get('fullName','?')}: Spent {c.get('totalSpent',0)}, {c.get('purchaseCount',0)} purchases, Churn risk {c.get('churnRisk',0)}%, Last purchase {c.get('lastPurchaseDate','?')}")

        # Orders
        if "orders" in filtered_data:
            parts.append(f"\nORDERS ({len(filtered_data['orders'])}):")
            data_categories_used.append("orders")
            for o in filtered_data["orders"][:10]:
                delayed = " ⚠️ DELAYED" if o.get("isDelayed") else ""
                parts.append(f"  • {o.get('orderNumber','?')}: {o.get('totalAmount',0)} — {o.get('status','?')}{delayed}")

        # Transactions
        if "transactions" in filtered_data:
            total_amount = sum(t.get("amount", 0) for t in filtered_data["transactions"])
            sale_count = len([t for t in filtered_data["transactions"] if t.get("type") == "sale"])
            parts.append(f"\nTRANSACTIONS ({len(filtered_data['transactions'])}): Total {total_amount}, {sale_count} sales")
            data_categories_used.append("transactions")
            for t in filtered_data["transactions"][:10]:
                anomaly = " ⚠️ ANOMALY" if t.get("isAnomaly") else ""
                parts.append(f"  • {t.get('type','?')}: {t.get('amount',0)} on {t.get('transactionDate','?')}{anomaly}")

        # Employees
        if "employees" in filtered_data:
            parts.append(f"\nEMPLOYEES ({len(filtered_data['employees'])}):")
            data_categories_used.append("employees")
            for e in filtered_data["employees"][:10]:
                parts.append(f"  • {e.get('fullName','?')}: {e.get('department','?')}, Performance {e.get('performanceScore',0)}%, Efficiency {e.get('efficiency',0)}%")

        parts.append(f"""
        
User asked: "{query}"
Category: {category}
Data categories provided: {', '.join(data_categories_used) if data_categories_used else 'none'}

{SYSTEM_PROMPT}

⚠️ IMPORTANT: Only analyze the data categories listed above ({', '.join(data_categories_used) if data_categories_used else 'none'}). Do NOT mention products if products data wasn't provided. Do NOT mention employees if employee data wasn't provided. Stay focused on what was asked.""")

        prompt = "\n".join(parts)
        result = await ai_service.chat([{"role": "user", "content": prompt}], max_tokens=2000, temperature=0.3)
        tokens_used = result.get("tokens", 0)

        try:
            text = result.get("reply", "{}").replace("```json", "").replace("```", "").strip()
            parsed = json.loads(text)
            parsed["tokens"] = tokens_used
            return parsed
        except:
            return {
                "query": query, "category": category,
                "key_findings": ["Could not analyze the data. Please try again."],
                "recommendations": [],
                "summary": "Analysis failed.",
                "metrics": {},
                "status": "error", "tokens": tokens_used
            }

insights_service = InsightsService()