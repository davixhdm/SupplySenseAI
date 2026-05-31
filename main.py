import sys
import os
import asyncio as _asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from config import settings

logger.remove()
logger.add(sys.stdout, level=settings.LOG_LEVEL)

os.makedirs("static", exist_ok=True)

VALID_PASSWORDS = [settings.ADMIN_PASSWORD, settings.ADMIN_PASSWORD2]

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"╔══════════════════════════════════════════════╗")
    logger.info(f"║  {settings.APP_NAME} v{settings.API_VERSION}                  ║")
    logger.info(f"║  Environment: {settings.ENVIRONMENT.ljust(31)}║")
    logger.info(f"║  Port: {str(settings.PORT).ljust(36)}║")
    logger.info(f"╚══════════════════════════════════════════════╝")
    if settings.GROQ_API_KEY:
        logger.info("Groq: CONFIGURED")
    else:
        logger.warning("Groq: MISSING — AI disabled")

    # Keep-alive for Render free tier
    if settings.ENVIRONMENT == "production":
        try:
            from services.keep_alive import keep_alive as _keep_alive_loop
            _asyncio.create_task(_keep_alive_loop())
            logger.info("Keep-alive: ENABLED (self-ping every 9 minutes)")
        except Exception as e:
            logger.warning(f"Keep-alive: FAILED — {e}")

    yield
    logger.info(f"{settings.APP_NAME} shut down")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.exception_handler(Exception)
async def global_handler(request: Request, exc: Exception):
    logger.error(f"Error: {exc}")
    return JSONResponse(status_code=500, content={"status": "error", "error": str(exc) if settings.DEBUG else "Internal error"})

@app.get("/favicon.ico")
async def favicon():
    if os.path.exists("static/favicon.svg"):
        return FileResponse("static/favicon.svg", media_type="image/svg+xml")
    raise HTTPException(404)

@app.get("/favicon.svg")
async def favicon_svg():
    if os.path.exists("static/favicon.svg"):
        return FileResponse("static/favicon.svg", media_type="image/svg+xml")
    raise HTTPException(404)

from routes.supplysense import router
app.include_router(router, prefix="/api")

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(password: str = Query(None)):
    if password not in VALID_PASSWORDS:
        return HTMLResponse("""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>SupplySense AI — Admin Login</title>
<link rel="icon" type="image/svg+xml" href="/static/favicon.svg">
<style>
*{margin:0;padding:0;box-sizing:border-box}body{background:#0f172a;color:#f8fafc;display:flex;align-items:center;justify-content:center;height:100vh;font-family:'Segoe UI',sans-serif}
.card{background:#1e293b;border:1px solid #334155;border-radius:16px;padding:40px;text-align:center;width:380px}
.logo{width:48px;height:48px;background:#16a34a;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:18px;color:#fff;margin:0 auto 16px}
h2{font-size:22px;margin-bottom:4px}.sub{color:#64748b;font-size:14px;margin-bottom:24px}
input{width:100%;padding:12px;border-radius:10px;border:1px solid #334155;background:#0f172a;color:#f8fafc;font-size:15px;margin-bottom:16px;text-align:center}
button{width:100%;padding:12px;border-radius:10px;border:none;background:#16a34a;color:#fff;font-size:15px;font-weight:600;cursor:pointer}
button:hover{background:#15803d}.error{color:#ef4444;font-size:13px;margin-top:8px}
</style></head>
<body><form method="GET" class="card">
<div class="logo">SS</div>
<h2>SupplySense AI</h2><p class="sub">Admin Control Panel</p>
<input type="password" name="password" placeholder="Enter admin password" autofocus>
<button type="submit">Access Admin</button>
<p class="error" id="error"></p>
</form>
<script>
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('password') && urlParams.get('password') !== '') {
    document.getElementById('error').textContent = 'Invalid password';
}
</script>
</body></html>""")
    
    if os.path.exists("static/admin.html"):
        with open("static/admin.html", "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse("<h1>Admin panel not found</h1>", status_code=404)

@app.get("/")
async def root():
    return {"name": settings.APP_NAME, "version": settings.API_VERSION, "status": "running", "docs": "/docs", "admin": "/admin", "health": "/api/health"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)