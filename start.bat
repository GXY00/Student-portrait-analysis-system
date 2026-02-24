@echo off
setlocal enabledelayedexpansion

title Student Portrait System Launcher

echo ===================================================
echo       Starting Student Portrait System
echo ===================================================

:: 1. Check Python environment
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in PATH.
    echo Please install Python and add it to your PATH.
    pause
    exit /b 1
)
echo [INFO] Python found.

:: 2. Check Node.js environment
call npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] NPM is not found in PATH.
    echo Please install Node.js and add it to your PATH.
    pause
    exit /b 1
)
echo [INFO] NPM found.

:: 3. Start Backend
echo [INFO] Starting Flask Backend...
cd backend
:: Use start to open a new window for the backend
start "Flask Backend" cmd /k "python app.py"
cd ..

:: 4. Start Frontend
echo [INFO] Starting Vue Frontend...
cd bishe
:: Use start to open a new window for the frontend
start "Vue Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ===================================================
echo       Services Launched!
echo ===================================================
echo.
echo Backend URL:  http://127.0.0.1:5000
echo Frontend URL: http://localhost:8080 (After compilation)
echo.
echo Note: Please wait for both windows to initialize.
echo Press any key to close this launcher window...
pause >nul
