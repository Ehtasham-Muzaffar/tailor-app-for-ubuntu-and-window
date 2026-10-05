"""
main.py  –  Application entry point & main window
"""
import sys
import os
import customtkinter as ctk
from ui.theme import *
from database import db_manager as db


def resource_path(relative: str) -> str:
    """Get absolute path to resource — works both in dev and PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative)


class TailorApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("✂  Fazian Tailor Shop")
        self.geometry("1300x840")
        self.minsize(1024, 680)
        self.configure(fg_color=CLR_BG)

        # Set window icon
        icon_path = resource_path(os.path.join("assets", "icon.png"))
        if os.path.exists(icon_path):
            try:
                from PIL import Image, ImageTk
                img = Image.open(icon_path)
                self._icon_img = ImageTk.PhotoImage(img.resize((32, 32)))
                self.iconphoto(True, self._icon_img)
            except Exception:
                pass

        # Initialise DB on first run
        db.init_db()

        self._current_page = None
        self._build_layout()

        # Start on dashboard
        self._navigate("dashboard")

    # ── Main layout ───────────────────────────────────────────────────────
    def _build_layout(self):
        # ── Sidebar ────────────────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(self, fg_color=CLR_SURFACE,
                                    corner_radius=0, width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo area
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=110)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)

        # Try to show the PNG icon in sidebar
        icon_path = resource_path(os.path.join("assets", "icon.png"))
        if os.path.exists(icon_path):
            try:
                logo_img = ctk.CTkImage(
                    light_image=__import__("PIL.Image", fromlist=["Image"]).open(icon_path),
                    dark_image=__import__("PIL.Image", fromlist=["Image"]).open(icon_path),
                    size=(56, 56)
                )
                ctk.CTkLabel(logo_frame, image=logo_img, text="").pack(pady=(12, 0))
            except Exception:
                ctk.CTkLabel(logo_frame, text="✂", font=("Segoe UI", 36),
                             text_color=CLR_PRIMARY).pack(pady=(16, 0))
        else:
            ctk.CTkLabel(logo_frame, text="✂", font=("Segoe UI", 36),
                         text_color=CLR_PRIMARY).pack(pady=(16, 0))

        ctk.CTkLabel(logo_frame, text="Fazian Tailor", font=FONT_SUBHEAD,
                     text_color=CLR_TEXT).pack()
        ctk.CTkLabel(logo_frame, text="Shop Manager", font=FONT_SMALL,
                     text_color=CLR_TEXT_DARK).pack()

        # Separator
        ctk.CTkFrame(self.sidebar, height=1, fg_color=CLR_BORDER
                     ).pack(fill="x", padx=PAD, pady=(0, PAD_S))

        # ── Nav buttons ────────────────────────────────────────────────
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        nav_items = [
            ("dashboard", "🏠  Dashboard"),
            ("orders",    "📋  All Orders"),
            ("settings",  "⚙  Settings & Backup"),
        ]
        for page_id, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                anchor="w",
                height=44,
                corner_radius=8,
                font=FONT_BODY,
                fg_color="transparent",
                hover_color=CLR_SURFACE2,
                text_color=CLR_TEXT_MUTED,
                command=lambda pid=page_id: self._navigate(pid)
            )
            btn.pack(fill="x", padx=PAD_S, pady=2)
            self._nav_buttons[page_id] = btn

        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="both", expand=True)

        # Bottom info
        ctk.CTkFrame(self.sidebar, height=1, fg_color=CLR_BORDER
                     ).pack(fill="x", padx=PAD)
        ctk.CTkLabel(self.sidebar, text="Fazian Tailor Shop  v1.0",
                     font=FONT_SMALL, text_color=CLR_TEXT_DARK
                     ).pack(pady=(PAD_S, 2))
        ctk.CTkLabel(self.sidebar, text="Offline  •  SQLite",
                     font=FONT_SMALL, text_color=CLR_TEXT_DARK
                     ).pack(pady=(0, PAD))

        # ── Content area ───────────────────────────────────────────────
        self.content = ctk.CTkFrame(self, fg_color=CLR_BG, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

    # ── Navigation ────────────────────────────────────────────────────────
    def _navigate(self, page_id: str, payload=None):
        if self._current_page:
            self._current_page.destroy()
            self._current_page = None

        # Highlight active nav button
        for pid, btn in self._nav_buttons.items():
            if pid == page_id:
                btn.configure(fg_color=CLR_SURFACE2, text_color=CLR_PRIMARY)
            else:
                btn.configure(fg_color="transparent", text_color=CLR_TEXT_MUTED)

        # If navigating to "customer", no sidebar highlight (sub-page)
        if page_id == "customer":
            for btn in self._nav_buttons.values():
                btn.configure(fg_color="transparent", text_color=CLR_TEXT_MUTED)

        page = self._build_page(page_id, payload)
        if page:
            page.pack(fill="both", expand=True)
            self._current_page = page

    def _build_page(self, page_id: str, payload=None):
        nav = self._navigate
        if page_id == "dashboard":
            from ui.pages.dashboard import DashboardPage
            return DashboardPage(self.content, nav_callback=nav)

        elif page_id == "customer":
            if payload is None:
                return None
            from ui.pages.customer_profile import CustomerProfilePage
            return CustomerProfilePage(self.content,
                                       customer_id=payload,
                                       nav_callback=nav)

        elif page_id == "orders":
            from ui.pages.all_orders import AllOrdersPage
            return AllOrdersPage(self.content, nav_callback=nav)

        elif page_id == "settings":
            from ui.pages.settings import SettingsPage
            return SettingsPage(self.content, nav_callback=nav)

        return None


# ── Entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = TailorApp()
    app.mainloop()
