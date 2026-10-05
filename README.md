# ✂ Fazian Tailor Shop — Desktop Management System

A fully **offline** tailor shop management desktop app built with Python + CustomTkinter + SQLite.

## Quick Start (Ubuntu)

```bash
pip install -r requirements.txt
python3 main.py
```

## Build for Windows

```bash
# On Windows — copy project folder, then:
pip install -r requirements.txt
pyinstaller tailor_shop.spec --clean
# Output: dist\FazianTailorShop\FazianTailorShop.exe
```

## Features

- 🔍 Customer search by phone or name
- 📐 Full measurement form (10 fields)
- 📋 Order management with status tracking
- 💰 Financial tracking (total / advance / balance)
- 🧾 Order receipt generator (save as PDF)
- 💾 One-click database backup to USB/folder
- 🔄 Restore from backup
- 📵 100% offline — no internet required

## Tech Stack

- **UI**: Python 3.11 + CustomTkinter
- **Database**: SQLite (tailor_shop.db)
- **Packaging**: PyInstaller
- **Compatibility**: Windows 7 / 10 / 11

## Database Location

`tailor_shop.db` is stored alongside the executable.
Back it up regularly via **Settings → Backup Now**.
