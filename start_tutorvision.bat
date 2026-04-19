@echo off
echo ==================================================
echo       STARTING TUTORVISION SERVERS...
echo ==================================================

echo [1] Starting Python Backend Server...
start "TutorVision Backend" cmd /k "cd /d "%~dp0backend" && set PYTHONPATH=src && python -m uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload"

echo [2] Starting React Frontend Server...
start "TutorVision Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Servers are launching in separate windows!
echo DO NOT CLOSE those two new black terminal windows.
echo.
echo URL: http://localhost:5173
echo.
pause
