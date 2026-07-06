# backend/main.py
import logging
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.core.config import settings
from backend.database.connection import init_db
from backend.jobs.scheduler import start_scheduler

# Route imports
from backend.routes.users        import router as users_router
from backend.routes.chat         import router as chat_router
from backend.routes.history      import router as history_router
from backend.routes.emotions     import router as emotions_router
from backend.routes.memories     import router as memories_router
from backend.routes.goals        import router as goals_router
from backend.routes.weekly       import router as weekly_router
from backend.routes.mirror_me    import router as mirror_me_router
from backend.routes.voice_profile import router as voice_profile_router

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="InnerVoice API", version="4.0.0")

# ── CORS ──────────────────────────────────────────────────────────────────────
raw_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=raw_origins,
    allow_origin_regex=r"https?://localhost(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global exception handlers ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "data": None, "error": str(exc)}
    )

# ── Health & status routes ────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "healthy", "version": "4.0.0"}

@app.get("/api/status")
async def get_status():
    has_key = bool(settings.GROQ_API_KEY) and settings.GROQ_API_KEY != "your_groq_api_key_here"
    return {
        "success": True,
        "data": {
            "app_env":                  settings.APP_ENV,
            "version":                  "4.0.0",
            "database":                 "sqlite (aiosqlite)",
            "groq_api_key_configured":  has_key,
            "message": "InnerVoice API is running." if has_key
                       else "WARNING: GROQ_API_KEY is not configured."
        },
        "error": None
    }

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(users_router)
app.include_router(chat_router)
app.include_router(history_router)
app.include_router(emotions_router)
app.include_router(memories_router)
app.include_router(goals_router)
app.include_router(weekly_router)
app.include_router(mirror_me_router)
app.include_router(voice_profile_router)

# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
        print("\n" + "="*80)
        print("CRITICAL CONFIGURATION ERROR: GROQ_API_KEY is missing!")
        print("  1. Get a free key at: https://console.groq.com/keys")
        print("  2. Open 'backend/.env' and set GROQ_API_KEY=<your_key>")
        print("="*80 + "\n")
        logger.error("GROQ_API_KEY is missing. AI responses will be empty.")
    else:
        logger.info("GROQ_API_KEY is configured.")

    try:
        await init_db()
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize SQLite database: {e}")

    try:
        start_scheduler()
    except Exception as e:
        logger.error(f"Failed to start APScheduler: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.BACKEND_PORT, reload=True)
