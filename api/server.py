import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agent"))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from database import get_latest_filings, get_filings_by_swf, get_swf_summary

app = FastAPI(
    title="Gulf SWF Filing Intelligence API",
    description="Real-time SC 13D/13G filing intelligence for Gulf Sovereign Wealth Funds",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Gulf SWF Filing Intelligence API"}


@app.get("/api/filings")
def get_filings(limit: int = 20):
    """Return latest filings sorted by date descending."""
    try:
        return get_latest_filings(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/filings/{swf}")
def get_swf_filings(swf: str, limit: int = 10):
    """Return filings for a specific SWF (e.g. ADIA, PIF, QIA, Mubadala, ADQ)."""
    try:
        # Accept both short key and full name
        from swf_config import SWF_CONFIG
        name = SWF_CONFIG.get(swf, {}).get("name", swf)
        return get_filings_by_swf(name, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/summary")
def summary():
    """Return per-SWF filing counts and latest dates."""
    try:
        return get_swf_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/trigger")
async def trigger(background_tasks: BackgroundTasks):
    """Manually trigger one full monitoring cycle in the background."""
    try:
        from main import run_agent
        background_tasks.add_task(asyncio.run, run_agent())
        return {"status": "triggered", "message": "Monitoring cycle started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
