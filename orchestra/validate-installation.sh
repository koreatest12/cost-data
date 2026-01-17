#!/bin/bash
#
# AWX Installation Validation Script
# AWX 설치 상태를 검증하는 스크립트
#

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# 검증 시작
print_header "AWX Orchestra Server - 설치 검증"

ERRORS=0
WARNINGS=0

# 1. Docker 확인
print_info "Docker 설치 확인 중..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    print_success "Docker가 설치되어 있습니다: $DOCKER_VERSION"
else
    print_error "Docker가 설치되어 있지 않습니다"
    ERRORS=$((ERRORS + 1))
fi

# 2. Docker Compose 확인
print_info "Docker Compose 확인 중..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    print_success "Docker Compose가 설치되어 있습니다: $COMPOSE_VERSION"
elif docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version)
    print_success "Docker Compose가 설치되어 있습니다: $COMPOSE_VERSION"
else
    print_error "Docker Compose가 설치되어 있지 않습니다"
    ERRORS=$((ERRORS + 1))
fi

# 3. AWX 컨테이너 확인
print_info "AWX 컨테이너 상태 확인 중..."

CONTAINERS=("awx_postgres" "awx_redis" "awx_web" "awx_task")
for container in "${CONTAINERS[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        STATUS=$(docker inspect --format='{{.State.Status}}' "$container")
        if [ "$STATUS" == "running" ]; then
            print_success "$container 컨테이너가 실행 중입니다"
        else
            print_error "$container 컨테이너가 중지 상태입니다 (상태: $STATUS)"
            ERRORS=$((ERRORS + 1))
        fi
    else
        print_warn "$container 컨테이너를 찾을 수 없습니다 (아직 설치되지 않았을 수 있습니다)"
        WARNINGS=$((WARNINGS + 1))
    fi
done

# 4. 네트워크 확인
print_info "Docker 네트워크 확인 중..."
if docker network ls | grep -q "awx_network"; then
    print_success "AWX 네트워크가 생성되어 있습니다"
else
    print_warn "AWX 네트워크를 찾을 수 없습니다"
    WARNINGS=$((WARNINGS + 1))
fi

# 5. 볼륨 확인
print_info "Docker 볼륨 확인 중..."
VOLUMES=("postgres_data" "redis_data" "awx_projects" "awx_data")
for volume in "${VOLUMES[@]}"; do
    if docker volume ls | grep -q "orchestra_${volume}"; then
        print_success "볼륨 orchestra_${volume}이 생성되어 있습니다"
    else
        print_warn "볼륨 orchestra_${volume}을 찾을 수 없습니다"
        WARNINGS=$((WARNINGS + 1))
    fi
done

# 6. 포트 확인
print_info "포트 8080 사용 확인 중..."
if command -v netstat &> /dev/null; then
    if netstat -tuln 2>/dev/null | grep -q ":8080"; then
        print_success "포트 8080이 사용 중입니다 (AWX 웹 서비스)"
    else
        print_warn "포트 8080이 사용되지 않고 있습니다"
        WARNINGS=$((WARNINGS + 1))
    fi
elif command -v ss &> /dev/null; then
    if ss -tuln 2>/dev/null | grep -q ":8080"; then
        print_success "포트 8080이 사용 중입니다 (AWX 웹 서비스)"
    else
        print_warn "포트 8080이 사용되지 않고 있습니다"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    print_warn "netstat 또는 ss 명령어를 찾을 수 없어 포트를 확인할 수 없습니다"
    WARNINGS=$((WARNINGS + 1))
fi

# 7. 웹 서비스 확인
print_info "AWX 웹 서비스 응답 확인 중..."
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    print_success "AWX 웹 서비스가 응답합니다 (http://localhost:8080)"
else
    print_warn "AWX 웹 서비스가 아직 응답하지 않습니다 (초기화 중일 수 있습니다)"
    WARNINGS=$((WARNINGS + 1))
fi

# 8. 파일 구조 확인
print_info "Orchestra 파일 구조 확인 중..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

FILES=(
    "$SCRIPT_DIR/docker-compose.yml"
    "$SCRIPT_DIR/install-awx.sh"
    "$SCRIPT_DIR/README.md"
    "$SCRIPT_DIR/QUICKSTART.md"
    "$SCRIPT_DIR/playbooks/health-check.yml"
    "$SCRIPT_DIR/playbooks/deploy-webservers.yml"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "$(basename "$file") 파일이 존재합니다"
    else
        print_error "$(basename "$file") 파일을 찾을 수 없습니다"
        ERRORS=$((ERRORS + 1))
    fi
done

# 결과 요약
print_header "검증 결과 요약"

echo ""
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ 모든 검증 항목을 통과했습니다!${NC}"
    echo ""
    echo "AWX Orchestra Server가 정상적으로 설치되고 실행 중입니다."
    echo ""
    echo "다음 단계:"
    echo "  1. 웹 브라우저에서 http://localhost:8080 접속"
    echo "  2. 사용자명: admin, 비밀번호: admin으로 로그인"
    echo "  3. QUICKSTART.md 가이드를 참고하여 인벤토리 및 프로젝트 설정"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ 경고가 ${WARNINGS}개 발생했습니다${NC}"
    echo ""
    echo "AWX가 아직 완전히 초기화되지 않았을 수 있습니다."
    echo "몇 분 후 다시 시도해 보거나 로그를 확인하세요:"
    echo "  docker logs -f awx_web"
    exit 0
else
    echo -e "${RED}✗ 오류가 ${ERRORS}개, 경고가 ${WARNINGS}개 발생했습니다${NC}"
    echo ""
    echo "설치에 문제가 있습니다. 다음을 확인하세요:"
    echo "  1. Docker가 올바르게 설치되어 있는지 확인"
    echo "  2. install-awx.sh 스크립트를 실행했는지 확인"
    echo "  3. 로그를 확인: docker-compose logs"
    echo "  4. README.md의 문제 해결 섹션 참조"
    exit 1
fi
