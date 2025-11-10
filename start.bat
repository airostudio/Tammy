@echo off
echo ======================================
echo   Tammy AI Assistant - Startup Script
echo ======================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create .env if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo WARNING: Please edit .env with your configuration
)

REM Create necessary directories
echo Creating necessary directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs

echo.
echo Setup complete!
echo.
echo To start Tammy, run:
echo   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo API Documentation will be available at:
echo   http://localhost:8000/docs
echo.
pause
