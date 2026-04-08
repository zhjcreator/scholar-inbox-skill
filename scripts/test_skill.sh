#!/usr/bin/env bash
# Quick sanity check: verify scholarinboxcli is installed and auth works
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VENV_CLI="$SKILL_DIR/.venv/bin/scholarinboxcli"

# Use venv CLI if available, otherwise fall back to system PATH
if [ -f "$VENV_CLI" ]; then
    CLI="$VENV_CLI"
else
    CLI="scholarinboxcli"
fi

echo "=== Scholar Inbox Skill — Verification ==="
echo ""

# 1. CLI is accessible
if ! command -v "$CLI" &>/dev/null 2>&1 && [ ! -f "$CLI" ]; then
    echo "❌ scholarinboxcli not found. Run ./scripts/setup_env.sh first."
    exit 1
fi
echo "✓ CLI found: $CLI"

# 2. Show version / basic help
echo ""
echo "--- CLI help ---"
"$CLI" --help
echo ""

# 3. Auth status
echo "--- Auth status ---"
"$CLI" auth status || true
echo ""

echo "=== Verification complete ==="
echo ""
echo "If not logged in, run:"
echo "  $CLI auth login --sha-key YOUR_SHA_KEY"
