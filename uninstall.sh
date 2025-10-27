#!/bin/bash
# GitCLI Uninstallation Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║         GitCLI Uninstallation Script                   ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if GitCLI is installed
if ! command -v gitcli &> /dev/null; then
    echo -e "${YELLOW}⚠️  GitCLI is not installed or not in PATH${NC}"
    echo -e "${CYAN}Checking for local installations...${NC}"
fi

# Uninstall with pipx if available
if command -v pipx &> /dev/null; then
    if pipx list | grep -q "gitcli-automation"; then
        echo -e "${CYAN}Uninstalling GitCLI with pipx...${NC}"
        pipx uninstall gitcli-automation
        echo -e "${GREEN}✅ GitCLI uninstalled with pipx!${NC}"
    fi
fi

# Uninstall with pip
if pip3 list | grep -q "gitcli-automation"; then
    echo -e "${CYAN}Uninstalling GitCLI with pip...${NC}"
    pip3 uninstall -y gitcli-automation
    echo -e "${GREEN}✅ GitCLI uninstalled with pip!${NC}"
fi

# Remove local installation directory
INSTALL_DIR="$HOME/.gitcli"
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${CYAN}Removing local installation directory...${NC}"
    rm -rf "$INSTALL_DIR"
    echo -e "${GREEN}✅ Removed $INSTALL_DIR${NC}"
fi

# Remove config file
CONFIG_FILE=".gitcli-config.json"
if [ -f "$CONFIG_FILE" ]; then
    read -p "Remove configuration file? (y/N): " REMOVE_CONFIG
    if [ "$REMOVE_CONFIG" = "y" ] || [ "$REMOVE_CONFIG" = "Y" ]; then
        rm "$CONFIG_FILE"
        echo -e "${GREEN}✅ Removed configuration file${NC}"
    fi
fi

# Verify uninstallation
if command -v gitcli &> /dev/null; then
    echo -e "${YELLOW}⚠️  GitCLI command still found in PATH${NC}"
    echo -e "${YELLOW}You may need to restart your terminal${NC}"
else
    echo -e "${GREEN}✅ GitCLI has been completely uninstalled${NC}"
fi

echo -e "\n${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           Uninstallation Complete!                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
