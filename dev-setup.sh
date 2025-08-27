#!/bin/bash

# Development setup script for Car Booking System

echo "Setting up Car Booking System development environment..."

# Backend setup
echo "Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm install

cd ..

echo "Setup complete!"
echo ""
echo "To start development:"
echo "1. Backend: cd backend && python run_dev.py"
echo "2. Frontend: cd frontend && npm run dev"