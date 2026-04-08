#!/bin/bash
# Setup script for Scholar Inbox Skill
# Installs scholarinboxcli from the fork repo (zhjcreator/scholarinboxcli)

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SKILL_DIR/.venv"

echo "Setting up Scholar Inbox Skill environment..."
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

# Install scholarinboxcli from fork repo (includes rate + sha-key login features)
FORK_URL="git+https://github.com/zhjcreator/scholarinboxcli.git"
echo "Installing scholarinboxcli from fork: $FORK_URL"
uv pip install --python "$VENV_DIR/bin/python" "$FORK_URL"
echo -e "${GREEN}✓ scholarinboxcli installed${NC}"
echo ""

# Verify installation
PYTHON_PATH="$VENV_DIR/bin/python"
CLI_PATH="$VENV_DIR/bin/scholarinboxcli"

if [ -f "$CLI_PATH" ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Setup complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "CLI location: $CLI_PATH"
    echo ""
    echo "Next steps:"
    echo "  1. Get your sha_key from https://www.scholar-inbox.com"
    echo "     (Open F12 → Network → find api/session_info → copy sha_key from response)"
    echo "  2. Login:"
    echo "     $CLI_PATH auth login --sha-key YOUR_SHA_KEY"
    echo "  3. Test:"
    echo "     $CLI_PATH papers digest"
    echo ""
else
    echo -e "${YELLOW}⚠️  Installation completed but CLI not found at expected path.${NC}"
    echo "   Try: uv run scholarinboxcli --help"
fi
