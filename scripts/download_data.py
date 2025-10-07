#!/usr/bin/env python3
"""
Script to download historical market data for all instruments in the watchlist
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime,timedelta
import pandas as pd

# Add parent directory to path
sys.path.insert(0,str(Path(__file__).parent.parent))

from app.core.config import config_manager
from app.data.providers.data_aggregator import DataAggregator


async def download_historical_data(
        symbols: list,
        days: int = 365,
        interval: str = "1d"
):
    """
    Download historical data for given symbols

    Args:
        symbols: List of ticker symbols
        days: Number of days of historical data
        interval: Data interval (1d, 1wk, 1mo)
    """
    data_aggregator = DataAggregator()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True,exist_ok=True)

    print(f"📥 Downloading historical data for {len(symbols)} symbols")
    print(f"📅 Period: {start_date.date()} to {end_date.date()}")
    print(f"⏱️  Interval: {interval}")
    print("-" * 60)

    success_count = 0
    failed_symbols = []

    for i,symbol in enumerate(symbols,1):
        try:
            print(f"[{i}/{len(symbols)}] Downloading {symbol}...",end=" ")

            df = await data_aggregator.get_historical(
                symbol,
                start_date,
                end_date,
                interval
            )

            if not df.empty:
                # Save to CSV
                filename = output_dir / f"{symbol}_{interval}_historical.csv"
                df.to_csv(filename)

                print(f"✅ Saved {len(df)} rows to {filename}")
                success_count += 1
            else:
                print(f"❌ No data received")
                failed_symbols.append(symbol)

        except Exception as e:
            print(f"❌ Error: {e}")
            failed_symbols.append(symbol)

        # Small delay to avoid rate limiting
        await asyncio.sleep(0.5)

    print("-" * 60)
    print(f"✅ Successfully downloaded: {success_count}/{len(symbols)}")

    if failed_symbols:
        print(f"❌ Failed symbols: {', '.join(failed_symbols)}")


async def download_recent_data(symbols: list,days: int = 30):
    """Download recent data for quick backtesting"""
    await download_historical_data(symbols,days=days,interval="1d")


async def main():
    """Main function"""
    print("=" * 60)
    print("Historical Data Downloader")
    print("=" * 60)

    # Get watchlist from config
    watchlist = config_manager.get_watchlist()

    print(f"\n📋 Watchlist loaded: {len(watchlist)} symbols")
    print(f"Symbols: {', '.join(watchlist[:10])}...")

    # Menu
    print("\nSelect option:")
    print("1. Download 1 year daily data (recommended)")
    print("2. Download 3 months daily data")
    print("3. Download 1 month daily data")
    print("4. Download 1 year weekly data")
    print("5. Download custom period")

    choice = input("\nEnter choice (1-5) [1]: ").strip() or "1"

    if choice == "1":
        await download_historical_data(watchlist,days=365,interval="1d")
    elif choice == "2":
        await download_historical_data(watchlist,days=90,interval="1d")
    elif choice == "3":
        await download_historical_data(watchlist,days=30,interval="1d")
    elif choice == "4":
        await download_historical_data(watchlist,days=365,interval="1wk")
    elif choice == "5":
        days = int(input("Enter number of days: "))
        interval = input("Enter interval (1d/1wk/1mo) [1d]: ").strip() or "1d"
        await download_historical_data(watchlist,days=days,interval=interval)
    else:
        print("Invalid choice!")
        return

    print("\n✅ Download complete!")
    print(f"📁 Data saved to: {Path('data/raw').absolute()}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Download interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()