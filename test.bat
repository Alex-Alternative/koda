@echo off
echo Running Koda Stress Test...
echo.
cd /d "%~dp0"
call venv\Scripts\activate
python test_stress.py
echo.
pause
