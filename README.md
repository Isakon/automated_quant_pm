# Automated Quantitative Trading & Portfolio Management System
## To be tested on OS Linux Ubuntu 22.04 LTS
## DO NOT USE IT YET ON YOUR LOCAL MACHINE

A professional-grade automated trading system built with FastAPI, PyTorch, and modern ML/DL techniques.

## Features

- Real-time market data aggregation from multiple sources
- ML/DL models for signal generation (PyTorch)
- Automated trading strategy execution
- Portfolio optimization and risk management
- RESTful API with FastAPI
- Real-time web dashboard
- Comprehensive backtesting engine

## Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure credentials:
```bash
cp credentials/.env.example credentials/.env
# Edit credentials/.env with your API keys
```

4. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Access dashboard:
```
http://localhost:8000
```

## Project Structure

See directory tree for detailed structure.

## License

MIT
