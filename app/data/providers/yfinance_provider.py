import yfinance as yf
import pandas as pd
from typing import List,Dict,Optional
from datetime import datetime,timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor
from .base import BaseDataProvider


class YFinanceProvider(BaseDataProvider):
    """Yahoo Finance data provider (free, no API key needed)"""

    def __init__(self):
        super().__init__(api_key=None)
        self.executor = ThreadPoolExecutor(max_workers=10)

    async def get_quote(self,symbol: str) -> Dict:
        """Get real-time quote from Yahoo Finance"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._get_quote_sync,
            symbol
        )

    def _get_quote_sync(self,symbol: str) -> Dict:
        """Synchronous quote fetch"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="2d")

            if hist.empty:
                return self._empty_quote(symbol)

            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change = current_price - prev_close
            change_percent = (change / prev_close * 100) if prev_close > 0 else 0

            return self.format_quote({
                'symbol': symbol,
                'price': float(current_price),
                'change': float(change),
                'change_percent': float(change_percent),
                'volume': int(hist['Volume'].iloc[-1]),
                'timestamp': hist.index[-1],
                'open': float(hist['Open'].iloc[-1]),
                'high': float(hist['High'].iloc[-1]),
                'low': float(hist['Low'].iloc[-1]),
                'close': float(current_price),
                'prev_close': float(prev_close),
                'bid': info.get('bid',current_price),
                'ask': info.get('ask',current_price),
            })
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return self._empty_quote(symbol)

    def _empty_quote(self,symbol: str) -> Dict:
        """Return empty quote structure"""
        return self.format_quote({
            'symbol': symbol,
            'price': 0.0,
            'change': 0.0,
            'change_percent': 0.0,
            'volume': 0,
            'timestamp': datetime.now(),
        })

    async def get_quotes(self,symbols: List[str]) -> List[Dict]:
        """Get quotes for multiple symbols concurrently"""
        tasks = [self.get_quote(symbol) for symbol in symbols]
        return await asyncio.gather(*tasks)

    async def get_historical(
            self,
            symbol: str,
            start_date: datetime,
            end_date: datetime,
            interval: str = "1d"
    ) -> pd.DataFrame:
        """Get historical data"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._get_historical_sync,
            symbol,
            start_date,
            end_date,
            interval
        )

    def _get_historical_sync(
            self,
            symbol: str,
            start_date: datetime,
            end_date: datetime,
            interval: str
    ) -> pd.DataFrame:
        """Synchronous historical data fetch"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval
            )

            # Standardize column names
            df.columns = [col.lower() for col in df.columns]
            return df
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()

    async def is_available(self) -> bool:
        """Check if Yahoo Finance is available"""
        try:
            quote = await self.get_quote("AAPL")
            return quote['price'] > 0
        except:
            return False