from fastapi import APIRouter,Request,Query
from fastapi.responses import HTMLResponse
from typing import List,Optional
from datetime import datetime,timedelta

router = APIRouter()


@router.get("/dashboard",response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render the main dashboard"""
    templates = request.app.state.templates
    config_manager = request.app.state.config_manager

    watchlist = config_manager.get_watchlist()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "title": "Market Dashboard",
            "watchlist": watchlist,
            "app_name": config_manager.settings.app_name
        }
    )


@router.get("/quotes")
async def get_quotes(
        request: Request,
        symbols: Optional[str] = Query(None,description="Comma-separated list of symbols")
):
    """
    Get real-time quotes for symbols
    If no symbols provided, returns quotes for default watchlist
    """
    data_aggregator = request.app.state.data_aggregator
    config_manager = request.app.state.config_manager

    if symbols:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
    else:
        symbol_list = config_manager.get_watchlist()

    quotes = await data_aggregator.get_quotes(symbol_list)

    return {
        "timestamp": datetime.now().isoformat(),
        "count": len(quotes),
        "quotes": quotes
    }


@router.get("/quote/{symbol}")
async def get_quote(request: Request,symbol: str):
    """Get quote for a single symbol"""
    data_aggregator = request.app.state.data_aggregator

    quote = await data_aggregator.get_quote(symbol.upper())

    return {
        "timestamp": datetime.now().isoformat(),
        "quote": quote
    }


@router.get("/historical/{symbol}")
async def get_historical(
        request: Request,
        symbol: str,
        days: int = Query(30,ge=1,le=365,description="Number of days of historical data"),
        interval: str = Query("1d",description="Data interval (1d, 1wk, 1mo)")
):
    """Get historical data for a symbol"""
    data_aggregator = request.app.state.data_aggregator

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    df = await data_aggregator.get_historical(
        symbol.upper(),
        start_date,
        end_date,
        interval
    )

    if df.empty:
        return {
            "symbol": symbol,
            "data": [],
            "message": "No data available"
        }

    # Convert DataFrame to dict
    data = df.reset_index().to_dict(orient='records')

    return {
        "symbol": symbol,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "interval": interval,
        "count": len(data),
        "data": data
    }


@router.get("/instruments")
async def get_instruments(request: Request):
    """Get all configured instruments"""
    config_manager = request.app.state.config_manager

    return {
        "instruments": config_manager.get_all_instruments(),
        "watchlist": config_manager.get_watchlist()
    }


@router.get("/providers")
async def check_providers(request: Request):
    """Check status of all data providers"""
    data_aggregator = request.app.state.data_aggregator

    provider_status = await data_aggregator.check_providers()

    return {
        "timestamp": datetime.now().isoformat(),
        "providers": provider_status
    }