"""Main FastAPI application for demo website."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from demo_website.config import get_settings

settings = get_settings()
app = FastAPI(title="Demo Website", version="0.1.0")

# Get the static directory path
static_dir = Path(__file__).parent / "static"


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint for readiness probes."""
    return {"status": "healthy"}


@app.get("/config")
async def config() -> dict[str, str]:
    """Return API configuration for frontend."""
    return {"api_url": settings.api_url}


@app.get("/")
async def root() -> FileResponse:
    """Serve the main index.html page."""
    return FileResponse(static_dir / "index.html")


# Mount static files after all routes
app.mount("/static", StaticFiles(directory=static_dir), name="static")
