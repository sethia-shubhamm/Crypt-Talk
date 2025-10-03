#!/usr/bin/env bash
# Render build script for Crypt-Talk

echo "🔨 Starting build process..."

# Install frontend dependencies and build
echo "📦 Installing frontend dependencies..."
cd public
npm install
echo "🏗️ Building React frontend..."
npm run build

# Move build folder to server directory for Flask to serve
echo "📁 Moving build files to server directory..."
if [ -d "../server/build" ]; then
    rm -rf ../server/build
fi
cp -r build ../server/

# Install backend dependencies
echo "🐍 Installing Python dependencies..."
cd ../server
pip install -r requirements.txt

echo "✅ Build completed successfully!"