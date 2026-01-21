#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "🛑 Stopping Tournament Studio..."
docker compose down

echo "✅ Tournament Studio stopped."



