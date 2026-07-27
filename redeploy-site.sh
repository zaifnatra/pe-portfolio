#!/bin/bash
set -e

PROJECT_DIR="$HOME/pe-portfolio"

echo "Moving to project directory..."
cd "$PROJECT_DIR"

echo "Pulling latest changes from main..."
git fetch && git reset origin/main --hard

echo "Spinning down running containers..."
docker compose -f docker-compose.prod.yml down

echo "Rebuilding and starting containers..."
docker compose -f docker-compose.prod.yml up -d --build

echo "Redeploy complete. Containers rebuilt and running."
