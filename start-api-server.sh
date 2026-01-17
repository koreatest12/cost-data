#!/bin/bash

# API Server Startup Script for Linux/MacOS
# This script starts the Cost Data File Management API Server

echo "======================================"
echo "Cost Data API Server"
echo "======================================"
echo ""

# Check if Java is installed
if ! command -v java &> /dev/null; then
    echo "Error: Java is not installed. Please install JDK 17 or higher."
    exit 1
fi

# Check Java version
JAVA_VERSION=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}' | cut -d'.' -f1)
if [ "$JAVA_VERSION" -lt 17 ]; then
    echo "Error: Java 17 or higher is required. Current version: $JAVA_VERSION"
    exit 1
fi

echo "Starting API server..."
echo "Building application..."

# Build the application
mvn clean package -DskipTests

if [ $? -ne 0 ]; then
    echo "Error: Build failed"
    exit 1
fi

echo ""
echo "Starting server on http://localhost:8080"
echo ""
echo "Default credentials:"
echo "  User:  user / password"
echo "  Admin: admin / admin"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================"
echo ""

# Run the application
mvn spring-boot:run
