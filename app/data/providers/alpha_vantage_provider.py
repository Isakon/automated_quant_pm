from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.cryptocurrencies import CryptoCurrencies
import pandas as pd
from typing import List,Dict,Optional
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
from .base import BaseDataProvider


class AlphaVantageProvider(BaseDataProvider):
    """Alpha Vantage data provider (requires API key, 25 calls/day free tier)"""

    def __init__(self,api_key: str):
        super().__init__(api_key)
        self.ts = TimeSeries(key=api_key,output_format='pandas')
        self.crypto = CryptoCurrencies(key=api_key,output_format='pandas')
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.call_count = 0
        self.max_calls = 25  # Free tier limit

    async def get_quote(self,symbol: str) -> Dict:
        """Get real-time quote from Alpha Vantage"""
        if self.call_count >= self.max_calls:
            print(f"Alpha Vantage API call limit reached ({self.max_calls})")
            return self._empty_quote(symbol)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._get_quote_sync,
            symbol
        )

    def _get_quote_sync(self,symbol: str) -> Dict:
        """Synchronous quote fetch"""
        try:
            self.call_count += 1

            # Check if it's a crypto symbol
            if '-' in symbol and 'USD' in symbol:
                return self._get_crypto_quote(symbol)

            # Get quote for stocks
            data,meta = self.ts.get_quote_endpoint(symbol=symbol)

            price = float(data['05. price'][0])
            change = float(data['09. change'][0])
            change_percent = float(data['10. change percent'][0].rstrip('%'))
            volume = int(data['06. volume'][0])

            return self.format_quote({
                'symbol': symbol,
                'price': price,
                'change': change,
                'change_percent': change_percent,
                'volume': volume,
                'timestamp': datetime.strptime(data['07. latest trading day'][0],'%Y-%m-%d'),
                'open': float(data['02. open'][0]),
                'high': float(data['03. high'][0]),
                'low': float(data['04. low'][0]),
                'close': price,
                'prev_close': float(data['08. previous close'][0]),
            })
        except Exception as e:
            print(f"Error fetching Alpha Vantage quote for {symbol}: {e}")
            return self._empty_quote(symbol)

    def _get_crypto_quote(self,symbol: str) -> Dict:
        """Get cryptocurrency quote"""
        try:
            # Parse crypto symbol (e.g., BTC-USD -> BTC, USD)
            crypto_symbol = symbol.split('-')[0]
            market = 'USD'

            data,meta = self.crypto.get_digital_currency_daily(
                symbol=crypto_symbol,
                market=market
            )

            latest = data.iloc[0]
            prev = data.iloc[1] if len(data) > 1 else latest

            price = float(latest[f'4a. close ({market})'])
            prev_price = float(prev[f'4a. close ({market})'])
            change = price - prev_price
            change_percent = (change / prev_price * 100) if prev_price > 0 else 0

            return self.format_quote({
                'symbol': symbol,
                'price': price,
                'change': change,
                'change_percent': change_percent,
                'volume': float(latest['5. volume']),
                'timestamp': data.index[0],
                'open': float(latest[f'1a. open ({market})']),
                'high': float(latest[f'2a. high ({market})']),
                'low': float(latest[f'3a. low ({market})']),
                'close': price,
                'prev_close': prev_price,
            })
        except Exception as e:
            print(f"Error fetching crypto quote for {symbol}: {e}")
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
        """Get quotes for multiple symbols"""
        quotes = []
        for symbol in symbols:
            if self.call_count >= self.max_calls:
                quotes.append(self._empty_quote(symbol))
            else:
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
        """Get historical data"""
        if self.call_count >= self.max_calls:
            print(f"Alpha Vantage API call limit reached")
            return pd.DataFrame()

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._get_historical_sync,
            symbol,
            interval
        )

    def _get_historical_sync(self,symbol: str,interval: str) -> pd.DataFrame:
        """Synchronous historical data fetch"""
        try:
            self.call_count += 1

            if interval == "1d":
                data,meta = self.ts.get_daily(symbol=symbol,outputsize='full')
            elif interval == "1wk":
                data,meta = self.ts.get_weekly(symbol=symbol)
            elif interval == "1mo":
                data,meta = self.ts.get_monthly(symbol=symbol)
            else:
                # For intraday data
                data,meta = self.ts.get_intraday(
                    symbol=symbol,
                    interval=interval,
                    outputsize='full'
                )

            # Rename columns to standard format
            data.columns = ['open','high','low','close','volume']
            return data
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()

    async def is_available(self) -> bool:
        """Check if Alpha Vantage is available"""
        try:
            if self.call_count >= self.max_calls:
                return False
            quote = await self.get_quote("AAPL")
            return quote['price'] > 0
        except:
            return False

    def reset_call_count(self):
        """Reset daily call counter"""
        self.call_count = 0