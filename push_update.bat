@echo off
setlocal enabledelayedexpansion
title Push Updates to GitHub

echo ===================================================
echo       Git Auto Push Script
echo ===================================================
echo.

:: 1. 检查是否安装了 Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in PATH.
    pause
    exit /b 1
)

:: 2. 显示当前 Git 状态
echo [INFO] Current Status:
git status
echo.

:: 3. 询问提交信息
set /p msg="Enter commit message (Press Enter for default 'Update project'): "
if "!msg!"=="" set msg="Update project"

:: 4. 执行 Git 命令
echo.
echo [INFO] Adding files...
git add .

echo [INFO] Committing with message: "!msg!"...
git commit -m "!msg!"

echo [INFO] Pushing to origin master...
git push origin master

echo.
if %errorlevel% equ 0 (
    echo [SUCCESS] Push completed successfully!
) else (
    echo [ERROR] Push failed. Please check the error messages above.
)

echo.
pause
