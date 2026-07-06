@echo off
echo ==========================================
echo INNERVOICE FRONTEND SETUP
echo ==========================================

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js is required but not found in PATH.
    echo Please install Node.js 18+ from https://nodejs.org
    exit /b 1
)

echo Installing dependencies...
call npm install

echo ==========================================
echo FRONTEND SETUP COMPLETED!
echo ==========================================
pause
