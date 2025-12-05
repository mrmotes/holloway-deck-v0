#!/usr/bin/env bash
set -euo pipefail
# install.sh - make wrappers executable and install symlinks to ~/.local/bin

# colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="$REPO_DIR/bin"
TARGET_DIR="$HOME/.local/bin"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${YELLOW}✦${RESET} ${GREEN}holloway-deck${RESET} ${YELLOW}✦${RESET}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

echo -e "${YELLOW}→${RESET} decentralizing infrastructure..."
chmod +x "$BIN_DIR"/* || true
echo -e "${GREEN}✓${RESET} command paths established"
echo ""

echo -e "${YELLOW}→${RESET} building from ${BLUE}$TARGET_DIR${RESET}"
mkdir -p "$TARGET_DIR"
echo -e "${GREEN}✓${RESET} source ready"
echo ""

echo -e "${YELLOW}→${RESET} wiring network..."
for f in "$BIN_DIR"/*; do
  cmd_name=$(basename "$f")
  ln -sf "$f" "$TARGET_DIR/$cmd_name"
  echo -e "  ${GREEN}✓${RESET} ${BLUE}$cmd_name${RESET} — connected"
done
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${GREEN}✓${RESET} your ${GREEN}holloway-deck${RESET} is ready"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
echo -e "ensure ${BLUE}$TARGET_DIR${RESET} is in your PATH to invoke commands freely:"
echo ""
echo -e "${YELLOW}if not yet configured:${RESET}"
echo -e "  ${BLUE}echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.profile${RESET}"
echo ""
echo -e "then activate the change:"
echo -e "  ${BLUE}source ~/.profile${RESET}"
echo ""
echo -e "evoke ${BLUE}draft${RESET} ${GREEN}to begin writing${RESET}"
