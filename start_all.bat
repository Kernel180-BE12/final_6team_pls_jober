@echo off
echo ========================================
echo    Final Project - All Services Start
echo ========================================
echo.

:: 프로젝트 루트 디렉토리로 이동
cd /d "%~dp0"

:: 각 서비스별 터미널 창에서 실행
echo [1/3] Starting Backend (Spring Boot)...
start "Backend - Spring Boot" cmd /k "cd /d back && gradlew bootRun"

echo [2/3] Starting Frontend (Vue.js + Vite)...
start "Frontend - Vue.js" cmd /k "cd /d front && npm run dev"

echo [3/3] Starting AI Service (FastAPI)...
start "AI Service - FastAPI" cmd /k "cd /d ai && python main.py"

echo.
echo ========================================
echo    All services are starting...
echo ========================================
echo.
echo Backend:    http://localhost:8080
echo Frontend:   http://localhost:5173
echo AI Service: http://localhost:8000
echo.
echo Press any key to exit this window...
pause > nul
