#!/usr/bin/env bash
# install_and_build.sh
# Run AFTER pip is confirmed installed in Wine Python
WINE_PY="$HOME/.wine/drive_c/Python311/python.exe"
PROJECT="/home/shami/Desktop/fazian tailor"

echo "=== Installing packages ==="
WINEDEBUG=-all wine "$WINE_PY" -m pip install --quiet customtkinter pillow pyinstaller 2>&1 | grep -v "^fixme\|WARN"

echo "=== Verifying ==="
WINEDEBUG=-all wine "$WINE_PY" -c "import customtkinter; import PIL; import PyInstaller; print('All packages OK')" 2>&1

echo "=== Building .exe ==="
cd "$PROJECT"
rm -rf dist build
WINEDEBUG=-all wine "$WINE_PY" -m PyInstaller tailor_shop.spec --clean 2>&1

echo "=== Result ==="
ls -lh "$PROJECT/dist/FazianTailorShop/FazianTailorShop.exe" 2>/dev/null && echo "SUCCESS" || echo "FAILED"
