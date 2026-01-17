#!/bin/bash

# API Server Test Script
# This script tests if the API server is running and endpoints are accessible

API_URL="http://localhost:8080"
USER_CRED="user:password"
ADMIN_CRED="admin:admin"

echo "======================================"
echo "API Server Test"
echo "======================================"
echo ""

# Check if server is running
echo "1. Testing server connectivity..."
if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$API_URL" | grep -q "401\|200"; then
    echo "✓ Server is running on $API_URL"
else
    echo "✗ Server is not responding. Please start the server first."
    exit 1
fi
echo ""

# Test file list endpoint
echo "2. Testing file list endpoint..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -u "$USER_CRED" "$API_URL/api/files/list")
if [ "$HTTP_CODE" == "200" ]; then
    echo "✓ File list endpoint is accessible (HTTP $HTTP_CODE)"
else
    echo "✗ File list endpoint failed (HTTP $HTTP_CODE)"
fi
echo ""

# Test file create endpoint
echo "3. Testing file create endpoint..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -u "$USER_CRED" \
    -X POST "$API_URL/api/files/create" \
    -H "Content-Type: application/json" \
    -d '{"path":"test-file.txt","content":"Test content"}')
if [ "$HTTP_CODE" == "200" ]; then
    echo "✓ File create endpoint is accessible (HTTP $HTTP_CODE)"
else
    echo "✗ File create endpoint failed (HTTP $HTTP_CODE)"
fi
echo ""

# Test directory create endpoint
echo "4. Testing directory create endpoint..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -u "$USER_CRED" \
    -X POST "$API_URL/api/files/directory/create" \
    -H "Content-Type: application/json" \
    -d '{"path":"test-directory"}')
if [ "$HTTP_CODE" == "200" ]; then
    echo "✓ Directory create endpoint is accessible (HTTP $HTTP_CODE)"
else
    echo "✗ Directory create endpoint failed (HTTP $HTTP_CODE)"
fi
echo ""

# Test file read endpoint
echo "5. Testing file read endpoint..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -u "$USER_CRED" \
    "$API_URL/api/files/read?path=test-file.txt")
if [ "$HTTP_CODE" == "200" ]; then
    echo "✓ File read endpoint is accessible (HTTP $HTTP_CODE)"
else
    echo "✗ File read endpoint failed (HTTP $HTTP_CODE)"
fi
echo ""

# Test authentication
echo "6. Testing authentication..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/files/list")
if [ "$HTTP_CODE" == "401" ]; then
    echo "✓ Authentication is working (HTTP $HTTP_CODE - Unauthorized)"
else
    echo "✗ Authentication test unexpected result (HTTP $HTTP_CODE)"
fi
echo ""

# Test admin delete endpoint
echo "7. Testing delete endpoint (admin only)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -u "$ADMIN_CRED" \
    -X DELETE "$API_URL/api/files/delete?path=test-file.txt")
if [ "$HTTP_CODE" == "200" ]; then
    echo "✓ Delete endpoint is accessible (HTTP $HTTP_CODE)"
else
    echo "✗ Delete endpoint failed (HTTP $HTTP_CODE)"
fi
echo ""

# Test delete with regular user (should fail)
echo "8. Testing delete with regular user (should be forbidden)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -u "$USER_CRED" \
    -X POST "$API_URL/api/files/create" \
    -H "Content-Type: application/json" \
    -d '{"path":"test-file2.txt","content":"Test"}')
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -u "$USER_CRED" \
    -X DELETE "$API_URL/api/files/delete?path=test-file2.txt")
if [ "$HTTP_CODE" == "403" ]; then
    echo "✓ Regular user cannot delete (HTTP $HTTP_CODE - Forbidden)"
else
    echo "✗ Authorization test unexpected result (HTTP $HTTP_CODE)"
fi
echo ""

# Cleanup
echo "9. Cleaning up test files..."
curl -s -o /dev/null -u "$ADMIN_CRED" \
    -X DELETE "$API_URL/api/files/delete?path=test-file2.txt"
curl -s -o /dev/null -u "$ADMIN_CRED" \
    -X DELETE "$API_URL/api/files/delete?path=test-directory"
echo "✓ Cleanup complete"
echo ""

echo "======================================"
echo "API Server Test Complete"
echo "======================================"
