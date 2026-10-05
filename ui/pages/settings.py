"""
ui/pages/settings.py  –  Settings & Backup page
"""
import customtkinter as ctk
import os, shutil
from tkinter import filedialog, messagebox
from ui.theme import *
from ui.widgets import HSep, SectionHeader
from database import db_manager as db


class SettingsPage(ctk.CTkFrame):

    def __init__(self, master, nav_callback, **kw):
        super().__init__(master, fg_color=CLR_BG, **kw)
        self.nav_callback = nav_callback
        self._build_ui()

    def _build_ui(self):
        toolbar = ctk.CTkFrame(self, fg_color=CLR_SURFACE,
                               corner_radius=0, height=54)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)
        ctk.CTkLabel(toolbar, text="⚙  Settings & Backup",
                     font=FONT_HEADING, text_color=CLR_TEXT
                     ).pack(side="left", padx=PAD*2)

        HSep(self).pack(fill="x")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=PAD*2, pady=PAD)

        # ── Database Info ──────────────────────────────────────────────
        SectionHeader(scroll, "🗄  Database").pack(anchor="w", pady=(0, PAD_S))
        db_card = ctk.CTkFrame(scroll, fg_color=CLR_SURFACE,
                                corner_radius=RAD, border_width=1,
                                border_color=CLR_BORDER)
        db_card.pack(fill="x", pady=(0, PAD))

        db_size = os.path.getsize(db.DB_PATH) / 1024 if os.path.exists(db.DB_PATH) else 0
        ctk.CTkLabel(db_card, text=f"📁  Location: {db.DB_PATH}",
                     font=FONT_BODY, text_color=CLR_TEXT_MUTED, anchor="w"
                     ).pack(fill="x", padx=PAD, pady=(PAD, 0))
        ctk.CTkLabel(db_card, text=f"💾  Size: {db_size:.1f} KB",
                     font=FONT_BODY, text_color=CLR_TEXT_MUTED, anchor="w"
                     ).pack(fill="x", padx=PAD, pady=(0, PAD))

        # ── Backup ────────────────────────────────────────────────────
        HSep(scroll).pack(fill="x", pady=PAD)
        SectionHeader(scroll, "🔒  Backup & Export").pack(anchor="w", pady=(0, PAD_S))

        bak_card = ctk.CTkFrame(scroll, fg_color=CLR_SURFACE,
                                corner_radius=RAD, border_width=1,
                                border_color=CLR_BORDER)
        bak_card.pack(fill="x", pady=(0, PAD))

        ctk.CTkLabel(bak_card,
                     text="Save a copy of your database (.db file) to any location\n"
                          "(USB drive, Google Drive folder, etc.)",
                     font=FONT_BODY, text_color=CLR_TEXT_MUTED, justify="left"
                     ).pack(anchor="w", padx=PAD, pady=PAD)

        btn_row = ctk.CTkFrame(bak_card, fg_color="transparent")
        btn_row.pack(anchor="w", padx=PAD, pady=(0, PAD))

        ctk.CTkButton(btn_row, text="📦  Backup Now", width=180, height=38,
                      fg_color=CLR_SUCCESS, hover_color="#16a34a",
                      font=FONT_BODY, text_color="#0f1117",
                      command=self._backup
                      ).pack(side="left", padx=(0, PAD))

        ctk.CTkButton(btn_row, text="📂  Open DB Folder", width=180, height=38,
                      fg_color=CLR_SURFACE2, hover_color=CLR_BORDER,
                      font=FONT_BODY, text_color=CLR_TEXT_MUTED,
                      command=self._open_db_folder
                      ).pack(side="left")

        # ── Restore ───────────────────────────────────────────────────
        HSep(scroll).pack(fill="x", pady=PAD)
        SectionHeader(scroll, "🔄  Restore from Backup").pack(anchor="w", pady=(0, PAD_S))

        rst_card = ctk.CTkFrame(scroll, fg_color=CLR_SURFACE,
                                corner_radius=RAD, border_width=1,
                                border_color=CLR_BORDER)
        rst_card.pack(fill="x", pady=(0, PAD))

        ctk.CTkLabel(rst_card,
                     text="⚠  WARNING: This will replace your current database with the backup file.",
                     font=FONT_BODY, text_color=CLR_WARNING, justify="left"
                     ).pack(anchor="w", padx=PAD, pady=PAD)

        ctk.CTkButton(rst_card, text="🔄  Restore Backup", width=180, height=38,
                      fg_color="#3d2400", hover_color=CLR_WARNING,
                      text_color=CLR_WARNING,
                      font=FONT_BODY,
                      command=self._restore
                      ).pack(anchor="w", padx=PAD, pady=(0, PAD))

        # ── About ─────────────────────────────────────────────────────
        HSep(scroll).pack(fill="x", pady=PAD)
        about_card = ctk.CTkFrame(scroll, fg_color=CLR_SURFACE,
                                   corner_radius=RAD, border_width=1,
                                   border_color=CLR_BORDER)
        about_card.pack(fill="x")
        ctk.CTkLabel(about_card, text="✂  Fazian Tailor Shop  –  v1.0.0",
                     font=FONT_HEADING, text_color=CLR_PRIMARY
                     ).pack(padx=PAD, pady=(PAD, 0))
        ctk.CTkLabel(about_card,
                     text="A fully offline tailor management system.\n"
                          "Built with Python + CustomTkinter + SQLite.",
                     font=FONT_BODY, text_color=CLR_TEXT_MUTED
                     ).pack(padx=PAD, pady=(0, PAD))

    def _backup(self):
        folder = filedialog.askdirectory(title="Select backup destination folder")
        if not folder:
            return
        try:
            dst = db.backup_database(folder)
            messagebox.showinfo("Backup Successful",
                                f"Database backed up to:\n{dst}", parent=self)
        except Exception as e:
            messagebox.showerror("Backup Failed", str(e), parent=self)

    def _open_db_folder(self):
        folder = os.path.dirname(db.DB_PATH)
        try:
            import subprocess
            subprocess.Popen(["xdg-open", folder])  # Linux
        except Exception:
            try:
                os.startfile(folder)                 # Windows fallback
            except Exception:
                pass

    def _restore(self):
        src = filedialog.askopenfilename(
            title="Select backup .db file",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if not src:
            return
        if not messagebox.askyesno(
                "Confirm Restore",
                "This will OVERWRITE the current database.\n"
                "All current data will be replaced with the backup.\n\n"
                "Are you sure?",
                parent=self):
            return
        try:
            shutil.copy2(src, db.DB_PATH)
            messagebox.showinfo("Restore Successful",
                                "Database restored. Please restart the app.", parent=self)
        except Exception as e:
            messagebox.showerror("Restore Failed", str(e), parent=self)
