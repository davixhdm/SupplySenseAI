import json
from services.ai_service import ai_service

class LandingService:
    async def chat(self, request: dict) -> dict:
        query = request.get("query", "")
        context = request.get("context", {})

        parts = [
            "You are SupplySense AI, a helpful assistant for the SupplySense inventory management platform.",
            "Answer the visitor's questions using ONLY the information provided below.",
            "Be friendly, professional, and encourage them to sign up for a free trial.",
            "Give detailed, informative responses that showcase the platform's value.",
            "",
            "--- SUPPLYSENSE INFORMATION (use this exact data) ---",
        ]

        if context.get("features"):
            if isinstance(context["features"], list):
                parts.append("\nFEATURES:")
                for f in context["features"]: parts.append(f"  • {f}")
            else: parts.append(f"\nFeatures: {context['features']}")

        if context.get("pricing"):
            parts.append(f"""
⚠️ EXACT PRICING — USE THESE NUMBERS ONLY:
{context['pricing']}
Repeat the exact numbers above when asked about pricing.""")
        if context.get("support"):
            s = context["support"]
            parts.append("\nSUPPORT:")
            if isinstance(s, dict):
                if s.get("email"): parts.append(f"  • Email: {s['email']}")
                if s.get("phone"): parts.append(f"  • Phone: {s['phone']}")
                if s.get("hours"): parts.append(f"  • Hours: {s['hours']}")
            else: parts.append(f"  {s}")
        if context.get("locations"): parts.append(f"\nLocations: {context['locations'] if isinstance(context['locations'], str) else ', '.join(context['locations'])}")
        if context.get("free_trial"): parts.append(f"\nFree Trial: {context['free_trial']}")

        parts.append(f"""
        
Visitor's question: "{query}"

Return ONLY valid JSON:
{{"reply": "your detailed, helpful response", "status": "success"}}
⚠️ Use ONLY exact information above. Do not invent details.""")

        prompt = "\n".join(parts)
        result = await ai_service.chat([{"role": "user", "content": prompt}], max_tokens=800, temperature=0.5)
        tokens_used = result.get("tokens", 0)
        try:
            text = result.get("reply", "{}").replace("```json", "").replace("```", "").strip()
            parsed = json.loads(text)
            parsed["tokens"] = tokens_used
            return parsed
        except:
            return {"reply": result.get("reply", "I couldn't process that."), "status": "success", "tokens": tokens_used}

landing_service = LandingService()