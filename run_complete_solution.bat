@echo off
echo ===================================================
echo    COMPLETE SOLUTION WITH ADVANCED SCRAPING
echo ===================================================
echo.

echo Activating Python 3.10 environment...
call .\venv_py310\Scripts\activate

echo.
echo Python environment information:
python --version
pip --version

echo.
echo Step 1: Running Advanced Product Scraper...
python advanced_scraper.py

echo.
echo Step 2: Extracting Product Information...
python product_extractor.py

echo.
echo Step 3: Starting Precise Voice Assistant...
python voice_assistant_precise.py

pause