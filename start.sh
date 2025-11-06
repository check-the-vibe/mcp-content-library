#!/bin/bash
# Quick start script for MCP Content Library

set -e

echo "🚀 Starting MCP Content Library..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies if needed
if ! python -c "import mcp" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -q "mcp[cli]" starlette uvicorn
fi

# Create storage directory
mkdir -p ~/.mcp_snippets

# Check which mode to run
MODE="${1:-http}"

if [ "$MODE" = "stdio" ]; then
    echo "✅ Starting server in STDIO mode..."
    echo "   (Use Ctrl+C to stop)"
    echo ""
    python server.py
elif [ "$MODE" = "http" ]; then
    echo "✅ Starting server in HTTP mode..."
    echo "   Server will be available at: http://0.0.0.0:8000/mcp"
    echo "   (Use Ctrl+C to stop)"
    echo ""
    python server_http.py
else
    echo "❌ Invalid mode: $MODE"
    echo "   Usage: ./start.sh [http|stdio]"
    exit 1
fi
