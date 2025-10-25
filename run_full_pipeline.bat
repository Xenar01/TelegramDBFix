@echo off
REM Full V1 Pipeline - Run all 5 days in sequence
REM ===============================================

echo ============================================================
echo Mosque Reconstruction Database - Full Pipeline (V1.0)
echo ============================================================
echo.

echo [Day 1/5] Extracting mosques from Excel files...
python src\excel_parser.py
if errorlevel 1 (
    echo ERROR: Excel extraction failed!
    pause
    exit /b 1
)
echo.

echo [Day 2/5] AI extraction from Telegram messages...
python src\ai_extract.py
if errorlevel 1 (
    echo ERROR: AI extraction failed!
    pause
    exit /b 1
)
echo.

echo [Day 3/5] Merging Excel + AI data...
python src\merge_data.py
if errorlevel 1 (
    echo ERROR: Merge failed!
    pause
    exit /b 1
)
echo.

echo [Day 4/5] Matching photos and maps...
python src\match_media.py
if errorlevel 1 (
    echo ERROR: Media matching failed!
    pause
    exit /b 1
)
echo.

echo [Day 5/5] Generating final reports...
python src\generate_final_report.py
if errorlevel 1 (
    echo ERROR: Report generation failed!
    pause
    exit /b 1
)
echo.

echo ============================================================
echo ✅ PIPELINE COMPLETE!
echo ============================================================
echo.
echo Main output:
echo   - out_csv\mosques_enriched_with_media.csv (Main database)
echo   - out_csv\FINAL_V1_REPORT.txt (Comprehensive report)
echo   - out_csv\mosque_database_summary.xlsx (Stakeholder file)
echo.
pause
