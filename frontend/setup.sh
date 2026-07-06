#!/bin/bash
echo ==========================================
echo INNERVOICE FRONTEND SETUP
echo ==========================================

# Check if Node.js is installed
if ! command -v node &> /dev/null
then
    echo "Node.js is required but not found in PATH."
    echo "Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

echo "Installing dependencies..."
npm install

echo ==========================================
echo FRONTEND SETUP COMPLETED!
echo ==========================================
