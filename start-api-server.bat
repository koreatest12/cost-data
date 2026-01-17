@echo off
REM API Server Startup Script for Windows
REM This script starts the Cost Data File Management API Server

echo ======================================
echo Cost Data API Server
echo ======================================
echo.

REM Check if Java is installed
java -version >nul 2>&1
if errorlevel 1 (
    echo Error: Java is not installed. Please install JDK 17 or higher.
    exit /b 1
)

echo Starting API server...
echo Building application...
echo.

REM Build the application
call mvn clean package -DskipTests

if errorlevel 1 (
    echo Error: Build failed
    exit /b 1
)

echo.
echo Starting server on http://localhost:8080
echo.
echo Default credentials:
echo   User:  user / password
echo   Admin: admin / admin
echo.
echo Press Ctrl+C to stop the server
echo ======================================
echo.

REM Run the application
call mvn spring-boot:run
