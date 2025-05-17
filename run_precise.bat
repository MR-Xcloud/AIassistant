@echo off
echo ===================================================
echo    PRECISE VOICE ASSISTANT WITH IMPROVED RAG
echo ===================================================
echo.

echo Activating Python 3.10 environment...
call .\venv_py310\Scripts\activate

echo.
echo Python environment information:
python --version
pip --version

echo.
echo Starting Precise Voice Assistant...
python voice_assistant_precise.py

pause