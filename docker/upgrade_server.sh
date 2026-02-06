#!/bin/bash
echo "🚀 Detecting Server Version..."
# Check using standard docker command
if [ "$(docker ps -q -f name=gemini-soc-server)" ]; then
    echo "🔄 Upgrading Gemini SOC Server..."
    docker compose down
    docker compose pull
    docker compose up -d --force-recreate
    echo "✅ Server Upgraded to Latest Version."
else
    echo "✨ Installing New Gemini SOC Server..."
    docker compose up -d
    echo "✅ Server Installed Successfully."
fi
