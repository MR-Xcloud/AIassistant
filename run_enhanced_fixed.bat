@echo off
echo Activating Python 3.10 environment...
call .\venv_py310\Scripts\activate

echo.
echo Python environment information:
python --version
pip --version

echo.
echo Starting Enhanced Fixed Voice Assistant with accurate answers...
python voice_assistant_fixed_enhanced.py

pause