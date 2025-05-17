@echo off
echo ===================================================
echo    ADVANCED PRODUCT SCRAPER WITH SELENIUM
echo ===================================================
echo.

echo Activating Python 3.10 environment...
call .\venv_py310\Scripts\activate

echo.
echo Python environment information:
python --version
pip --version

echo.
echo Running Advanced Product Scraper...
python advanced_scraper.py

pause