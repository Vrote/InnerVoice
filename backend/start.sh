#!/bin/bash
# backend/start.sh

echo "=========================================="
echo "STARTING INNERVOICE BACKEND SERVER"
echo "=========================================="

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    chmod +x setup.sh
    ./setup.sh
fi

source venv/bin/activate
echo "Starting FastAPI server..."
export PYTHONPATH=$(pwd)/..
python main.py
