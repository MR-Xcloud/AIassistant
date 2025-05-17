@echo off
echo ===================================================
echo    WEBMOBRIL VOICE ASSISTANT API SERVER
echo ===================================================
echo.

echo Activating Python environment...
call ..\venv_py310\Scripts\activate

echo.
echo Starting Django server...
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

pause
