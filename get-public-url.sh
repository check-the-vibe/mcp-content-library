#!/bin/bash
# Get the public URL for the MCP server in GitHub Codespaces

echo "🔍 Finding public URL for MCP server..."
echo ""

# Check if we're in Codespaces
if [ -n "$CODESPACE_NAME" ]; then
    # We're in Codespaces
    CODESPACE_URL="https://${CODESPACE_NAME}-8000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    MCP_ENDPOINT="${CODESPACE_URL}/mcp"

    echo "✅ GitHub Codespaces detected!"
    echo ""
    echo "📍 Public URL: $CODESPACE_URL"
    echo "🔌 MCP Endpoint: $MCP_ENDPOINT"
    echo ""
    echo "📋 Add this to your MCP client configuration:"
    echo ""
    echo '{'
    echo '  "servers": {'
    echo '    "contentLibrary": {'
    echo '      "type": "http",'
    echo "      \"url\": \"$MCP_ENDPOINT\""
    echo '    }'
    echo '  }'
    echo '}'
    echo ""
    echo "⚠️  Note: Make sure port 8000 is set to 'Public' visibility in the Ports panel"
    echo "   (View → Ports → right-click port 8000 → Port Visibility → Public)"

elif [ -n "$GITPOD_WORKSPACE_URL" ]; then
    # We're in Gitpod
    WORKSPACE_URL=$(echo $GITPOD_WORKSPACE_URL | sed 's/https:\/\///')
    PUBLIC_URL="https://8000-${WORKSPACE_URL}"
    MCP_ENDPOINT="${PUBLIC_URL}/mcp"

    echo "✅ Gitpod detected!"
    echo ""
    echo "📍 Public URL: $PUBLIC_URL"
    echo "🔌 MCP Endpoint: $MCP_ENDPOINT"

else
    # Local or other environment
    echo "📍 Local/Unknown environment detected"
    echo ""
    echo "🔌 Local endpoint: http://localhost:8000/mcp"
    echo ""
    echo "💡 For external access, you'll need to:"
    echo "   1. Ensure the server is accessible from outside (firewall, etc.)"
    echo "   2. Use your machine's public IP or domain name"
    echo "   3. Example: http://your-ip-or-domain:8000/mcp"
fi

echo ""
echo "🚀 To start the server, run:"
echo "   python server_http.py"
echo ""
echo "   Or use the convenience script:"
echo "   ./start.sh"
