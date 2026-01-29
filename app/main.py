from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from .database import engine, Base
from .routers import auth, dashboard, redirect
from pathlib import Path

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Simple URL Shortener")

# Mount static files
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Include Routers
app.include_router(auth.router)
app.include_router(dashboard.router)

# Redirect root to dashboard (which will redirect to login if not auth)
@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard")

# Catch-all redirect router must be last
app.include_router(redirect.router)
