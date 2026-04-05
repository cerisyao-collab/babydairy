"""Baby Diary API Application Entry Point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from src.config import settings
from src.api import auth, records, summary, config, ai
from src.api.errors import (
    APIError,
    api_error_handler,
    validation_error_handler,
    generic_error_handler,
)

# Create FastAPI application
app = FastAPI(
    title="Baby Diary API",
    description="Backend API for WeChat mini-program baby diary application",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Register exception handlers
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# Configure CORS for WeChat mini-program
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # WeChat mini-program origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(records.router, prefix="/api/records", tags=["记录管理"])
app.include_router(summary.router, prefix="/api/summary", tags=["每日总结"])
app.include_router(config.router, prefix="/api/config", tags=["配置管理"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI分析"])


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {"message": "Baby Diary API is running", "version": "1.0.0"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}