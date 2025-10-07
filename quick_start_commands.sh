#!/bin/bash

# QUICK START SCRIPT - Automated Quant PM
# Run this script to set up and start the entire system

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Automated Quant PM - Quick Start Installation            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}📋 Checking prerequisites...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed!${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Step 1: Create project structure
echo ""
echo -e "${BLUE}📁 Step 1: Creating project structure...${NC}"
./setup_project.sh

# Navigate to project directory
cd automated_quant_pm

# Step 2: Create virtual environment
echo ""
echo -e "${BLUE}🔧 Step 2: Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment created and activated${NC}"

# Step 3: Upgrade pip
echo ""
echo -e "${BLUE}⬆️  Step 3: Upgrading pip...${NC}"
pip install --upgrade pip --quiet
echo -e "${GREEN}✅ Pip upgraded${NC}"

# Step 4: Install dependencies
echo ""
echo -e "${BLUE}📦 Step 4: Installing dependencies...${NC}"
echo -e "${YELLOW}⏳ This may take a few minutes...${NC}"
pip install -r requirements.txt --quiet
echo -e "${GREEN}✅ All dependencies installed${NC}"

# Step 5: Set up configuration
echo ""
echo -e "${BLUE}⚙️  Step 5: Setting up configuration...${NC}"
if [ ! -f "credentials/.env" ]; then
    cp credentials/.env.example credentials/.env
    echo -e "${GREEN}✅ Configuration file created${NC}"
    echo -e "${YELLOW}⚠️  Please edit credentials/.env to add your API keys (optional for yfinance)${NC}"
else
    echo -e "${GREEN}✅ Configuration file already exists${NC}"
fi

# Step 6: Create necessary directories
echo ""
echo -e "${BLUE}📂 Step 6: Creating data directories...${NC}"
mkdir -p logs data/raw data/processed data/models
echo -e "${GREEN}✅ Directories created${NC}"

# Step 7: Make scripts executable
echo ""
echo -e "${BLUE}🔐 Step 7: Setting script permissions...${NC}"
chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true
echo -e "${GREEN}✅ Script permissions set${NC}"

# Test installation
echo ""
echo -e "${BLUE}🧪 Step 8: Testing installation...${NC}"
python3 -c "import fastapi, yfinance, torch, pandas; print('✅ All critical imports successful!')"

# Display summary
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  🎉 INSTALLATION COMPLETE! 🎉               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✅ Project setup complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo "1. ${YELLOW}[Optional]${NC} Edit API keys:"
echo "   nano credentials/.env"
echo ""
echo "2. Start the server:"
echo "   ${GREEN}./scripts/run_server.sh${NC}"
echo "   or"
echo "   ${GREEN}uvicorn app.main:app --reload --host 0.0.0.0 --port 8000${NC}"
echo ""
echo "3. Open dashboard in browser:"
echo "   ${GREEN}http://localhost:8000/dashboard${NC}"
echo ""
echo "4. View API documentation:"
echo "   ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo "5. ${YELLOW}[Optional]${NC} Download historical data:"
echo "   ${GREEN}python scripts/download_data.py${NC}"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo -e "${YELLOW}📝 Note: yfinance works without API keys!${NC}"
echo -e "${YELLOW}   Alpha Vantage requires free API key (25 calls/day)${NC}"
echo -e "${YELLOW}   Get key at: https://www.alphavantage.co/support/#api-key${NC}"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}Happy Trading! 📈🚀${NC}"
echo ""