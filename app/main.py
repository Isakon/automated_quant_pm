from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import config_manager
from app.api.routes import market_data
from app.data.providers.data_aggregator import DataAggregator

# Global data aggregator instance
data_aggregator = DataAggregator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Starting Automated Quant PM System...")
    print(f"📊 Loaded {len(config_manager.get_watchlist())} instruments")

    # Check provider availability
    provider_status = await data_aggregator.check_providers()
    print("📡 Data Provider Status:")
    for provider,status in provider_status.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {provider}")

    yield

    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=config_manager.settings.app_name,
    version=config_manager.settings.app_version,
    description="Automated Trading and Portfolio Management System",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static",StaticFiles(directory="static"),name="static")
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(market_data.router,prefix="/api/v1",tags=["Market Data"])

# Make data_aggregator available to routes
app.state.data_aggregator = data_aggregator
app.state.templates = templates
app.state.config_manager = config_manager


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": config_manager.settings.app_name,
        "version": config_manager.settings.app_version,
        "status": "running",
        "endpoints": {
            "dashboard": "/dashboard",
            "api_docs": "/docs",
            "market_data": "/api/v1/quotes"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    provider_status = await data_aggregator.check_providers()
    return {
        "status": "healthy",
        "providers": provider_status
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config_manager.settings.host,
        port=config_manager.settings.port,
        reload=config_manager.settings.debug,
        log_level=config_manager.settings.log_level.lower()
    )