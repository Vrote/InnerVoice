@echo off
echo ==========================================
echo STARTING INNERVOICE BACKEND SERVER
echo ==========================================

if not exist venv (
    echo Virtual environment not found. Running setup first...
    call setup.bat
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting FastAPI server...
set PYTHONPATH=..
python main.py

pause
