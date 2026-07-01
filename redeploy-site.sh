#!/bin/bash
set -e

PROJECT_DIR="$HOME/pe-portfolio"
SESSION_NAME="flask"

echo "Killing existing tmux sessions..."
tmux kill-server 2>/dev/null || true

echo "Freeing port 5000 (in case a non-tmux process is holding it)..."
fuser -k 5000/tcp 2>/dev/null || true
sleep 1

echo "Moving to project directory..."
cd "$PROJECT_DIR"

echo "Pulling latest changes from main..."
git fetch && git reset origin/main --hard

echo "Installing python dependencies..."
source venv/bin/activate
pip install -r requirements.txt
deactivate

echo "Starting Flask server in a new tmux session..."
tmux new-session -d -s "$SESSION_NAME" "cd $PROJECT_DIR && source venv/bin/activate && if [ -f app.py ]; then export FLASK_APP=app.py; elif [ -f main.py ]; then export FLASK_APP=main.py; fi && flask run --host=0.0.0.0"

echo "Redeploy complete. Flask server running in tmux session '$SESSION_NAME'."
