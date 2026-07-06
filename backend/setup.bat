@echo off
echo ==========================================
echo INNERVOICE BACKEND SETUP
echo ==========================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python 3.11+ is required but not found in PATH.
    echo Please install Python and make sure it is added to your PATH.
    exit /b 1
)

:: Create Virtual Environment
if not exist venv (
    echo Creating python virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
    echo Skipping creation...
)

:: Install Dependencies
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo ==========================================
echo BACKEND SETUP COMPLETED SUCCESSFULLY!
echo ==========================================
pause
