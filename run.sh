#!/bin/bash

echo "========================================"
echo "Guitar Cover Assistant - Starting Server"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    ./setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "Error: backend directory not found."
    exit 1
fi

# Start the Flask server
echo "Starting Flask server..."
cd backend
python app.py