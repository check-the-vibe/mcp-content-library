#!/bin/bash
# Setup script for Claude CLI integration

set -e

echo "🔧 Setting up Claude CLI for MCP Content Library"
echo ""

# Check if Claude CLI is installed
if ! command -v claude &> /dev/null; then
    echo "⚠️  Claude CLI not found!"
    echo ""
    echo "To install Claude CLI:"
    echo "  npm install -g @anthropic-ai/claude-cli"
    echo "  # or"
    echo "  pip install claude-cli"
    echo ""
    read -p "Do you want to continue anyway and just create the config? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📁 Creating local Claude config (.claude/mcp_config.json)..."
mkdir -p .claude
cat > .claude/mcp_config.json << 'EOF'
{
  "mcpServers": {
    "content-library": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
EOF
echo "✅ Local config created!"

echo ""
echo "Would you like to also set up global Claude CLI config?"
echo "(This will allow you to use the content library from any directory)"
echo ""
read -p "Set up global config? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Choose configuration type:"
    echo "1) Local server (http://localhost:8000/mcp)"
    echo "2) GitHub Codespaces public URL"
    echo ""
    read -p "Enter choice (1 or 2): " -n 1 -r
    echo

    if [[ $REPLY == "1" ]]; then
        CONFIG_URL="http://localhost:8000/mcp"
    elif [[ $REPLY == "2" ]]; then
        if [ -n "$CODESPACE_NAME" ]; then
            CONFIG_URL="https://${CODESPACE_NAME}-8000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}/mcp"
            echo "📍 Detected Codespaces URL: $CONFIG_URL"
        else
            echo "⚠️  Not running in Codespaces. Using localhost instead."
            CONFIG_URL="http://localhost:8000/mcp"
        fi
    else
        echo "Invalid choice. Using localhost."
        CONFIG_URL="http://localhost:8000/mcp"
    fi

    echo ""
    echo "📁 Creating global config at ~/.config/claude/mcp_config.json..."
    mkdir -p ~/.config/claude

    # Check if file exists and backup
    if [ -f ~/.config/claude/mcp_config.json ]; then
        echo "⚠️  Existing config found. Creating backup..."
        cp ~/.config/claude/mcp_config.json ~/.config/claude/mcp_config.json.backup
        echo "✅ Backup created: ~/.config/claude/mcp_config.json.backup"

        # Merge configs (simple approach - add our server)
        echo "Merging with existing config..."
        python3 << EOF
import json
with open('$HOME/.config/claude/mcp_config.json', 'r') as f:
    config = json.load(f)
if 'mcpServers' not in config:
    config['mcpServers'] = {}
config['mcpServers']['content-library'] = {
    'type': 'http',
    'url': '$CONFIG_URL'
}
with open('$HOME/.config/claude/mcp_config.json', 'w') as f:
    json.dump(config, f, indent=2)
print('✅ Config merged successfully!')
EOF
    else
        # Create new config
        cat > ~/.config/claude/mcp_config.json << EOF
{
  "mcpServers": {
    "content-library": {
      "type": "http",
      "url": "$CONFIG_URL"
    }
  }
}
EOF
        echo "✅ Global config created!"
    fi
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start the MCP server:"
echo "   ./start.sh"
echo ""
echo "2. In another terminal, use Claude CLI:"
echo ""
echo "   # Using local config (project-specific):"
echo "   export CLAUDE_MCP_CONFIG=.claude/mcp_config.json"
echo "   claude chat"
echo ""
echo "   # Or if you set up global config:"
echo "   claude chat"
echo ""
echo "3. Verify it's working:"
echo "   claude mcp list-servers"
echo "   claude mcp list-tools content-library"
echo ""
echo "📖 See README.md for more usage examples!"
