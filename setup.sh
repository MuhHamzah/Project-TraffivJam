#!/bin/bash
# Setup script for Smart Traffic Monitoring System on Linux/Mac

echo "========================================"
echo "Smart Traffic Monitoring System Setup"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.9+ first"
    exit 1
fi

echo "[1/4] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo "[2/4] Activating virtual environment..."
source venv/bin/activate

echo "[3/4] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "[4/4] Creating data directories..."
mkdir -p data/jembatan_merah
mkdir -p data/jl_djuanda
mkdir -p data/stasiun_bogor

echo ""
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit templates/maps.html and add your Google Maps API key"
echo "2. Run: ./run.sh"
echo "3. Open http://localhost:5000 in your browser"
echo ""
