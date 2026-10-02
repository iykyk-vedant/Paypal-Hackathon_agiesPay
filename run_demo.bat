@echo off
title AegisPay - Autonomous Multi-Agent AI Fraud Shield for PayPal
color 0B

echo ==============================================================================
echo           AegisPay: Autonomous Multi-Agent AI Fraud Shield for PayPal
echo ==============================================================================
echo.

:: Detect Python executable
set "PYTHON_EXE=python"
if exist "C:\Users\Vedant\AppData\Local\Programs\Python\Python310\python.exe" (
    set "PYTHON_EXE=C:\Users\Vedant\AppData\Local\Programs\Python\Python310\python.exe"
)

echo [*] Using Python interpreter: %PYTHON_EXE%
echo [*] Checking dependencies...
"%PYTHON_EXE%" -c "import fastapi, uvicorn, httpx, dotenv" >nul 2>&1
if errorlevel 1 (
    echo [!] Installing required dependencies...
    "%PYTHON_EXE%" -m pip install -r requirements.txt
)

echo.
echo [*] Launching AegisPay Swarm Orchestrator on http://localhost:8085 ...
start "AegisPay Swarm Orchestrator (Port 8085)" /min "%PYTHON_EXE%" aegispay-system\orchestrator_agent\agent.py

echo [*] Launching AG Grid Enterprise Ops Dashboard on http://localhost:8088 ...
start "AegisPay Dashboard Server (Port 8088)" /min "%PYTHON_EXE%" -m http.server 8088 --directory dashboard

echo [*] Waiting for services to initialize (3 seconds)...
timeout /t 3 /nobreak >nul

echo [*] Opening AegisPay Ops Dashboard in your default browser...
start http://localhost:8088

echo.
echo ==============================================================================
echo [SUCCESS] AegisPay Swarm & Dashboard are LIVE!
echo.
echo   - Ops Dashboard URL:  http://localhost:8088
echo   - Backend Swarm API:  http://localhost:8085
echo   - Live SSE Stream:    http://localhost:8085/events/stream
echo   - Health Check:       http://localhost:8085/health
echo.
echo Press any key in this window to stop all AegisPay background services...
echo ==============================================================================
pause >nul

echo [*] Terminating AegisPay services...
taskkill /fi "WINDOWTITLE eq AegisPay Swarm Orchestrator*" /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq AegisPay Dashboard Server*" /f >nul 2>&1
echo [OK] All AegisPay services stopped cleanly.
timeout /t 2 /nobreak >nul
