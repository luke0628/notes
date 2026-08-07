#!/usr/bin/env bash
# ============================================================
# New Mac Work Setup — one-shot deployment
# Run on the NEW Mac:  bash setup.sh
# ============================================================
set -euo pipefail

CYAN='\033[0;36m'
GREEN='\033[0;32m'
NC='\033[0m'
section() { echo -e "\n${CYAN}==>${NC} ${GREEN}$*${NC}"; }

# ── 1. Homebrew ────────────────────────────────────────────
if ! command -v brew &>/dev/null; then
    section "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Apple Silicon path
    eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || true
else
    section "Homebrew already installed — updating..."
    brew update
fi

# ── 2. Brew formulae ───────────────────────────────────────
section "Installing brew formulae..."
brew install \
    docker \
    dotnet \
    fastfetch \
    ffmpeg \
    fmt \
    git \
    kind \
    merve \
    node \
    powershell \
    ripgrep \
    telnet \
    vgrep \
    wget

# ── 3. Brew casks ──────────────────────────────────────────
section "Installing brew casks..."
brew install --cask \
    copilot-cli \
    docker-desktop \
    ghostty \
    iterm2 \
    powershell@preview

# ── 4. Oh My Zsh ───────────────────────────────────────────
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    section "Installing Oh My Zsh..."
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi

section "Installing zsh plugins..."
ZSH_CUSTOM="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"
mkdir -p "$ZSH_CUSTOM/plugins"

if [ ! -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]; then
    git clone https://github.com/zsh-users/zsh-autosuggestions "$ZSH_CUSTOM/plugins/zsh-autosuggestions"
fi
if [ ! -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]; then
    git clone https://github.com/zsh-users/zsh-syntax-highlighting "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting"
fi

# ── 5. Deploy .zshrc ──────────────────────────────────────
section "Writing .zshrc..."
cat > "$HOME/.zshrc" <<'ZSHRC'
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="robbyrussell"

plugins=(
    git
    zsh-autosuggestions
    zsh-syntax-highlighting
)

source $ZSH/oh-my-zsh.sh

fastfetch --config examples/25

. "$HOME/.local/bin/env"

export PATH="$HOME/.local/bin:$PATH"
ZSHRC

# ── 6. Placeholder: env script ─────────────────────────────
section "Creating ~/.local/bin/env placeholder..."
mkdir -p "$HOME/.local/bin"
if [ ! -f "$HOME/.local/bin/env" ]; then
    cat > "$HOME/.local/bin/env" <<'ENV'
# ─── Your toolchain environment — customize me ───
# This was sourced from old Mac's ~/.local/bin/env
# Add your PATH exports, env vars, etc. here.
ENV
    echo "  ⚠️  ~/.local/bin/env created as placeholder — copy content from old Mac"
fi

# ── 7. Reminders ───────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅  Setup complete!"
echo ""
echo "  📋  Manual steps remaining:"
echo "  1. Copy ~/.gitconfig from old Mac"
echo "  2. Copy ~/.ssh/ from old Mac (keys + config)"
echo "  3. Fill in ~/.local/bin/env with old content"
echo "  4. Install JetBrainsMono Nerd Font (ghostty font)"
echo "  5. Install Hermes Agent (if needed)"
echo "  6. Sign in to Docker Desktop, GitHub Copilot, etc."
echo ""
echo "  🖥️  Reboot or restart terminal for full effect."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
