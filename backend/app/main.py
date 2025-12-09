from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import uuid

from .config import settings
from .database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Marketing Intelligence Platform with Authenticity Verification",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to AdVision AI API",
        "docs": "/docs",
        "health": "/health"
    }


# Import and include routers
from .routers import (
    auth,
    campaigns,
    creatives,
    analytics,
    ml,
    documents,
    chat,
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
app.include_router(creatives.router, prefix="/creatives", tags=["Creatives"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(ml.router, prefix="/ml", tags=["Machine Learning"])
app.include_router(documents.router, prefix="/documents", tags=["Documents & RAG"])
app.include_router(chat.router, prefix="/chat", tags=["AI Chatbot"])
app.include_router(chatbot.router, prefix="/chatbot", tags=["AI Chatbot"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None),
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
