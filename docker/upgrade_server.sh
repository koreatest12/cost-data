#!/bin/bash
echo "🚀 Detecting Server Version..."
if [ "$(docker ps -q -f name=soc-dashboard-v1)" ]; then
    echo "🔄 Upgrading SOC Server..."
    docker-compose down
    docker-compose pull
    docker-compose up -d --force-recreate
    echo "✅ Server Upgraded to Latest Version."
else
    echo "✨ Installing New SOC Server..."
    docker-compose up -d
    echo "✅ Server Installed Successfully."
fi
