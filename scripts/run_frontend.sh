#!/usr/bin/env bash
# Start React frontend
cd "$(dirname "$0")/../frontend"
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "Starting Vite React development server on port 5173..."
npm run dev
