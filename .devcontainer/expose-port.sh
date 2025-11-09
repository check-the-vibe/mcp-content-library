#!/bin/bash

# Script to automatically expose port 8000 publicly in GitHub Codespaces
# This runs after the container is created

echo "🔧 Checking if running in GitHub Codespaces..."

# Check if we're in a Codespace (CODESPACE_NAME is set by GitHub)
if [ -z "$CODESPACE_NAME" ]; then
    echo "ℹ️  Not running in a GitHub Codespace, skipping port exposure."
    exit 0
fi

echo "✅ Running in GitHub Codespace: $CODESPACE_NAME"

# Wait a moment for the port to be forwarded
sleep 5

# Make port 8000 public
echo "🌐 Making port 8000 publicly accessible..."
gh codespace ports visibility 8000:public -c "$CODESPACE_NAME" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Port 8000 is now publicly accessible!"
    
    # Get the public URL
    PORT_URL=$(gh codespace ports -c "$CODESPACE_NAME" --json sourcePort,browseUrl -q '.[] | select(.sourcePort==8000) | .browseUrl')
    
    if [ -n "$PORT_URL" ]; then
        echo "🔗 Your public URL: $PORT_URL"
    fi
else
    echo "⚠️  Could not set port visibility. This may be due to permissions or the port not being forwarded yet."
    echo "ℹ️  You can manually set it public using: gh codespace ports visibility 8000:public"
fi
