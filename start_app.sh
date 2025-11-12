#!/bin/bash
# Start the Job Cross-Reference Web App

echo "🚀 Starting Job Cross-Reference Web App..."
echo ""
echo "📋 Make sure you have:"
echo "   - mentors.csv file ready"
echo "   - config.json with API keys"
echo ""
echo "🌐 Opening http://localhost:5001 in your browser..."
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"
python3 app.py

