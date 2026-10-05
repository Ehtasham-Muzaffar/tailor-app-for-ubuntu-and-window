"""
ui/theme.py  –  Global color tokens and font constants
"""
import customtkinter as ctk

# ── Appearance ────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Brand Palette ─────────────────────────────────────────────────────────
CLR_BG          = "#0B0F19"       # Very deep premium blue/black
CLR_SURFACE     = "#131826"       # Card/panel surfaces
CLR_SURFACE2    = "#1C2333"       # Slightly lighter surface
CLR_BORDER      = "#2A3449"       # Subtle borders

CLR_PRIMARY     = "#6366F1"       # Vibrant Indigo
CLR_PRIMARY_DK  = "#4F46E5"       # Darker Indigo (hover)
CLR_ACCENT      = "#EC4899"       # Vibrant Pink accent
CLR_SUCCESS     = "#10B981"       # Emerald Green
CLR_WARNING     = "#F59E0B"       # Amber
CLR_DANGER      = "#F43F5E"       # Rose Red
CLR_INFO        = "#38BDF8"       # Sky Blue

CLR_TEXT        = "#F8FAFC"       # Bright text
CLR_TEXT_MUTED  = "#94A3B8"       # Secondary / muted text
CLR_TEXT_DARK   = "#475569"       # Very muted

# ── Status colour map ─────────────────────────────────────────────────────
STATUS_COLORS = {
    "Pending":     CLR_WARNING,
    "In Progress": CLR_INFO,
    "Ready":       CLR_SUCCESS,
    "Delivered":   CLR_TEXT_MUTED,
}

# ── Font shortcuts ─────────────────────────────────────────────────────────
# Using generic Helvetica which falls back gracefully on all OS
FONT_TITLE   = ("Helvetica", 26, "bold")
FONT_HEADING = ("Helvetica", 18, "bold")
FONT_SUBHEAD = ("Helvetica", 14, "bold")
FONT_BODY    = ("Helvetica", 13)
FONT_SMALL   = ("Helvetica", 12)
FONT_MONO    = ("Courier", 12)

# ── Padding / radius ──────────────────────────────────────────────────────
PAD   = 16
PAD_S = 8
RAD   = 12
