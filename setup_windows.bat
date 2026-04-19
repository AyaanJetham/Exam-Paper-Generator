@echo off
echo ==================================================
echo     TUTORVISION - FIRST TIME SETUP
echo ==================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Download Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo Download Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Python found
echo [OK] Node.js found
echo.

:: ---- Backend Setup ----
echo [1/4] Setting up Python virtual environment...
cd /d "%~dp0backend"

if not exist "venv" (
    python -m venv venv
    echo      Created virtual environment.
) else (
    echo      Virtual environment already exists.
)

echo [2/4] Installing Python dependencies (this may take a few minutes)...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
python -m spacy download en_core_web_sm --quiet
echo      Python packages installed.

:: Check for .env file
if not exist ".env" (
    echo.
    echo [IMPORTANT] No .env file found!
    copy .env.example .env >nul
    echo      Created .env from template.
    echo      You MUST edit backend\.env and add your API keys.
    echo      Get free keys from:
    echo        - Groq:     https://console.groq.com/keys
    echo        - Gemini:   https://aistudio.google.com/apikey
    echo        - Together: https://api.together.ai/settings/api-keys
    echo.
) else (
    echo      .env file found.
)

:: ---- Frontend Setup ----
echo [3/4] Installing frontend dependencies...
cd /d "%~dp0frontend"
call npm install --silent
echo      Frontend packages installed.

echo.
echo ==================================================
echo [4/4] SETUP COMPLETE!
echo ==================================================
echo.
echo NEXT STEPS:
echo   1. Edit backend\.env with your API keys (if not done)
echo   2. Run start_tutorvision.bat to launch the app
echo   3. Open http://localhost:5173 in your browser
echo.
pause
