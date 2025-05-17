@echo off
echo Activating Python 3.10 environment...
call .\venv_py310\Scripts\activate

echo.
echo Python environment information:
python --version
pip --version

echo.
echo Starting Language-Aware Voice Assistant...
python voice_assistant_language_aware.py

pause