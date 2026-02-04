#!/bin/bash
echo "🔧 Restoring permissions..."
find . -type f -name "*.sh" -exec chmod +x {} \;
echo "✅ Done."
