import httpx
import json
import asyncio
from loguru import logger
from config import settings

class AIService:
    def __init__(self):
        self.groq_key = settings.GROQ_API_KEY
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"

    async def chat(self, messages: list, max_tokens: int = 1500, temperature: float = 0.3) -> dict:
        headers = {"Authorization": f"Bearer {self.groq_key}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": temperature, "max_tokens": max_tokens}

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(self.groq_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return {"success": True, "reply": data["choices"][0]["message"]["content"], "tokens": data.get("usage", {}).get("total_tokens", 0)}
            except Exception as e:
                if "429" in str(e):
                    logger.warning("Rate limited — retrying in 10s")
                    await asyncio.sleep(10)
                    try:
                        response = await client.post(self.groq_url, headers=headers, json=payload)
                        response.raise_for_status()
                        data = response.json()
                        return {"success": True, "reply": data["choices"][0]["message"]["content"], "tokens": data.get("usage", {}).get("total_tokens", 0)}
                    except:
                        pass
                logger.error(f"Groq error: {e}")
                return {"success": False, "error": str(e)}

ai_service = AIService()