#!/bin/bash
# Setup script for scholarinboxcli using uv
# This script creates a local virtual environment and installs scholarinboxcli

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SKILL_DIR/.venv"

echo "Setting up scholarinboxcli environment..."
echo "Skill directory: $SKILL_DIR"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: uv is not installed.${NC}"
    echo ""
    echo "Please install uv first:"
    echo "  macOS/Linux: brew install uv"
    echo "  macOS/Linux (alternative): curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  Windows: pip install uv"
    echo "  Windows (alternative): powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\""
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ uv found: $(uv --version)${NC}"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    uv venv "$VENV_DIR" --python ">=3.10"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists at $VENV_DIR${NC}"
fi
echo ""

# Install/upgrade scholarinboxcli
echo "Installing scholarinboxcli..."
uv pip install --python "$VENV_DIR/bin/python" --upgrade scholarinboxcli
echo -e "${GREEN}✓ scholarinboxcli installed${NC}"
echo ""

# Determine the correct binary path based on OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    # Windows
    CLI_PATH="$VENV_DIR/Scripts/scholarinboxcli.exe"
else
    # macOS/Linux
    CLI_PATH="$VENV_DIR/bin/scholarinboxcli"
fi

# Verify installation
if [ -f "$CLI_PATH" ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Setup complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "CLI binary location:"
    echo "  $CLI_PATH"
    echo ""
    echo "Version:"
    "$CLI_PATH" --version
    echo ""
    echo "Next steps:"
    echo "  1. Get your sha_key from https://www.scholar-inbox.com"
    echo "     (Open F12 → Network → find api/session_info → copy sha_key from response)"
    echo "  2. Authenticate: $CLI_PATH auth login --url 'https://www.scholar-inbox.com/login?sha_key=YOUR_KEY&date=MM-DD-YYYY'"
    echo "  3. Start using: $CLI_PATH trending --json"
    echo ""
else
    echo -e "${YELLOW}⚠️  Installation completed but binary not found at expected path.${NC}"
    echo "   You can try running: uv run --with scholarinboxcli scholarinboxcli --help"
fi
