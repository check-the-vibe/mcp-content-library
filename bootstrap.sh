#!/bin/bash
# Unified bootstrap script for MCP Content Library
# Sets up everything needed to run the server

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
NON_INTERACTIVE=false
SKIP_CLI_INSTALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --non-interactive|-n)
            NON_INTERACTIVE=true
            shift
            ;;
        --skip-cli)
            SKIP_CLI_INSTALL=true
            shift
            ;;
        --help|-h)
            echo "MCP Content Library Bootstrap Script"
            echo ""
            echo "Usage: ./bootstrap.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --non-interactive, -n   Run without prompts (for CI/automation)"
            echo "  --skip-cli             Skip Claude CLI installation"
            echo "  --help, -h             Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Run './bootstrap.sh --help' for usage"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   MCP Content Library Bootstrap Setup     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Check Python version
echo -e "${YELLOW}[1/8]${NC} Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found!${NC}"
    echo "Please install Python 3.11 or later"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Found Python $PYTHON_VERSION${NC}"

# Step 2: Setup virtual environment
echo ""
echo -e "${YELLOW}[2/8]${NC} Setting up Python virtual environment..."
if [ -d ".venv" ]; then
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
else
    echo "  Creating .venv..."
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "  Activating virtual environment..."
source .venv/bin/activate

# Step 3: Install Python dependencies
echo ""
echo -e "${YELLOW}[3/8]${NC} Installing Python dependencies..."
echo "  This may take a minute..."
pip install -q --upgrade pip
pip install -q -e .
pip install -q -r requirements.txt

if python -c "import mcp" 2>/dev/null; then
    echo -e "${GREEN}✓ All Python dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi

# Step 4: Create storage directory
echo ""
echo -e "${YELLOW}[4/8]${NC} Setting up storage directory..."
STORAGE_DIR="${MCP_SNIPPETS_ROOT:-$HOME/.mcp_snippets}"
mkdir -p "$STORAGE_DIR"
echo -e "${GREEN}✓ Storage directory: $STORAGE_DIR${NC}"

# Step 5: Install Claude CLI
echo ""
echo -e "${YELLOW}[5/8]${NC} Setting up Claude CLI..."
if [ "$SKIP_CLI_INSTALL" = true ]; then
    echo "  Skipped (--skip-cli flag)"
elif command -v claude &> /dev/null; then
    CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✓ Claude CLI already installed ($CLAUDE_VERSION)${NC}"
else
    echo "  Claude CLI not found. Attempting installation..."
    
    # Try npm first (preferred method)
    if command -v npm &> /dev/null; then
        echo "  Installing via npm..."
        if npm install -g @anthropic-ai/claude-cli 2>&1 | grep -q "permission denied"; then
            echo -e "${YELLOW}  ⚠ npm needs sudo. Trying with sudo...${NC}"
            sudo npm install -g @anthropic-ai/claude-cli 2>/dev/null || true
        else
            npm install -g @anthropic-ai/claude-cli 2>/dev/null || true
        fi
    fi
    
    # Fallback to pip if npm failed
    if ! command -v claude &> /dev/null; then
        echo "  Trying pip installation..."
        pip install -q claude-cli 2>/dev/null || true
    fi
    
    # Check if installation succeeded
    if command -v claude &> /dev/null; then
        echo -e "${GREEN}✓ Claude CLI installed successfully${NC}"
    else
        echo -e "${YELLOW}  ⚠ Could not auto-install Claude CLI${NC}"
        echo ""
        echo "  To install manually, run one of:"
        echo "    npm install -g @anthropic-ai/claude-cli"
        echo "    pip install claude-cli"
        echo ""
    fi
fi

# Step 6: Configure Claude CLI for MCP
echo ""
echo -e "${YELLOW}[6/8]${NC} Configuring Claude CLI MCP connection..."
if [ "$NON_INTERACTIVE" = true ]; then
    # Non-interactive: just create local config
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
    echo -e "${GREEN}✓ Local Claude config created (.claude/mcp_config.json)${NC}"
else
    # Interactive: run the setup script
    if [ -f "setup-claude-cli.sh" ]; then
        bash setup-claude-cli.sh
    else
        # Fallback: create basic config
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
        echo -e "${GREEN}✓ Local Claude config created (.claude/mcp_config.json)${NC}"
    fi
fi

# Step 7: Display other CLI installation instructions
echo ""
echo -e "${YELLOW}[7/8]${NC} Additional AI CLI tools..."
echo ""
echo -e "${BLUE}📦 OpenAI Codex:${NC}"
echo "   Installation: pip install openai"
echo "   Setup: export OPENAI_API_KEY='your-key-here'"
echo "   Docs: https://platform.openai.com/docs/guides/code"
echo ""
echo -e "${BLUE}📦 Qwen2.5-Coder (OpenCode):${NC}"
echo "   Installation: pip install transformers torch"
echo "   Docs: https://github.com/QwenLM/Qwen2.5-Coder"
echo ""

# Step 8: Final summary and next steps
echo ""
echo -e "${YELLOW}[8/8]${NC} Bootstrap complete!"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo "  1️⃣  Start the MCP server:"
echo "     ${YELLOW}./start.sh${NC}"
echo ""
echo "  2️⃣  Or run directly:"
echo "     ${YELLOW}source .venv/bin/activate && python server_http.py${NC}"
echo ""
echo "  3️⃣  Access the server:"
echo "     • Web UI:        http://localhost:8000/"
echo "     • MCP Endpoint:  http://localhost:8000/mcp"
echo "     • Health Check:  http://localhost:8000/health"
echo ""
echo "  4️⃣  Use with Claude CLI:"
echo "     ${YELLOW}export CLAUDE_MCP_CONFIG=.claude/mcp_config.json${NC}"
echo "     ${YELLOW}claude chat${NC}"
echo ""
echo "  5️⃣  Get public URL (if in Codespaces):"
echo "     ${YELLOW}./get-public-url.sh${NC}"
echo ""

if [ "$NON_INTERACTIVE" = false ]; then
    echo -e "${BLUE}Would you like to start the server now?${NC}"
    read -p "Start server? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${GREEN}Starting server...${NC}"
        ./start.sh
    fi
else
    echo -e "${BLUE}💡 Running in non-interactive mode. Start server with: ./start.sh${NC}"
fi

echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
