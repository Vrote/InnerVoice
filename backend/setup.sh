#!/bin/bash
# backend/setup.sh

echo "=========================================="
echo "INNERVOICE BACKEND SETUP"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 is required but not found."
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists. Skipping..."
fi

# Activate and install dependencies
source venv/bin/activate
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "=========================================="
echo "BACKEND SETUP COMPLETED SUCCESSFULLY!"
echo "=========================================="
