#!/bin/bash
# Setup script for Scholar Inbox Python API using uv
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

echo "Setting up Scholar Inbox Python API environment..."
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

# Install scholarinboxcli (the base package)
echo "Installing scholarinboxcli..."
uv pip install --python "$VENV_DIR/bin/python" scholarinboxcli
echo -e "${GREEN}✓ scholarinboxcli installed${NC}"
echo ""

# Verify installation
PYTHON_PATH="$VENV_DIR/bin/python"
if [ -f "$PYTHON_PATH" ]; then
    # Test import
    if $PYTHON_PATH -c "from scholar_inbox_api import MyScholarInboxClient; print('OK')" 2>/dev/null; then
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}Setup complete!${NC}"
        echo -e "${GREEN}========================================${NC}"
    else
        echo -e "${YELLOW}Warning: Could not import MyScholarInboxClient${NC}"
        echo "  (This is normal if you're running from the skill directory)"
    fi
    echo ""
    echo "Python location:"
    echo "  $PYTHON_PATH"
    echo ""
    echo "To use the Python API:"
    echo "  export PYTHONPATH=\"$SKILL_DIR:\$PYTHONPATH\""
    echo "  $PYTHON_PATH -c \"from scholar_inbox_api import MyScholarInboxClient; print('OK')\""
    echo ""
    echo "To run the CLI interface:"
    echo "  $PYTHON_PATH $SKILL_DIR/scholar_inbox_api.py --help"
    echo ""
    echo "Next steps:"
    echo "  1. Get your sha_key from https://www.scholar-inbox.com"
    echo "     (Open F12 → Network → find api/session_info → copy sha_key from response)"
    echo "  2. Set environment variable: export SCHOLAR_INBOX_SHA_KEY=YOUR_KEY"
    echo "  3. Test: $PYTHON_PATH $SKILL_DIR/scholar_inbox_api.py status"
    echo ""
else
    echo -e "${YELLOW}⚠️  Installation completed but Python not found at expected path.${NC}"
    echo "   You can try: uv run python --version"
fi
