#!/bin/bash
echo "🚀 Starting System Health Check for v2026.282..."
URL="http://localhost:8080/api/stats"
RESPONSE=%{http_code}
if [ "$RESPONSE" -eq 200 ]; then
  echo "✅ System is UP and Running (HTTP 200)"
  curl -s $URL | jq .
else
  echo "❌ System Health Check Failed (HTTP $RESPONSE)"
  exit 1
fi
