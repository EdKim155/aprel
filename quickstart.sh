#!/bin/bash

echo "================================================"
echo "   Telegram Booking Bot - Quick Start Script"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your bot token and admin IDs."
    echo ""
    echo "To edit .env file, run:"
    echo "  nano .env"
    echo "or"
    echo "  vi .env"
    echo ""
    read -p "Press Enter to continue after editing .env file..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ Dependencies installed successfully"

# Run import test
echo ""
echo "Testing imports..."
python3 test_import.py

if [ $? -ne 0 ]; then
    echo "❌ Import test failed"
    exit 1
fi

echo ""
echo "================================================"
echo "   Setup Complete! 🎉"
echo "================================================"
echo ""
echo "To start the bot, run:"
echo "  source venv/bin/activate  # Activate virtual environment"
echo "  python bot.py             # Start the bot"
echo ""
echo "Or use this one-liner:"
echo "  source venv/bin/activate && python bot.py"
echo ""
echo "For more information, see:"
echo "  - README.md for overview"
echo "  - SETUP.md for detailed setup instructions"
echo "  - TESTING.md for testing guide"
echo ""
