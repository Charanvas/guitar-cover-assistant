#!/bin/bash

echo "========================================"
echo "Guitar Cover Assistant - Setup"
echo "========================================"

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
cd backend
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p uploads
mkdir -p ../models_data

cd ..

echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo ""
echo "To run the application:"
echo "1. Run: ./run.sh"
echo "2. Open your browser to: http://localhost:5000"
echo ""
echo "Note: First run may take longer as models are initialized."
echo "========================================"