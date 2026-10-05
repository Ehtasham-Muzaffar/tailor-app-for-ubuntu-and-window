#!/usr/bin/env bash
# ============================================================
#  build_exe_wine.sh  –  Full automated Windows .exe builder
#  Run this on Ubuntu with Wine installed:
#    chmod +x build_exe_wine.sh
#    ./build_exe_wine.sh
# ============================================================
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WINE_PYTHON="$HOME/.wine/drive_c/Python311/python.exe"
WINE_PIP="$HOME/.wine/drive_c/Python311/Scripts/pip.exe"
WINE_PYINST="$HOME/.wine/drive_c/Python311/Scripts/pyinstaller.exe"
MSI_URL="https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.msi"
MSI_PATH="/tmp/python-3.11.9-amd64.msi"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Fazian Tailor Shop  –  Windows .exe Build  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
echo ""

# ── Step 1: Check Wine ─────────────────────────────────────
echo -e "${YELLOW}[1/5] Checking Wine...${NC}"
if ! command -v wine &>/dev/null; then
    echo -e "${RED}Wine not found! Install with: sudo apt install wine${NC}"
    exit 1
fi
echo "      Wine: $(wine --version)"

# ── Step 2: Download Python MSI ───────────────────────────
echo -e "${YELLOW}[2/5] Checking Python 3.11 Windows installer...${NC}"
if [ ! -f "$MSI_PATH" ]; then
    echo "      Downloading Python 3.11.9 for Windows (~25MB)..."
    wget -q --show-progress -O "$MSI_PATH" "$MSI_URL"
fi
echo "      Installer: $(du -h $MSI_PATH | cut -f1)"

# ── Step 3: Install Python in Wine ────────────────────────
echo -e "${YELLOW}[3/5] Installing Python inside Wine...${NC}"
if [ ! -f "$WINE_PYTHON" ]; then
    echo "      Running Python MSI installer in Wine (this takes ~2 min)..."
    WINEDEBUG=-all wine msiexec /i "$MSI_PATH" /quiet \
        TARGETDIR="C:\\Python311" \
        ADDLOCAL=ALL \
        PrependPath=1 2>/dev/null
    sleep 5
    if [ -f "$WINE_PYTHON" ]; then
        echo -e "      ${GREEN}✓ Python installed in Wine${NC}"
    else
        echo -e "      ${RED}✗ Python install may have failed – trying alternate path...${NC}"
        # Try default path
        ALT="$HOME/.wine/drive_c/users/$USER/AppData/Local/Programs/Python/Python311/python.exe"
        [ -f "$ALT" ] && WINE_PYTHON="$ALT" && echo "      Found at alternate path"
    fi
else
    echo "      Python already installed in Wine"
fi

WINE_PYTHON_VERSION=$(WINEDEBUG=-all wine "$WINE_PYTHON" --version 2>/dev/null || echo "unknown")
echo "      $WINE_PYTHON_VERSION"

# ── Step 4: Install packages inside Wine Python ───────────
echo -e "${YELLOW}[4/5] Installing packages in Wine Python...${NC}"

WINE_PIP_EXE="$HOME/.wine/drive_c/Python311/Scripts/pip.exe"

# Check if already installed
ALREADY=$(WINEDEBUG=-all wine "$WINE_PYTHON" -c "import customtkinter; print('ok')" 2>/dev/null || echo "no")
if [ "$ALREADY" != "ok" ]; then
    echo "      Installing customtkinter, pillow, pyinstaller..."
    WINEDEBUG=-all wine "$WINE_PYTHON" -m pip install --quiet --upgrade pip 2>/dev/null
    WINEDEBUG=-all wine "$WINE_PYTHON" -m pip install --quiet customtkinter pillow pyinstaller 2>/dev/null
    echo -e "      ${GREEN}✓ Packages installed${NC}"
else
    echo "      Packages already installed"
fi

# ── Step 5: Build .exe with PyInstaller ───────────────────
echo -e "${YELLOW}[5/5] Building Windows .exe with PyInstaller...${NC}"
echo "      This may take 3-5 minutes..."

# Clean previous builds
rm -rf "$PROJECT_DIR/dist" "$PROJECT_DIR/build"

# Run PyInstaller inside Wine
cd "$PROJECT_DIR"
WINEDEBUG=-all wine "$WINE_PYTHON" -m PyInstaller tailor_shop.spec --clean 2>&1

# ── Check result ──────────────────────────────────────────
EXE_PATH="$PROJECT_DIR/dist/FazianTailorShop/FazianTailorShop.exe"
if [ -f "$EXE_PATH" ]; then
    SIZE=$(du -sh "$PROJECT_DIR/dist/FazianTailorShop" | cut -f1)
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅  BUILD SUCCESSFUL!                        ║${NC}"
    echo -e "${GREEN}╠══════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║  EXE: dist/FazianTailorShop/FazianTailorShop.exe  ║${NC}"
    echo -e "${GREEN}║  Size: $SIZE                                  ║${NC}"
    echo -e "${GREEN}╠══════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║  Copy the entire dist/FazianTailorShop/      ║${NC}"
    echo -e "${GREEN}║  folder to the Windows PC.                   ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
else
    echo -e "${RED}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌  Build did not produce .exe file          ║${NC}"
    echo -e "${RED}║  Try Method B: build directly on Windows PC   ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════╝${NC}"
    exit 1
fi
