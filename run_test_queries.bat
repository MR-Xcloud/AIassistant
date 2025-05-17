@echo off
echo Activating Python 3.10 environment...
call .\venv_py310\Scripts\activate

echo.
echo Python environment information:
python --version
pip --version

echo.
echo Testing specific query types...
python test_specific_queries.py

pause