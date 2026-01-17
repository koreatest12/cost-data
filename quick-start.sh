#!/bin/bash
#
# Quick Deployment Script for Cost Data
# Runs application locally on port 9999 for testing
#

set -e

echo "========================================="
echo "Cost Data - Quick Start (Port 9999)"
echo "========================================="

# Check Java
if ! command -v java &> /dev/null; then
    echo "ERROR: Java not found. Please install JDK 17 or higher."
    exit 1
fi

# Check Maven
if ! command -v mvn &> /dev/null; then
    echo "ERROR: Maven not found. Please install Maven 3.6 or higher."
    exit 1
fi

# Build the application
echo ""
echo "[1/4] Building application..."
mvn clean package -DskipTests

if [ $? -ne 0 ]; then
    echo "ERROR: Build failed"
    exit 1
fi

# Create necessary directories
echo ""
echo "[2/4] Creating directories..."
mkdir -p uploads data

# Find the JAR file
JAR_FILE=$(find target -name "*.jar" -type f | head -n 1)

if [ -z "$JAR_FILE" ]; then
    echo "ERROR: JAR file not found in target directory"
    exit 1
fi

echo ""
echo "[3/4] Starting application on port 9999..."
echo "JAR: $JAR_FILE"
echo ""

# Run the application
echo "[4/4] Application running..."
echo "========================================="
echo "Access the application at:"
echo "  http://localhost:9999"
echo ""
echo "API Endpoints:"
echo "  http://localhost:9999/api/files/*"
echo ""
echo "Default Users:"
echo "  user/password (read/write)"
echo "  admin/admin (all permissions)"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================="
echo ""

java -jar "$JAR_FILE" --server.port=9999
