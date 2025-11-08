#!/bin/bash
# Install systemd service for MCP Content Library

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  MCP Content Library - Systemd Installation  ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Running as root. This will install for the current user.${NC}"
    echo ""
fi

# Get the current user
INSTALL_USER="${SUDO_USER:-$USER}"
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="mcp-content-library@.service"

echo -e "${YELLOW}Installation Details:${NC}"
echo "  User:            $INSTALL_USER"
echo "  Working Dir:     $CURRENT_DIR"
echo "  Service File:    $SERVICE_FILE"
echo ""

# Check if virtual environment exists
if [ ! -d "$CURRENT_DIR/.venv" ]; then
    echo -e "${RED}✗ Virtual environment not found!${NC}"
    echo ""
    echo "Please run bootstrap first:"
    echo "  ./bootstrap.sh"
    exit 1
fi

# Check if service file exists
if [ ! -f "$CURRENT_DIR/$SERVICE_FILE" ]; then
    echo -e "${RED}✗ Service file not found: $SERVICE_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}[1/4]${NC} Updating service file with current paths..."

# Create a temporary service file with the actual paths
TEMP_SERVICE="/tmp/mcp-content-library@.service.tmp"
sed "s|/home/%i/mcp-content-library|$CURRENT_DIR|g" "$CURRENT_DIR/$SERVICE_FILE" > "$TEMP_SERVICE"

echo -e "${GREEN}✓ Service file prepared${NC}"

echo ""
echo -e "${YELLOW}[2/4]${NC} Installing systemd service..."

# Copy service file to systemd directory
if [ "$EUID" -eq 0 ]; then
    cp "$TEMP_SERVICE" "/etc/systemd/system/$SERVICE_FILE"
else
    sudo cp "$TEMP_SERVICE" "/etc/systemd/system/$SERVICE_FILE"
fi

rm "$TEMP_SERVICE"
echo -e "${GREEN}✓ Service file installed${NC}"

echo ""
echo -e "${YELLOW}[3/4]${NC} Reloading systemd daemon..."
if [ "$EUID" -eq 0 ]; then
    systemctl daemon-reload
else
    sudo systemctl daemon-reload
fi
echo -e "${GREEN}✓ Systemd reloaded${NC}"

echo ""
echo -e "${YELLOW}[4/4]${NC} Enabling and starting service..."

SERVICE_NAME="mcp-content-library@${INSTALL_USER}.service"

if [ "$EUID" -eq 0 ]; then
    systemctl enable "$SERVICE_NAME"
    systemctl start "$SERVICE_NAME"
else
    sudo systemctl enable "$SERVICE_NAME"
    sudo systemctl start "$SERVICE_NAME"
fi

echo -e "${GREEN}✓ Service enabled and started${NC}"

# Wait a moment for service to start
sleep 2

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Installation Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""

# Check service status
echo -e "${BLUE}Service Status:${NC}"
if [ "$EUID" -eq 0 ]; then
    systemctl status "$SERVICE_NAME" --no-pager || true
else
    sudo systemctl status "$SERVICE_NAME" --no-pager || true
fi

echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo ""
echo "  Check status:"
echo "    ${YELLOW}sudo systemctl status $SERVICE_NAME${NC}"
echo ""
echo "  View logs:"
echo "    ${YELLOW}sudo journalctl -u $SERVICE_NAME -f${NC}"
echo "    ${YELLOW}sudo tail -f /var/log/mcp-content-library.log${NC}"
echo ""
echo "  Stop service:"
echo "    ${YELLOW}sudo systemctl stop $SERVICE_NAME${NC}"
echo ""
echo "  Restart service:"
echo "    ${YELLOW}sudo systemctl restart $SERVICE_NAME${NC}"
echo ""
echo "  Disable auto-start:"
echo "    ${YELLOW}sudo systemctl disable $SERVICE_NAME${NC}"
echo ""
echo "  Uninstall:"
echo "    ${YELLOW}sudo systemctl stop $SERVICE_NAME${NC}"
echo "    ${YELLOW}sudo systemctl disable $SERVICE_NAME${NC}"
echo "    ${YELLOW}sudo rm /etc/systemd/system/$SERVICE_FILE${NC}"
echo "    ${YELLOW}sudo systemctl daemon-reload${NC}"
echo ""

echo -e "${GREEN}Server should now be running at: http://localhost:8000/${NC}"
echo ""
