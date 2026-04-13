from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from models.database import engine, Base
from api.reports import router as reports_router
from api.downloads import router as downloads_router
from api.streams import router as streams_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="Report Platform",
    description="Asynchronous report generation and management platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reports_router)
app.include_router(downloads_router)
app.include_router(streams_router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "message": "Report Platform API",
        "docs": "/docs",
        "health": "/api/health",
    }
