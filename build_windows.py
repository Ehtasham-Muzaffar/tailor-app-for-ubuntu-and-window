#!/usr/bin/env python3
"""
build_windows.py
================
Cross-compilation helper: builds a Windows .exe from Ubuntu using Wine + PyInstaller.

OPTION A (Recommended) – Build directly ON a Windows machine:
    Copy the entire project folder to Windows, install Python 3.10/3.11,
    run:  pip install -r requirements.txt
          pyinstaller tailor_shop.spec

OPTION B – Build from Ubuntu via Wine (automated by this script):
    Requirements:
        sudo apt install wine winetricks
        # Install Python inside Wine:
        wine msiexec /i python-3.11.9-amd64.msi /quiet TargetDir="C:\\Python311"
        wine pip install customtkinter pillow pyinstaller

Usage on Ubuntu:
    python3 build_windows.py
"""

import subprocess
import sys
import os
import shutil

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR    = os.path.join(PROJECT_DIR, "dist")
BUILD_DIR   = os.path.join(PROJECT_DIR, "build")

WINE_PYTHON = "wine python"  # adjust if Wine Python is at a different path


def clean_prev():
    for d in [DIST_DIR, BUILD_DIR]:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"  Cleaned: {d}")


def build_native_linux():
    """Build a Linux binary (for testing on this machine)."""
    print("\n[BUILD] Building Linux binary for local testing…")
    cmd = [sys.executable, "-m", "PyInstaller", "tailor_shop.spec", "--clean"]
    subprocess.run(cmd, cwd=PROJECT_DIR, check=True)
    exe = os.path.join(DIST_DIR, "FazianTailorShop", "FazianTailorShop")
    if os.path.exists(exe):
        print(f"\n  ✅  Linux binary ready: {exe}")
    else:
        print("  ❌  Build may have failed – check output above.")


def build_wine_windows():
    """Build a Windows .exe using Wine (requires Wine + Python inside Wine)."""
    print("\n[BUILD] Building Windows .exe via Wine…")
    cmd = f'{WINE_PYTHON} -m PyInstaller tailor_shop.spec --clean'
    result = subprocess.run(cmd, shell=True, cwd=PROJECT_DIR)
    if result.returncode == 0:
        exe = os.path.join(DIST_DIR, "FazianTailorShop", "FazianTailorShop.exe")
        print(f"\n  ✅  Windows .exe ready: {exe}")
    else:
        print("  ❌  Wine build failed. See README for manual Windows build instructions.")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "linux"
    clean_prev()
    if mode == "wine":
        build_wine_windows()
    else:
        build_native_linux()
