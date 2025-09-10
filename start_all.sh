#!/bin/bash

echo "========================================"
echo "   Final Project - All Services Start"
echo "========================================"
echo

# 프로젝트 루트 디렉토리로 이동
cd "$(dirname "$0")"

# 각 서비스별 터미널 창에서 실행
echo "[1/3] Starting Backend (Spring Boot)..."
gnome-terminal --title="Backend - Spring Boot" -- bash -c "cd back && ./gradlew bootRun; exec bash" 2>/dev/null || \
xterm -title "Backend - Spring Boot" -e "cd back && ./gradlew bootRun; bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '$(pwd)'/back && ./gradlew bootRun"' 2>/dev/null || \
echo "Please start Backend manually: cd back && ./gradlew bootRun"

echo "[2/3] Starting Frontend (Vue.js + Vite)..."
gnome-terminal --title="Frontend - Vue.js" -- bash -c "cd front && npm run dev; exec bash" 2>/dev/null || \
xterm -title "Frontend - Vue.js" -e "cd front && npm run dev; bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '$(pwd)'/front && npm run dev"' 2>/dev/null || \
echo "Please start Frontend manually: cd front && npm run dev"

echo "[3/3] Starting AI Service (FastAPI)..."
gnome-terminal --title="AI Service - FastAPI" -- bash -c "cd ai && python main.py; exec bash" 2>/dev/null || \
xterm -title "AI Service - FastAPI" -e "cd ai && python main.py; bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '$(pwd)'/ai && python main.py"' 2>/dev/null || \
echo "Please start AI Service manually: cd ai && python main.py"

echo
echo "========================================"
echo "   All services are starting..."
echo "========================================"
echo
echo "Backend:    http://localhost:8080"
echo "Frontend:   http://localhost:5173"
echo "AI Service: http://localhost:8000"
echo
echo "Press Enter to exit..."
read
