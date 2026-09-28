import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.app.config import settings
from backend.app.database import engine, Base
from backend.app.routers import (
    auth, dashboard, lessons, homework, leaderboard, attendance, flashcards, badges
)

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Shamix Prep SAT API",
    description="Full-stack production API and static server for Shamix Prep SAT Platform.",
    version="2.0.0"
)

# Configure CORS (No wildcard fallback; if ALLOWED_ORIGINS is empty, allow no cross-origin requests)
origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api prefix
api_prefix = "/api"
app.include_router(auth.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(lessons.router, prefix=api_prefix)
app.include_router(homework.router, prefix=api_prefix)
app.include_router(leaderboard.router, prefix=api_prefix)
app.include_router(attendance.router, prefix=api_prefix)
app.include_router(flashcards.router, prefix=api_prefix)
app.include_router(badges.router, prefix=api_prefix)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))

@app.get("/", include_in_schema=False)
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Shamix Prep SAT Backend Running"}

# Mount StaticFiles ONLY on dedicated frontend directory
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
