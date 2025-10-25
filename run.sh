#!/bin/bash
# Quick-start script for Linux/Mac

echo "========================================"
echo "Telegram Mosque Database ETL"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

echo "[1/3] Installing dependencies..."
python3 -m pip install -r requirements.txt --quiet

echo "[2/3] Running ETL parser..."
python3 src/parse_export.py

echo "[3/3] Done!"
echo
echo "Check the following directories:"
echo "  - out_csv/         : CSV files"
echo "  - media_organized/ : Photos organized by province"
echo

read -p "Press enter to continue..."
