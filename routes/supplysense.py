from fastapi import APIRouter, HTTPException, Request
from services.insights_service import insights_service
from services.forecast_service import forecast_service
from services.anomaly_service import anomaly_service
from services.supplier_service import supplier_service
from services.churn_service import churn_service
from services.recommendations_service import recommendations_service
from services.landing_service import landing_service
from config import settings

router = APIRouter(tags=["SupplySense AI"])

_usage = {"requests": 0, "tokens": 0, "endpoints": {}}
_engine_running = True

def _track(endpoint: str, tokens: int = 0):
    _usage["requests"] += 1
    _usage["tokens"] += tokens
    _usage["endpoints"][endpoint] = _usage["endpoints"].get(endpoint, 0) + 1

# ================================================================================================
# PUBLIC ENDPOINTS (No auth)
# ================================================================================================

@router.get("/health")
async def health():
    return {"status": "healthy", "service": "SupplySense AI Engine", "version": "1.0.0", "engine": "running" if _engine_running else "stopped"}

@router.post("/insights")
async def insights(request: dict):
    if not _engine_running:
        raise HTTPException(503, "AI engine is stopped")
    result = await insights_service.analyze(request)
    _track("insights", result.get("tokens", 0))
    return result

@router.post("/forecast/stockout")
async def stockout(request: dict):
    if not _engine_running:
        raise HTTPException(503, "AI engine is stopped")
    result = await forecast_service.stockout(request)
    _track("stockout", result.get("tokens", 0))
    return result

@router.post("/forecast/demand")
async def demand(request: dict):
    if not _engine_running:
        raise HTTPException(503, "AI engine is stopped")
    result = await forecast_service.demand(request)
    _track("demand", result.get("tokens", 0))
    return result

@router.post("/anomaly/detect")
async def detect_anomalies(request: dict):
    if not _engine_running:
        raise HTTPException(503, "AI engine is stopped")
    result = await anomaly_service.detect(request)
    _track("anomaly", result.get("tokens", 0))
    return result

@router.post("/supplier/score")
async def supplier_score(request: dict):
    if not _engine_running:
        raise HTTPException(503, "AI engine is stopped")
    result = await supplier_service.score(request)
    _track("supplier", result.get("tokens", 0))
    return result

@router.post("/customer/churn")
async def customer_churn(request: dict):
    if not _engine_running:
        raise HTTPException(503, "AI engine is stopped")
    result = await churn_service.predict(request)
    _track("churn", result.get("tokens", 0))
    return result

@router.post("/recommendations")
async def recommendations(request: dict):
    if not _engine_running:
        raise HTTPException(503, "AI engine is stopped")
    result = await recommendations_service.generate(request)
    _track("recommendations", result.get("tokens", 0))
    return result

@router.post("/landing/chat")
async def landing_chat(request: dict):
    if not _engine_running:
        raise HTTPException(503, "AI engine is stopped")
    result = await landing_service.chat(request)
    _track("landing", result.get("tokens", 0))
    return result

# ================================================================================================
# ADMIN ENDPOINTS (Password-protected)
# ================================================================================================

def _verify_admin(password: str):
    if password != settings.ADMIN_PASSWORD:
        raise HTTPException(401, "Invalid admin password")

@router.get("/admin/usage")
async def admin_usage(password: str):
    _verify_admin(password)
    return {"usage": _usage, "engine_running": _engine_running}

@router.post("/admin/stop")
async def admin_stop(password: str):
    _verify_admin(password)
    global _engine_running
    _engine_running = False
    return {"status": "stopped", "message": "AI engine stopped."}

@router.post("/admin/start")
async def admin_start(password: str):
    _verify_admin(password)
    global _engine_running
    _engine_running = True
    return {"status": "started", "message": "AI engine started."}

@router.post("/admin/reset")
async def admin_reset(password: str):
    _verify_admin(password)
    global _usage
    _usage = {"requests": 0, "tokens": 0, "endpoints": {}}
    return {"status": "reset", "message": "Usage stats reset."}