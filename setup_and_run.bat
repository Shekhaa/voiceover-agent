@echo off
setlocal enabledelayedexpansion

title AuraVoice Studio - Setup and Launcher
color 0B

echo =====================================================================
echo           AuraVoice Studio - 1-Click Setup and Launcher
echo     (Kokoro-82M SOTA Voice Engine + Dramatic Music Auto-Ducking)
echo =====================================================================
echo.

:: 1. Check Python Installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python is not installed or not added to your system PATH!
    echo Please install Python 3.10 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PY_VER=%%i
echo   Found %PY_VER% - OK!
echo.

:: 2. Set Up Virtual Environment (.venv)
echo [2/5] Checking virtual environment...
if not exist ".venv\Scripts\activate.bat" (
    echo   Creating a new isolated virtual environment (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        color 0C
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo   Virtual environment created successfully.
) else (
    echo   Existing virtual environment (.venv) found.
)

:: 3. Activate Virtual Environment
echo.
echo [3/5] Activating virtual environment (.venv)...
call .venv\Scripts\activate.bat

:: 4. Install Dependencies
echo.
echo [4/5] Checking and installing Python dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Failed to install requirements!
    pause
    exit /b 1
)
echo   All dependencies installed successfully.

:: 5. Download Model Weights and Background Music Assets
echo.
echo [5/5] Verifying Kokoro-82M neural model and background music assets...
python download_assets.py
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Failed to download model or music assets!
    pause
    exit /b 1
)

:: Launching the Application
echo.
echo =====================================================================
echo   Setup Complete! Starting AuraVoice Studio...
echo   Opening: http://127.0.0.1:5000 in your browser
echo =====================================================================
echo.

:: Open browser after 2 seconds
start "" http://127.0.0.1:5000

:: Start Server
python server.py

pause
