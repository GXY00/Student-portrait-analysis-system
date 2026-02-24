@echo off
echo Stopping Project Processes...

echo.
echo Killing Python processes (Backend)...
taskkill /F /IM python.exe /T 2>nul
if %errorlevel% equ 0 (
    echo Python processes stopped.
) else (
    echo No Python processes found or access denied.
)

echo.
echo Killing Node.js processes (Frontend)...
taskkill /F /IM node.exe /T 2>nul
if %errorlevel% equ 0 (
    echo Node.js processes stopped.
) else (
    echo No Node.js processes found or access denied.
)

echo.
echo ========================================================
echo All related processes have been requested to terminate.
echo Note: This script forcibly stops ALL Python and Node.js
echo processes running on your current user session.
echo ========================================================
pause
