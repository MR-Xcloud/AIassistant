@echo off
echo ===================================================
echo    DATA CLEANER FOR SCRAPED CONTENT
echo ===================================================
echo.

echo Activating Python 3.10 environment...
call .\venv_py310\Scripts\activate

echo.
echo Python environment information:
python --version
pip --version

echo.
echo Running Data Cleaner...
python data_cleaner.py

echo.
echo Data cleaning completed. Results saved to:
echo - clean_data.pkl (for the voice assistant)
echo - clean_data.json (for easy inspection)
echo - clean_data.txt (for easy reading)

pause