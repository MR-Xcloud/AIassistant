@echo off
echo ===================================================
echo    LANGCHAIN VOICE ASSISTANT WITH GROQ
echo ===================================================
echo.

echo Activating Python 3.10 environment...
call .\venv_py310\Scripts\activate

echo.
echo Installing required packages...
pip install langchain faiss-cpu sentence-transformers langchain-community

echo.
echo Starting LangChain Voice Assistant...
python voice_assistant_langchain.py

pause