@echo off
echo Activating Python 3.10 environment...
call .\venv_py310\Scripts\activate

echo.
echo Python environment information:
python --version
pip --version

echo.
echo Updating knowledge base with product information...
python update_knowledge_base.py

echo.
echo Starting Complete Voice Assistant...
python voice_assistant_complete.py

pause