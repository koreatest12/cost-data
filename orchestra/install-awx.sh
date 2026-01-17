#!/bin/bash
#
# Ansible AWX (Orchestra Server) Installation Script
# 이 스크립트는 Ansible AWX를 설치하고 설정합니다.
#

set -e

echo "=========================================="
echo "Ansible AWX (Orchestra Server) 설치 시작"
echo "=========================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 함수: 메시지 출력
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. 시스템 요구사항 확인
print_info "시스템 요구사항 확인 중..."

# Docker 설치 확인
if ! command -v docker &> /dev/null; then
    print_error "Docker가 설치되어 있지 않습니다."
    print_info "Docker 설치 중..."
    
    # Ubuntu/Debian
    if [ -f /etc/debian_version ]; then
        sudo apt-get update
        sudo apt-get install -y \
            ca-certificates \
            curl \
            gnupg \
            lsb-release
        
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
          $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    # RHEL/CentOS
    elif [ -f /etc/redhat-release ]; then
        sudo yum install -y yum-utils
        sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        sudo systemctl start docker
        sudo systemctl enable docker
    fi
    
    print_info "Docker 설치 완료"
else
    print_info "Docker가 이미 설치되어 있습니다: $(docker --version)"
fi

# Docker Compose 확인
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose가 설치되어 있지 않습니다."
    print_info "Docker Compose 설치 중..."
    
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_info "Docker Compose 설치 완료"
else
    print_info "Docker Compose가 이미 설치되어 있습니다"
fi

# 2. AWX 설치 디렉토리로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

print_info "AWX 설치 디렉토리: $SCRIPT_DIR"

# 3. 기존 컨테이너 정리 (선택사항)
if [ "$1" == "--clean" ]; then
    print_warn "기존 AWX 컨테이너를 정리합니다..."
    docker-compose down -v || docker compose down -v || true
fi

# 4. AWX 컨테이너 시작
print_info "AWX 컨테이너를 시작합니다..."

if command -v docker-compose &> /dev/null; then
    docker-compose up -d
else
    docker compose up -d
fi

# 5. 컨테이너 상태 확인
print_info "컨테이너 상태 확인 중..."
sleep 5

if command -v docker-compose &> /dev/null; then
    docker-compose ps
else
    docker compose ps
fi

# 6. AWX 초기화 대기
print_info "AWX가 초기화될 때까지 기다립니다 (약 2-3분 소요)..."
print_info "로그를 확인하려면: docker logs -f awx_web"

# 7. 설치 완료 메시지
echo ""
echo "=========================================="
print_info "AWX (Orchestra Server) 설치가 완료되었습니다!"
echo "=========================================="
echo ""
echo "접속 정보:"
echo "  - URL: http://localhost:8080"
echo "  - 사용자명: admin"
echo "  - 비밀번호: admin"
echo ""
echo "다음 명령어로 로그를 확인할 수 있습니다:"
echo "  docker logs -f awx_web"
echo ""
echo "AWX를 중지하려면:"
echo "  cd $SCRIPT_DIR"
echo "  docker-compose down"
echo ""
echo "AWX를 완전히 제거하려면 (데이터 포함):"
echo "  cd $SCRIPT_DIR"
echo "  docker-compose down -v"
echo ""

# 8. 상태 확인 대기
print_info "AWX 웹 서비스가 준비될 때까지 대기 중..."
MAX_WAIT=180
WAIT_TIME=0
while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        print_info "AWX 웹 서비스가 준비되었습니다!"
        break
    fi
    sleep 5
    WAIT_TIME=$((WAIT_TIME + 5))
    echo -n "."
done

if [ $WAIT_TIME -ge $MAX_WAIT ]; then
    print_warn "AWX 웹 서비스가 아직 준비되지 않았을 수 있습니다."
    print_warn "잠시 후 http://localhost:8080 에 접속해 보세요."
fi

echo ""
print_info "설치 스크립트가 완료되었습니다."
