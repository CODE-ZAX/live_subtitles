#!/bin/bash

# Docker build script for the AI Video Transcription App

set -e

echo "🚀 Building AI Video Transcription App for Docker..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js to build the frontend."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker."
    exit 1
fi

# Build React frontend
print_status "Building React frontend..."
cd frontend

# Install dependencies
print_status "Installing frontend dependencies..."
npm install

# Build the frontend
print_status "Building frontend for production..."
npm run build

print_success "Frontend built successfully!"

# Go back to root directory
cd ..

# Build Docker image
print_status "Building Docker image..."
docker-compose build

print_success "Docker image built successfully!"
print_status "To start the application, run: docker-compose up"
print_status "The app will be available at: http://localhost:8000"
