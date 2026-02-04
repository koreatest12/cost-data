#!/bin/bash
echo "🔧 Restoring execution permissions..."
find . -type f -name "*.sh" -print0 | while IFS= read -r -d '' file; do
    chmod +x "$file"
    echo "  - Fixed: $file"
done
echo "✅ Done."
