"""
ui/widgets.py  –  Reusable custom widgets
"""
import customtkinter as ctk
from ui.theme import *


# ─── Stat Card ────────────────────────────────────────────────────────────
class StatCard(ctk.CTkFrame):
    """A glowing KPI card used on the dashboard."""
    def __init__(self, master, title: str, value: str, color: str = CLR_PRIMARY, **kw):
        super().__init__(master, fg_color=CLR_SURFACE, corner_radius=12, **kw)
        self.configure(border_width=1, border_color=CLR_BORDER)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(side="left", fill="both", expand=True, pady=PAD*1.5, padx=PAD*1.5)

        title_frame = ctk.CTkFrame(inner, fg_color="transparent")
        title_frame.pack(anchor="w", fill="x")
        
        # Small colored indicator dot
        dot = ctk.CTkFrame(title_frame, fg_color=color, width=10, height=10, corner_radius=5)
        dot.pack(side="left", padx=(0, 6))
        
        ctk.CTkLabel(title_frame, text=title, font=FONT_SMALL,
                     text_color=CLR_TEXT_MUTED).pack(side="left")

        self._val_lbl = ctk.CTkLabel(inner, text=value, font=("Segoe UI", 26, "bold"),
                                     text_color=CLR_TEXT)
        self._val_lbl.pack(anchor="w", pady=(8, 0))

    def update_value(self, value: str):
        self._val_lbl.configure(text=value)


# ─── Section Header ───────────────────────────────────────────────────────
class SectionHeader(ctk.CTkLabel):
    def __init__(self, master, text: str, **kw):
        super().__init__(master, text=text, font=FONT_HEADING,
                         text_color=CLR_TEXT, **kw)


# ─── Labelled Entry ───────────────────────────────────────────────────────
class LabelEntry(ctk.CTkFrame):
    def __init__(self, master, label: str, placeholder: str = "",
                 width: int = 200, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        ctk.CTkLabel(self, text=label, font=FONT_SMALL,
                     text_color=CLR_TEXT_MUTED, anchor="w").pack(anchor="w", pady=(0, 2))
        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder,
                                  width=width, height=36, font=FONT_BODY,
                                  corner_radius=8,
                                  fg_color=CLR_SURFACE2, border_color=CLR_BORDER,
                                  text_color=CLR_TEXT)
        self.entry.pack(anchor="w")

    def get(self) -> str:
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, "end")
        if value is not None:
            self.entry.insert(0, str(value))

    def clear(self):
        self.entry.delete(0, "end")


