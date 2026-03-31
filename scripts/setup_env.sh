#!/usr/bin/env bash
# setup_env.sh — Install scholarinboxcli using uv into an isolated environment
#
# Usage: bash setup_env.sh
#
# Prerequisites: uv must be installed
#   macOS/Linux: brew install uv  OR  curl -LsSf https://astral.sh/uv/install.sh | sh
#   Windows:     pip install uv  OR  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
#
# After running this script, use the printed binary path to execute scholarinboxcli commands.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_DIR="${SKILL_DIR}/.venv"

echo "🔧 Setting up Scholar Inbox CLI environment..."
echo "   Environment directory: ${ENV_DIR}"

# --- Check uv is available ---
if ! command -v uv &>/dev/null; then
    echo "❌ 'uv' is not installed."
    echo "   Install it with: brew install uv"
    echo "   Or: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "   Found uv: $(uv --version)"

# --- Create virtual environment if it doesn't exist ---
if [ ! -d "${ENV_DIR}" ]; then
    echo "   Creating virtual environment with uv (Python >=3.10)..."
    uv venv "${ENV_DIR}" --python ">=3.10"
else
    echo "   Virtual environment already exists, skipping creation."
fi

# --- Determine platform-specific paths ---
OS="$(uname -s)"
if [ "${OS}" = "Darwin" ] || [ "${OS}" = "Linux" ]; then
    BIN_DIR="${ENV_DIR}/bin"
    PYTHON="${ENV_DIR}/bin/python"
elif [ "${OS:0:5}" = "MINGW" ] || [ "${OS:0:6}" = "MSYS_NT" ] || [ "${OS}" = "Windows_NT" ]; then
    BIN_DIR="${ENV_DIR}/Scripts"
    PYTHON="${ENV_DIR}/Scripts/python.exe"
else
    echo "⚠️  Unknown OS '${OS}', assuming POSIX..."
    BIN_DIR="${ENV_DIR}/bin"
    PYTHON="${ENV_DIR}/bin/python"
fi

# --- Install or upgrade scholarinboxcli ---
echo "   Installing scholarinboxcli..."
uv pip install --python "${PYTHON}" --upgrade scholarinboxcli

# --- Verify installation ---
CLI="${BIN_DIR}/scholarinboxcli"
if [ -f "${CLI}" ] || [ -f "${CLI}.exe" ]; then
    VERSION=$("${CLI}" --version 2>/dev/null || echo "unknown")
    echo ""
    echo "✅ scholarinboxcli installed successfully! (version: ${VERSION})"
    echo ""
    echo "   Binary path: ${CLI}"
    echo ""
    echo "   Quick start:"
    echo "   ${CLI} auth login --url \"https://www.scholar-inbox.com/login?sha_key=YOUR_KEY&date=MM-DD-YYYY\""
    echo "   ${CLI} auth status"
    echo "   ${CLI} digest --json"
else
    echo ""
    echo "⚠️  Installation completed but binary not found at expected path."
    echo "   Try: uv run --with scholarinboxcli scholarinboxcli --help"
fi
