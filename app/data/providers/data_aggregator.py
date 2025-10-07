from typing import List,Dict,Optional
import pandas as pd
from datetime import datetime
from .yfinance_provider import YFinanceProvider
from .alpha_vantage_provider import AlphaVantageProvider
from app.core.config import config_manager


class DataAggregator:
    """
    Aggregates data from multiple providers with fallback mechanism
    Priority: YFinance (primary, free) -> Alpha Vantage (backup)
    """

    def __init__(self):
        self.providers = []
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize available data providers based on configuration"""
        # Always add YFinance (no API key needed)
        self.providers.append(YFinanceProvider())

        # Add Alpha Vantage if API key is available
        if config_manager.settings.alpha_vantage_api_key:
            self.providers.append(
                AlphaVantageProvider(config_manager.settings.alpha_vantage_api_key)
            )

        print(f"Initialized {len(self.providers)} data providers")

    async def get_quote(self,symbol: str) -> Dict:
        """
        Get quote with fallback mechanism
        Tries providers in order until successful
        """
        for provider in self.providers:
            try:
                quote = await provider.get_quote(symbol)
                if quote and quote.get('price',0) > 0:
                    quote['provider'] = provider.name
                    return quote
            except Exception as e:
                print(f"Provider {provider.name} failed for {symbol}: {e}")
                continue

        # If all providers fail, return empty quote
        return self._empty_quote(symbol)

    async def get_quotes(self,symbols: List[str]) -> List[Dict]:
        """Get quotes for multiple symbols"""
        quotes = []
        for symbol in symbols:
            quote = await self.get_quote(symbol)
            quotes.append(quote)
        return quotes

    async def get_historical(
            self,
            symbol: str,
            start_date: datetime,
            end_date: datetime,
            interval: str = "1d"
    ) -> pd.DataFrame:
        """Get historical data with fallback"""
        for provider in self.providers:
            try:
                df = await provider.get_historical(
                    symbol,start_date,end_date,interval
                )
                if not df.empty:
                    return df
            except Exception as e:
                print(f"Provider {provider.name} failed for historical {symbol}: {e}")
                continue

        return pd.DataFrame()

    def _empty_quote(self,symbol: str) -> Dict:
        """Return empty quote structure"""
        return {
            'symbol': symbol,
            'price': 0.0,
            'change': 0.0,
            'change_percent': 0.0,
            'volume': 0,
            'timestamp': datetime.now(),
            'bid': 0.0,
            'ask': 0.0,
            'open': 0.0,
            'high': 0.0,
            'low': 0.0,
            'close': 0.0,
            'prev_close': 0.0,
            'provider': 'none',
        }

    async def check_providers(self) -> Dict[str,bool]:
        """Check availability of all providers"""
        status = {}
        for provider in self.providers:
            is_available = await provider.is_available()
            status[provider.name] = is_available
        return status