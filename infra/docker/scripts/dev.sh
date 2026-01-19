#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "🎾 Starting Tournament Studio (Development Mode)..."

docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

echo "✅ Development environment started!"


