@echo off
echo Activating Python 3.10 environment...
call .\venv_py310\Scripts\activate

echo.
echo Python environment information:
python --version
pip --version

echo.
echo Installing required packages for translation...
pip install requests

echo.
echo Starting Bilingual Voice Assistant (English & Hindi)...
python voice_assistant_bilingual.py

pause