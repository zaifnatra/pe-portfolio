#!/bin/bash
set -e

PROJECT_DIR="$HOME/pe-portfolio"

echo "Moving to project directory..."
cd "$PROJECT_DIR"

echo "Pulling latest changes from main..."
git fetch && git reset origin/main --hard

echo "Installing python dependencies..."
source venv/bin/activate
pip install -r requirements.txt
deactivate

echo "Restarting myportfolio service..."
sudo systemctl restart myportfolio

echo "Redeploy complete. myportfolio service restarted."