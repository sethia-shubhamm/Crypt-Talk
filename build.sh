#!/usr/bin/env bash
# Render build script for Crypt-Talk

echo "🔨 Starting build process..."

# Install frontend dependencies and build
echo "📦 Installing frontend dependencies..."
cd public
npm install
echo "🏗️ Building React frontend..."
npm run build

# Install backend dependencies
echo "🐍 Installing Python dependencies..."
cd ../server
pip install -r requirements.txt

echo "✅ Build completed successfully!"