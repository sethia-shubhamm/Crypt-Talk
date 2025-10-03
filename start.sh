#!/usr/bin/env bash
# Render start script for Crypt-Talk

echo "🚀 Starting Crypt-Talk server..."
echo "📁 Serving React frontend from Flask backend"
cd server
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120