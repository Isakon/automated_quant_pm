from abc import ABC,abstractmethod
from typing import Optional,List,Dict
import pandas as pd
from datetime import datetime


class BaseDataProvider(ABC):
    """Abstract base class for market data providers"""

    def __init__(self,api_key: Optional[str] = None):
        self.api_key = api_key
        self.name = self.__class__.__name__

    @abstractmethod
    async def get_quote(self,symbol: str) -> Dict:
        """
        Get real-time quote for a symbol

        Returns:
            Dict with keys: symbol, price, change, change_percent, volume,
                           timestamp, bid, ask, open, high, low, close
        """
        pass

    @abstractmethod
    async def get_quotes(self,symbols: List[str]) -> List[Dict]:
        """Get real-time quotes for multiple symbols"""
        pass

    @abstractmethod
    async def get_historical(
            self,
            symbol: str,
            start_date: datetime,
            end_date: datetime,
            interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Get historical data for a symbol

        Args:
            symbol: Ticker symbol
            start_date: Start date
            end_date: End date
            interval: Data interval (1m, 5m, 15m, 1h, 1d, 1wk, 1mo)

        Returns:
            DataFrame with OHLCV data
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the provider is available and working"""
        pass

    def format_quote(self,data: Dict) -> Dict:
        """Standardize quote format across providers"""
        return {
            'symbol': data.get('symbol'),
            'price': data.get('price',0.0),
            'change': data.get('change',0.0),
            'change_percent': data.get('change_percent',0.0),
            'volume': data.get('volume',0),
            'timestamp': data.get('timestamp',datetime.now()),
            'bid': data.get('bid',0.0),
            'ask': data.get('ask',0.0),
            'open': data.get('open',0.0),
            'high': data.get('high',0.0),
            'low': data.get('low',0.0),
            'close': data.get('close',0.0),
            'prev_close': data.get('prev_close',0.0),
        }