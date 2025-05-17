@echo off
echo Activating Python 3.10 environment...
call .\venv_py310\Scripts\activate

echo.
echo Python environment information:
python --version
pip --version

echo.
echo Installing required packages for RAG with Groq...
pip install requests

echo.
echo Starting Voice Assistant with RAG and Groq...
python voice_assistant_with_rag.py

pause