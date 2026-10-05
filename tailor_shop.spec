# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Fazian Tailor Shop
# Run: pyinstaller tailor_shop.spec

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

ctk_data = collect_data_files('customtkinter', includes=['**/*.json', '**/*.png'])
icon_data = [('assets/icon.png', 'assets')]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=ctk_data + icon_data,
    hiddenimports=[
        'customtkinter',
        'PIL._tkinter_finder',
        'PIL.ImageTk',
        'database.db_manager',
        'ui.theme',
        'ui.widgets',
        'ui.dialogs',
        'ui.pages.dashboard',
        'ui.pages.customer_profile',
        'ui.pages.all_orders',
        'ui.pages.settings',
        'sqlite3',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'darkdetect',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy', 'pandas', 'matplotlib', 'scipy'],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FazianTailorShop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FazianTailorShop',
)
