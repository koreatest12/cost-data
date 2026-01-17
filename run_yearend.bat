@echo off
REM 연말정산 시뮬레이션 프로그램 실행 스크립트 (Windows)
REM Year-End Tax Settlement Simulation Program Launcher (Windows)

setlocal enabledelayedexpansion

echo ========================================
echo    연말정산 시뮬레이션 프로그램
echo    Year-End Tax Settlement Simulator
echo ========================================
echo.

REM Python 버전 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo 오류: Python이 설치되어 있지 않습니다.
    echo Error: Python is not installed.
    pause
    exit /b 1
)

REM 메뉴 선택
echo 실행 모드를 선택하세요:
echo 1) 대화형 모드 (Interactive Mode)
echo 2) 설정 파일 사용 (Use Configuration File)
echo 3) 예제 설정 파일 생성 (Create Example Config)
echo 4) 도움말 (Help)
echo.

set /p choice="선택 (1-4): "

if "%choice%"=="1" (
    python yearend_settlement.py
) else if "%choice%"=="2" (
    echo.
    echo 사용 가능한 설정 파일:
    dir /b yearend*.json 2>nul
    if errorlevel 1 echo   (설정 파일이 없습니다)
    echo.
    set /p config_file="설정 파일 경로를 입력하세요: "
    if exist "!config_file!" (
        python yearend_settlement.py --config "!config_file!"
    ) else (
        echo 오류: 파일을 찾을 수 없습니다: !config_file!
    )
) else if "%choice%"=="3" (
    python yearend_settlement.py --create-example
) else if "%choice%"=="4" (
    python yearend_settlement.py --help
) else (
    echo 잘못된 선택입니다.
    exit /b 1
)

echo.
pause
