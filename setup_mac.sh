#!/bin/bash

echo "Installing Node dependencies..."
cd hello-eth
npm install
cd ..

echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt
echo "Setup complete."
echo "To run the application, navigate to the SmartHome directory and run:"
echo "./runSimulation_mac.sh"
echo "./run_mac.sh"
