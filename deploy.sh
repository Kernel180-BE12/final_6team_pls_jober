#!/bin/bash

# ===================================================================
#  통합 배포 스크립트
# ===================================================================

set -e  # 에러 발생 시 스크립트 중단

echo "🚀 PLS-Jober 통합 배포 시작..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경변수 파일 확인
if [ ! -f ".env" ]; then
    log_error ".env 파일이 없습니다. env.example을 참고하여 .env 파일을 생성해주세요."
    exit 1
fi

# Docker 및 Docker Compose 설치 확인
if ! command -v docker &> /dev/null; then
    log_error "Docker가 설치되어 있지 않습니다."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose가 설치되어 있지 않습니다."
    exit 1
fi

# 기존 컨테이너 정리
log_info "기존 컨테이너 정리 중..."
docker-compose down --remove-orphans || true

# 사용하지 않는 이미지 정리
log_info "사용하지 않는 Docker 이미지 정리 중..."
docker image prune -f

# AI 서비스 이미지 빌드
log_info "AI 서비스 이미지 빌드 중..."
docker-compose build ai-service

# 백엔드 이미지 pull (Docker Hub에서)
log_info "백엔드 이미지 다운로드 중..."
docker pull jonathanchoii/pls-jober-backend:latest

# 프론트엔드 빌드 (로컬에서)
log_info "프론트엔드 빌드 중..."
cd front
npm ci
npm run build
cd ..

# 프론트엔드 빌드 완료 (nginx 컨테이너에서 직접 마운트됨)
log_info "프론트엔드 빌드 완료"

# 호스트 서비스 상태 확인
log_info "호스트 서비스 상태 확인 중..."

# MySQL 상태 확인
if systemctl is-active --quiet mysql; then
    log_success "MySQL이 정상적으로 실행 중입니다."
else
    log_warning "MySQL이 실행되지 않았습니다. sudo systemctl start mysql로 시작해주세요."
fi

# ChromaDB 상태 확인 (포트 8001로 가정)
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    log_success "ChromaDB가 정상적으로 실행 중입니다."
else
    log_warning "ChromaDB 헬스체크 실패. ChromaDB가 실행 중인지 확인해주세요."
fi

# 호스트 Nginx 중지 (Docker nginx 사용)
log_info "호스트 Nginx 중지 중..."
sudo systemctl stop nginx || true
sudo systemctl disable nginx || true

# 서비스 시작
log_info "Docker 서비스 시작 중..."
docker-compose up -d

# 헬스체크
log_info "서비스 헬스체크 중..."
sleep 30

# 백엔드 헬스체크
if curl -f http://localhost:8080/actuator/health > /dev/null 2>&1; then
    log_success "백엔드 서비스가 정상적으로 실행 중입니다."
else
    log_warning "백엔드 서비스 헬스체크 실패. 로그를 확인해주세요."
fi

# AI 서비스 헬스체크
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log_success "AI 서비스가 정상적으로 실행 중입니다."
else
    log_warning "AI 서비스 헬스체크 실패. 로그를 확인해주세요."
fi

# Nginx 컨테이너 헬스체크
if curl -f http://localhost/health > /dev/null 2>&1; then
    log_success "Nginx 컨테이너가 정상적으로 실행 중입니다."
else
    log_warning "Nginx 컨테이너 헬스체크 실패. 로그를 확인해주세요."
fi

# 서비스 상태 확인
log_info "서비스 상태 확인:"
docker-compose ps

log_success "🎉 배포가 완료되었습니다!"
echo ""
echo "📋 서비스 접속 정보:"
echo "  🌐 프론트엔드: http://134.185.106.160"
echo "  🔧 백엔드 API: http://134.185.106.160/api"
echo "  🤖 AI 서비스: http://134.185.106.160/ai"
echo ""
echo "📊 서비스 관리 명령어:"
echo "  Docker 서비스 상태 확인: docker-compose ps"
echo "  Docker 서비스 로그 확인: docker-compose logs -f [서비스명]"
echo "  Docker 서비스 중지: docker-compose down"
echo "  Docker 서비스 재시작: docker-compose restart [서비스명]"
echo ""
echo "  호스트 서비스 관리:"
echo "  MySQL 상태: sudo systemctl status mysql"
echo "  MySQL 재시작: sudo systemctl restart mysql"
echo "  ChromaDB 상태: curl http://localhost:8001/health"
echo ""
echo "  Docker 서비스 관리:"
echo "  Nginx 컨테이너 로그: docker-compose logs -f nginx"
echo "  Nginx 컨테이너 재시작: docker-compose restart nginx"
