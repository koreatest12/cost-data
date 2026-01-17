#!/bin/bash
# 연말정산 시뮬레이션 프로그램 실행 스크립트
# Year-End Tax Settlement Simulation Program Launcher

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROGRAM="$SCRIPT_DIR/yearend_settlement.py"

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   연말정산 시뮬레이션 프로그램${NC}"
echo -e "${GREEN}   Year-End Tax Settlement Simulator${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Python 버전 확인
if ! command -v python3 &> /dev/null; then
    echo "오류: Python 3가 설치되어 있지 않습니다."
    echo "Error: Python 3 is not installed."
    exit 1
fi

# 메뉴 선택
echo "실행 모드를 선택하세요:"
echo "1) 대화형 모드 (Interactive Mode)"
echo "2) 설정 파일 사용 (Use Configuration File)"
echo "3) 예제 설정 파일 생성 (Create Example Config)"
echo "4) 도움말 (Help)"
echo ""
read -p "선택 (1-4): " choice

case $choice in
    1)
        python3 "$PROGRAM"
        ;;
    2)
        echo ""
        echo "사용 가능한 설정 파일:"
        ls -1 "$SCRIPT_DIR"/yearend*.json 2>/dev/null || echo "  (설정 파일이 없습니다)"
        echo ""
        read -p "설정 파일 경로를 입력하세요: " config_file
        if [ -f "$config_file" ]; then
            python3 "$PROGRAM" --config "$config_file"
        elif [ -f "$SCRIPT_DIR/$config_file" ]; then
            python3 "$PROGRAM" --config "$SCRIPT_DIR/$config_file"
        else
            echo "오류: 파일을 찾을 수 없습니다: $config_file"
        fi
        ;;
    3)
        python3 "$PROGRAM" --create-example
        ;;
    4)
        python3 "$PROGRAM" --help
        ;;
    *)
        echo "잘못된 선택입니다."
        exit 1
        ;;
esac
