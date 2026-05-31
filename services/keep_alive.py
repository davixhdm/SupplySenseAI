import httpx
import asyncio
import os
from loguru import logger

SELF_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")
PING_INTERVAL = 540  # 9 minutes

async def keep_alive():
    logger.info(f"Keep-alive starting: will ping {SELF_URL}/api/health every {PING_INTERVAL}s")
    await asyncio.sleep(60)
    while True:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"{SELF_URL}/api/health")
                if response.status_code == 200:
                    logger.info("Keep-alive: OK")
                else:
                    logger.warning(f"Keep-alive: HTTP {response.status_code}")
        except Exception as e:
            logger.warning(f"Keep-alive ping failed: {e}")
        await asyncio.sleep(PING_INTERVAL)

if __name__ == "__main__":
    asyncio.run(keep_alive())