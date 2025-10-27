#!/bin/bash
# GitCLI Installation Script
# Installs GitCLI globally on macOS, Linux, and Windows (Git Bash)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/Adelodunpeter25/GitCLI.git"
INSTALL_DIR="$HOME/.gitcli"
BIN_DIR="$HOME/.local/bin"

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║         GitCLI Installation Script                     ║"
echo "║         Git Operations Automation                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running on supported OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Windows;;
    MINGW*)     MACHINE=Windows;;
    MSYS*)      MACHINE=Windows;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo -e "${CYAN}Detected OS: ${MACHINE}${NC}"

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed!${NC}"
    echo -e "${YELLOW}Please install Python 3.7 or higher and try again.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✅ Found Python ${PYTHON_VERSION}${NC}"

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 is not installed!${NC}"
    echo -e "${YELLOW}Please install pip3 and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found pip3${NC}"

# Check for git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed!${NC}"
    echo -e "${YELLOW}Please install Git and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found Git${NC}"
echo ""

# Ask installation method
echo -e "${CYAN}Choose installation method:${NC}"
echo "  1. Install from PyPI (recommended - latest stable)"
echo "  2. Install from GitHub (latest development version)"
echo ""
read -p "Enter choice (1 or 2): " INSTALL_METHOD </dev/tty

if [ "$INSTALL_METHOD" = "1" ]; then
    # Install from PyPI using pipx if available, otherwise pip
    echo -e "\n${CYAN}Installing GitCLI from PyPI...${NC}"
    
    if command -v pipx &> /dev/null; then
        echo -e "${GREEN}✅ Found pipx, using isolated installation${NC}"
        pipx install gitcli-automation --force
        echo -e "${GREEN}✅ GitCLI installed successfully with pipx!${NC}"
    else
        echo -e "${YELLOW}⚠️  pipx not found, using pip with --user flag${NC}"
        pip3 install --user gitcli-automation --upgrade
        echo -e "${GREEN}✅ GitCLI installed successfully with pip!${NC}"
        
        # Ensure ~/.local/bin is in PATH
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            echo -e "\n${YELLOW}⚠️  Adding ~/.local/bin to PATH${NC}"
            
            # Detect shell
            if [ -n "$BASH_VERSION" ]; then
                SHELL_RC="$HOME/.bashrc"
            elif [ -n "$ZSH_VERSION" ]; then
                SHELL_RC="$HOME/.zshrc"
            else
                SHELL_RC="$HOME/.profile"
            fi
            
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
            echo -e "${GREEN}✅ Added to $SHELL_RC${NC}"
            echo -e "${YELLOW}💡 Run: source $SHELL_RC${NC}"
            echo -e "${YELLOW}   Or restart your terminal${NC}"
        fi
    fi

elif [ "$INSTALL_METHOD" = "2" ]; then
    # Install from GitHub
    echo -e "\n${CYAN}Installing GitCLI from GitHub...${NC}"
    
    # Remove old installation if exists
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}⚠️  Removing old installation...${NC}"
        rm -rf "$INSTALL_DIR"
    fi
    
    # Clone repository
    echo -e "${CYAN}Cloning repository...${NC}"
    git clone "$REPO_URL" "$INSTALL_DIR"
    
    # Install
    cd "$INSTALL_DIR"
    
    if command -v pipx &> /dev/null; then
        echo -e "${GREEN}✅ Found pipx, using isolated installation${NC}"
        pipx install . --force
    else
        echo -e "${YELLOW}⚠️  pipx not found, using pip with --user flag${NC}"
        pip3 install --user -e .
        
        # Ensure ~/.local/bin is in PATH
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            echo -e "\n${YELLOW}⚠️  Adding ~/.local/bin to PATH${NC}"
            
            # Detect shell
            if [ -n "$BASH_VERSION" ]; then
                SHELL_RC="$HOME/.bashrc"
            elif [ -n "$ZSH_VERSION" ]; then
                SHELL_RC="$HOME/.zshrc"
            else
                SHELL_RC="$HOME/.profile"
            fi
            
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
            echo -e "${GREEN}✅ Added to $SHELL_RC${NC}"
            echo -e "${YELLOW}💡 Run: source $SHELL_RC${NC}"
            echo -e "${YELLOW}   Or restart your terminal${NC}"
        fi
    fi
    
    echo -e "${GREEN}✅ GitCLI installed successfully from GitHub!${NC}"
else
    echo -e "${RED}❌ Invalid choice!${NC}"
    exit 1
fi

# Verify installation
echo -e "\n${CYAN}Verifying installation...${NC}"
if command -v gitcli &> /dev/null; then
    VERSION=$(gitcli --version 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✅ GitCLI is installed and ready!${NC}"
    echo -e "${CYAN}Version: ${VERSION}${NC}"
else
    echo -e "${YELLOW}⚠️  GitCLI command not found in PATH${NC}"
    echo -e "${YELLOW}You may need to restart your terminal or run:${NC}"
    echo -e "${CYAN}  source ~/.bashrc${NC}  (or ~/.zshrc)"
fi

# Success message
echo -e "\n${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           Installation Complete! 🎉                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo -e "\n${CYAN}Quick Start:${NC}"
echo -e "  ${YELLOW}gitcli${NC}              - Start interactive mode"
echo -e "  ${YELLOW}gitcli save${NC}         - Stage, commit, and push"
echo -e "  ${YELLOW}gitcli config${NC}       - Configure settings"
echo -e "  ${YELLOW}gitcli help${NC}         - Show all commands"
echo -e "\n${CYAN}Documentation:${NC}"
echo -e "  ${YELLOW}https://github.com/Adelodunpeter25/GitCLI${NC}"
echo ""

# Offer to install pipx if not present
if ! command -v pipx &> /dev/null; then
    echo -e "${YELLOW}💡 Tip: Install pipx for better Python app management:${NC}"
    if [ "$MACHINE" = "Mac" ]; then
        echo -e "  ${CYAN}brew install pipx${NC}"
    else
        echo -e "  ${CYAN}python3 -m pip install --user pipx${NC}"
    fi
    echo ""
fi
