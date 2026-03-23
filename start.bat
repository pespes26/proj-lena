@echo off
title Lena FM Dashboard

echo Installing backend dependencies...
cd /d "%~dp0backend"
pip install -r requirements.txt -q

echo Installing frontend dependencies...
cd /d "%~dp0frontend"
call npm install --silent

echo.
echo Starting backend on http://localhost:8000 ...
cd /d "%~dp0backend"
start "Lena Backend" cmd /k "uvicorn main:app --host 0.0.0.0 --port 8000"

echo Starting frontend on http://localhost:3000 ...
cd /d "%~dp0frontend"
start "Lena Frontend" cmd /k "npx vite --port 3000"

timeout /t 3 >nul
start http://localhost:3000

echo.
echo Both servers are running. Close the terminal windows to stop them.