# ─── Labelled OptionMenu ──────────────────────────────────────────────────
class LabelOptionMenu(ctk.CTkFrame):
    def __init__(self, master, label: str, values: list, width: int = 200, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        ctk.CTkLabel(self, text=label, font=FONT_SMALL,
                     text_color=CLR_TEXT_MUTED, anchor="w").pack(anchor="w", pady=(0, 2))
        
        self.var = ctk.StringVar(value=values[0] if values else "")
        self.menu = ctk.CTkOptionMenu(self, values=values, variable=self.var,
                                      width=width, height=36, font=FONT_BODY,
                                      corner_radius=8,
                                      fg_color=CLR_SURFACE2, button_color=CLR_PRIMARY,
                                      button_hover_color=CLR_PRIMARY_DK,
                                      dropdown_fg_color=CLR_SURFACE2)
        self.menu.pack(anchor="w")

    def get(self) -> str:
        return self.var.get()

    def set(self, value):
        if value:
            self.var.set(str(value))


# ─── Status Badge ─────────────────────────────────────────────────────────
class StatusBadge(ctk.CTkLabel):
    def __init__(self, master, status: str, **kw):
        color = STATUS_COLORS.get(status, CLR_TEXT_MUTED)
        super().__init__(master, text=f"  {status}  ",
                         font=FONT_SMALL, fg_color=color,
                         text_color="#0f1117",
                         corner_radius=6, **kw)


# ─── Separator ────────────────────────────────────────────────────────────
class HSep(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, height=1, fg_color=CLR_BORDER, **kw)


# ─── Scrollable Order Row ─────────────────────────────────────────────────
class OrderRow(ctk.CTkFrame):
    """Single row in the order list."""
    def __init__(self, master, order_data: dict,
                 on_edit=None, on_delete=None, on_receipt=None, **kw):
        super().__init__(master, fg_color=CLR_SURFACE, corner_radius=8,
                         border_width=1, border_color=CLR_BORDER, **kw)

        # Layout columns
        self.columnconfigure(0, weight=2)   # suit type
        self.columnconfigure(1, weight=2)   # dates
        self.columnconfigure(2, weight=1)   # status
        self.columnconfigure(3, weight=2)   # amounts
        self.columnconfigure(4, weight=1)   # actions

        status  = order_data["status"] if order_data["status"] else "Pending"
        color   = STATUS_COLORS.get(status, CLR_TEXT_MUTED)

        # Suit type + order date
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=PAD, pady=PAD_S)
        qty = order_data["quantity"] if "quantity" in order_data.keys() and order_data["quantity"] else 1
        suit = order_data["suit_type"] if order_data["suit_type"] else ""
        
        # Urgent badge and Suit
        suit_row = ctk.CTkFrame(left, fg_color="transparent")
        suit_row.pack(anchor="w")
        
        ctk.CTkLabel(suit_row, text=f"{qty}x {suit}",
                     font=FONT_SUBHEAD, text_color=CLR_TEXT).pack(side="left")
                     
        if "is_urgent" in order_data and order_data["is_urgent"]:
            ctk.CTkLabel(suit_row, text=" 🔥 URGENT ", font=FONT_SMALL,
                         fg_color=CLR_DANGER, text_color="#fff", corner_radius=4).pack(side="left", padx=(6, 0))

        worker = order_data.get("worker_name", "")
        if worker:
            ctk.CTkLabel(left, text=f"Worker: {worker}",
                         font=FONT_SMALL, text_color=CLR_PRIMARY).pack(anchor="w")

        ctk.CTkLabel(left, text=f"Order: {order_data['order_date'] if order_data['order_date'] else ''}",
                     font=FONT_SMALL, text_color=CLR_TEXT_MUTED).pack(anchor="w")

        # Dates
        mid = ctk.CTkFrame(self, fg_color="transparent")
        mid.grid(row=0, column=1, sticky="w", padx=PAD, pady=PAD_S)
        ctk.CTkLabel(mid, text=f"Delivery: {order_data['delivery_date'] if order_data['delivery_date'] else '—'}",
                     font=FONT_SMALL, text_color=CLR_TEXT_MUTED).pack(anchor="w")

        # Status badge
        StatusBadge(self, status).grid(row=0, column=2, padx=PAD, pady=PAD_S)

        # Amounts
        amt_frame = ctk.CTkFrame(self, fg_color="transparent")
        amt_frame.grid(row=0, column=3, sticky="w", padx=PAD, pady=PAD_S)
        total   = order_data["total_amount"] if order_data["total_amount"] else 0
        advance = order_data["advance_paid"] if order_data["advance_paid"] else 0
        remain  = order_data["remaining"] if "remaining" in order_data.keys() and order_data["remaining"] else (total - advance)
        ctk.CTkLabel(amt_frame, text=f"Total: Rs {total:,.0f}",
                     font=FONT_SMALL, text_color=CLR_TEXT).pack(anchor="w")
        ctk.CTkLabel(amt_frame, text=f"Advance: Rs {advance:,.0f}",
                     font=FONT_SMALL, text_color=CLR_SUCCESS).pack(anchor="w")
        ctk.CTkLabel(amt_frame, text=f"Balance: Rs {remain:,.0f}",
                     font=FONT_SMALL,
                     text_color=CLR_DANGER if remain > 0 else CLR_TEXT_MUTED).pack(anchor="w")

        # Action buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=0, column=4, padx=PAD, pady=PAD_S)

        order_id = order_data["id"]
        ctk.CTkButton(btn_frame, text="✏ Edit", width=80, height=26,
                      font=FONT_SMALL,
                      fg_color=CLR_PRIMARY, hover_color=CLR_PRIMARY_DK,
                      command=lambda: on_edit(order_id) if on_edit else None
                      ).pack(pady=2)
        ctk.CTkButton(btn_frame, text="🧾 Receipt", width=80, height=26,
                      font=FONT_SMALL,
                      fg_color="#1a2e1a", hover_color=CLR_SUCCESS,
                      text_color=CLR_SUCCESS,
                      command=lambda: on_receipt(order_id) if on_receipt else None
                      ).pack(pady=2)
                      
        def send_whatsapp():
            import webbrowser
            from urllib.parse import quote
            phone = order_data.get("customer_phone", "")
            if not phone and "customer_id" in order_data:
                # Need to fetch phone from db if not passed directly in order_data
                from database import db_manager as db
                cust = db.get_customer_by_id(order_data["customer_id"])
                if cust:
                    phone = cust["phone"]
            
            if phone:
                # Clean phone number
                phone = ''.join(c for c in phone if c.isdigit() or c == '+')
                bal = order_data.get('remaining', 0)
                msg = f"Hello, your order from Fazian Tailor Shop is ready for pickup."
                if bal > 0:
                    msg += f" Balance due: Rs {bal:,.0f}."
                webbrowser.open(f"https://wa.me/{phone}?text={quote(msg)}")
                
        ctk.CTkButton(btn_frame, text="💬 WhatsApp", width=80, height=26,
                      font=FONT_SMALL,
                      fg_color="#1d3b25", hover_color="#25D366",
                      text_color="#25D366",
                      command=send_whatsapp
                      ).pack(pady=2)
                      
        ctk.CTkButton(btn_frame, text="🗑 Del", width=80, height=26,
                      font=FONT_SMALL,
                      fg_color="#3d1515", hover_color=CLR_DANGER,
                      text_color=CLR_DANGER,
                      command=lambda: on_delete(order_id) if on_delete else None
                      ).pack(pady=2)
