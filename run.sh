#!/bin/bash
# Startup script for Community Tourism Relay Bridge Server

echo "Starting Community Tourism Relay System..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the server
echo ""
echo "Starting Flask server..."
echo "Website will be available at: http://localhost:5000"
echo "API endpoints available at: http://localhost:5000/api/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py

