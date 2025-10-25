@echo off
REM Quick-start script for Windows

echo ========================================
echo Telegram Mosque Database ETL
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
python -m pip install -r requirements.txt --quiet

echo [2/3] Running ETL parser...
python src\parse_export.py

echo [3/3] Done!
echo.
echo Check the following directories:
echo   - out_csv\        : CSV files
echo   - media_organized\ : Photos organized by province
echo.

pause
