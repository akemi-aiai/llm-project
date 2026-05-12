#!/usr/bin/env bash
set -euo pipefail

EMAIL="${1:-student@example.com}"
PASSWORD="${2:-StrongPassword123}"

curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\"}" || true

echo ""
echo "Login response:"
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${EMAIL}&password=${PASSWORD}"
echo ""
