@echo off
setlocal enabledelayedexpansion
title Muazu Studio v2.2 - Local AI Funny Dubbing ^& Video Production Studio

echo ===============================================================================
echo                MUAZU STUDIO (v2.2 Local-First)
echo   Local AI Funny Dubbing ^& Video Production Suite (Zero Extra Cost)
echo ===============================================================================
echo.

:: 1. Detect Python Executable
set "PYTHON_EXE="
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
) else (
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        set "PYTHON_EXE=python"
    ) else (
        where py >nul 2>nul
        if %errorlevel% equ 0 (
            set "PYTHON_EXE=py -3"
        )
    )
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python 3.10+ executable could not be found!
    echo Please install Python 3.11 from python.org or ensure it is in your PATH.
    echo.
    pause
    exit /b 1
)

echo [OK] Using Python: "%PYTHON_EXE%"

:: 2. Check Virtual Environment or Dependencies
if exist "venv\Scripts\python.exe" (
    echo [INFO] Found virtual environment in venv\
    set "PYTHON_EXE=venv\Scripts\python.exe"
)

:: Verify dependencies from requirements.txt
"%PYTHON_EXE%" -c "import fastapi" >nul 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Installing required dependencies from requirements.txt...
    "%PYTHON_EXE%" -m pip install -r requirements.txt
)

:: 3. Ensure required directories exist
if not exist "data" mkdir data
if not exist "temp" mkdir temp
if not exist "models" mkdir models
if not exist "presets" mkdir presets
if not exist "storage" mkdir storage
if not exist "storage\projects" mkdir storage\projects

:: 4. Check Single Port Availability (127.0.0.1:8000)
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>nul
if %errorlevel% equ 0 (
    echo [NOTICE] Port 8000 is currently occupied.
    echo Opening dashboard in browser...
    start "" "http://127.0.0.1:8000"
)

:: 5. Launch Browser in Background after 2 seconds
start /b powershell -NoProfile -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8000'" >nul 2>nul

:: 6. Launch Master Server
echo.
echo [INFO] Starting Master Server on http://127.0.0.1:8000 ...
echo [INFO] Ready! Your browser will open shortly at: http://127.0.0.1:8000
echo [INFO] Press Ctrl+C to stop the studio.
echo.

"%PYTHON_EXE%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Server stopped with error code %errorlevel%.
    pause
)
