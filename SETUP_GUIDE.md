# Complete Setup Guide - Automated Quant PM

This guide will walk you through setting up your automated trading and portfolio management system from scratch.

## Prerequisites

- Linux/Unix-based system (Ubuntu 20.04+ recommended)
- Python 3.9 or higher
- pip (Python package manager)
- Git
- 4GB RAM minimum
- Internet connection for market data

## Step-by-Step Installation

### 1. Create Project Directory Structure

Save the `setup_project.sh` script and run it:

```bash
# Make the script executable
chmod +x setup_project.sh

# Run the setup script
./setup_project.sh

# Navigate to the project directory
cd automated_quant_pm
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# This will install:
# - FastAPI and web server components
# - Market data providers (yfinance, alpha-vantage)
# - PyTorch for ML models
# - Data processing libraries (pandas, numpy)
# - And many more...
```

### 4. Configure API Keys

```bash
# Copy the example environment file
cp credentials/.env.example credentials/.env

# Edit the file with your API keys
nano credentials/.env
```

Add your API keys (optional for yfinance, required for others):

```bash
# Alpha Vantage (free tier: 25 calls/day)
# Get your key at: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY=your_key_here

# Other providers (optional)
TWELVE_DATA_API_KEY=your_key_here
POLYGON_API_KEY=your_key_here
```

**Note**: yfinance works without API keys!

### 5. Verify Installation

```bash
# Check Python version
python --version  # Should be 3.9+

# Check installed packages
pip list | grep -E "fastapi|yfinance|torch"

# Test import
python -c "import fastapi, yfinance, torch; print('✅ All imports successful!')"
```

### 6. Start the Server

```bash
# Make the run script executable
chmod +x scripts/run_server.sh

# Start the development server
./scripts/run_server.sh
```

Or manually:

```bash
# Activate venv if not already active
source venv/bin/activate

# Run with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Access the Dashboard

Open your browser and navigate to:

```
http://localhost:8000/dashboard
```

You should see the real-time market dashboard with 20 popular financial instruments!

### 8. API Documentation

FastAPI provides automatic API documentation:

```
http://localhost:8000/docs          # Swagger UI
http://localhost:8000/redoc         # ReDoc
```

## Available API Endpoints

### Market Data

```bash
# Get quotes for all watchlist instruments
curl http://localhost:8000/api/v1/quotes

# Get quote for specific symbol
curl http://localhost:8000/api/v1/quote/AAPL

# Get quotes for multiple symbols
curl "http://localhost:8000/api/v1/quotes?symbols=AAPL,MSFT,GOOGL"

# Get historical data
curl "http://localhost:8000/api/v1/historical/AAPL?days=30&interval=1d"

# Check provider status
curl http://localhost:8000/api/v1/providers

# Get all configured instruments
curl http://localhost:8000/api/v1/instruments
```

### System

```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/
```

## Download Historical Data

To download historical data for backtesting and training:

```bash
# Make the download script executable
chmod +x scripts/download_data.py

# Run the download script
python scripts/download_data.py
```

This will:
1. Download historical data for all watchlist instruments
2. Save to `data/raw/` directory
3. Support multiple intervals (daily, weekly, monthly)

## Testing the System

### 1. Test Market Data Fetching

```python
# Create a test script: test_data.py
import asyncio
from app.data.providers.data_aggregator import DataAggregator

async def test():
    agg = DataAggregator()
    quote = await agg.get_quote("AAPL")
    print(f"AAPL Price: ${quote['price']}")

asyncio.run(test())
```

### 2. Test API Endpoints

```bash
# Install httpie for easier API testing
pip install httpie

# Test quotes endpoint
http GET http://localhost:8000/api/v1/quotes

# Test specific symbol
http GET http://localhost:8000/api/v1/quote/TSLA
```

## Project Structure Overview

```
automated_quant_pm/
├── app/                    # Main application code
│   ├── api/               # API routes
│   ├── core/              # Configuration and core utilities
│   ├── data/              # Data providers and processing
│   ├── models/            # PyTorch ML models
│   ├── trading/           # Trading strategies and execution
│   └── portfolio/         # Portfolio management
├── config/                # Configuration files
├── credentials/           # API keys and secrets
├── data/                  # Data storage
│   ├── raw/              # Raw market data
│   ├── processed/        # Processed features
│   └── models/           # Trained model checkpoints
├── scripts/              # Utility scripts
├── templates/            # HTML templates
└── tests/                # Test files
```

## Common Issues and Solutions

### Issue: "Module not found" errors

```bash
# Solution: Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Issue: yfinance not working

```bash
# Solution: Update yfinance
pip install yfinance --upgrade
```

### Issue: Port 8000 already in use

```bash
# Solution: Use different port
uvicorn app.main:app --reload --port 8001

# Or kill the process using port 8000
sudo lsof -ti:8000 | xargs kill -9
```

### Issue: Permission denied on scripts

```bash
# Solution: Make scripts executable
chmod +x scripts/*.sh scripts/*.py
```

## Next Steps

1. **Configure Watchlist**: Edit `config/instruments.yaml` to customize your instrument list

2. **Add More Data Providers**: Edit `app/data/providers/` to add more providers

3. **Develop ML Models**: Create PyTorch models in `app/models/pytorch/`

4. **Implement Trading Strategies**: Add strategies in `app/trading/signals/`

5. **Set Up Backtesting**: Implement backtesting in `app/trading/backtesting/`

6. **Deploy to Production**: Use gunicorn for production deployment

## Production Deployment

For production deployment with gunicorn:

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn app.main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log
```

## Support and Documentation

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **yfinance**: https://github.com/ranaroussi/yfinance
- **Alpha Vantage**: https://www.alphavantage.co/documentation
- **PyTorch**: https://pytorch.org/docs

## License

< License > - See LICENSE file for details

---

**Happy Trading! 📈🚀**