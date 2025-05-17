@echo off
echo ===================================================
echo    FINAL VOICE ASSISTANT WITH MULTIPLE QUESTION SUPPORT
echo ===================================================
echo.

echo Activating Python 3.10 environment...
call .\venv_py310\Scripts\activate

echo.
echo Python environment information:
python --version
pip --version

echo.
echo Starting Final Voice Assistant...
python voice_assistant_langchain.py

pause