#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Starting Truffle Develop in a new terminal window..."
osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_ROOT/hello-eth' && npx truffle develop\""

echo "Waiting for Truffle to start..."
sleep 5

echo "Running IOT Simulation..."
cd "$SCRIPT_DIR"
source "$PROJECT_ROOT/venv/bin/activate"
python3 IOTSimulation.py
