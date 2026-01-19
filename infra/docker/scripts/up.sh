#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "🎾 Starting Tournament Studio..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from example..."
    cp .env.example .env 2>/dev/null || echo "No .env.example found"
fi

# Start services
docker compose up -d --build

echo "✅ Tournament Studio is running!"
echo "   Frontend: http://localhost:3003"
echo "   API:      http://localhost:8001"
echo "   API Docs: http://localhost:8001/api/docs"
echo ""
echo "📌 Port assignments (to avoid conflicts with existing containers):"
echo "   Web:      3003 (internal 3000)"
echo "   API:      8001 (internal 8000)"
echo "   Postgres: 5435 (internal 5432)"
echo "   Redis:    6380 (internal 6379)"

