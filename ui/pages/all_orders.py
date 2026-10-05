"""
ui/pages/all_orders.py  –  All Orders page with status filter
"""
import customtkinter as ctk
from ui.theme import *
from ui.widgets import HSep, SectionHeader
from database import db_manager as db


class AllOrdersPage(ctk.CTkFrame):

    def __init__(self, master, nav_callback, **kw):
        super().__init__(master, fg_color=CLR_BG, **kw)
        self.nav_callback = nav_callback
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # Toolbar
        toolbar = ctk.CTkFrame(self, fg_color=CLR_SURFACE,
                               corner_radius=0, height=54)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)

        ctk.CTkLabel(toolbar, text="📋  All Orders",
                     font=FONT_HEADING, text_color=CLR_TEXT
                     ).pack(side="left", padx=PAD*2)

        # Status filter
        self.filter_var = ctk.StringVar(value="All")
        ctk.CTkSegmentedButton(
            toolbar,
            values=["All", "Pending", "In Progress", "Ready", "Delivered"],
            variable=self.filter_var,
            font=FONT_SMALL,
            command=lambda v: self.refresh()
        ).pack(side="left", padx=PAD*2)

        HSep(self).pack(fill="x")

        # Column headers
        hdr = ctk.CTkFrame(self, fg_color=CLR_SURFACE2,
                           corner_radius=0, height=32)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        for col, wt in [("Customer", 2), ("Suit Type", 2),
                        ("Delivery", 2), ("Status", 1), ("Amount", 2), ("", 1)]:
            ctk.CTkLabel(hdr, text=col, font=FONT_SMALL,
                         text_color=CLR_TEXT_MUTED, anchor="w"
                         ).pack(side="left", padx=PAD, expand=(wt == 2))

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=PAD*2, pady=PAD_S)

    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        orders = db.get_all_orders(status_filter=self.filter_var.get())
        if not orders:
            ctk.CTkLabel(self.scroll,
                         text="No orders found for this filter.",
                         font=FONT_BODY, text_color=CLR_TEXT_MUTED
                         ).pack(pady=PAD*4)
            return
        for order in orders:
            self._render_row(dict(order))

    def _render_row(self, o: dict):
        row = ctk.CTkFrame(self.scroll, fg_color=CLR_SURFACE,
                           corner_radius=8, border_width=1,
                           border_color=CLR_BORDER)
        row.pack(fill="x", pady=3)
        row.columnconfigure(0, weight=2)
        row.columnconfigure(1, weight=2)
        row.columnconfigure(2, weight=2)
        row.columnconfigure(3, weight=1)
        row.columnconfigure(4, weight=2)
        row.columnconfigure(5, weight=1)

        # Customer
        cust_f = ctk.CTkFrame(row, fg_color="transparent")
        cust_f.grid(row=0, column=0, sticky="w", padx=PAD, pady=PAD_S)
        ctk.CTkLabel(cust_f, text=o["customer_name"] if o["customer_name"] else "",
                     font=FONT_SUBHEAD, text_color=CLR_TEXT).pack(anchor="w")
        ctk.CTkLabel(cust_f, text=o["customer_phone"] if o["customer_phone"] else "",
                     font=FONT_SMALL, text_color=CLR_TEXT_MUTED).pack(anchor="w")

        # Suit type
        qty = o["quantity"] if "quantity" in o.keys() and o["quantity"] else 1
        suit = o["suit_type"] if o["suit_type"] else ""
        ctk.CTkLabel(row, text=f"{qty}x {suit}",
                     font=FONT_BODY, text_color=CLR_TEXT
                     ).grid(row=0, column=1, sticky="w", padx=PAD)

        # Delivery
        ctk.CTkLabel(row, text=o["delivery_date"] if o["delivery_date"] else "—",
                     font=FONT_BODY, text_color=CLR_TEXT_MUTED
                     ).grid(row=0, column=2, sticky="w", padx=PAD)

        # Status
        from ui.widgets import StatusBadge
        StatusBadge(row, o["status"] if o["status"] else "Pending"
                    ).grid(row=0, column=3, padx=PAD, pady=PAD_S)

        # Amounts
        amt_f = ctk.CTkFrame(row, fg_color="transparent")
        amt_f.grid(row=0, column=4, sticky="w", padx=PAD, pady=PAD_S)
        rem = o["remaining"] if o["remaining"] else 0
        ctk.CTkLabel(amt_f, text=f"Rs {o['total_amount'] if o['total_amount'] else 0:,.0f}",
                     font=FONT_BODY, text_color=CLR_TEXT).pack(anchor="w")
        ctk.CTkLabel(amt_f,
                     text=f"Bal: Rs {rem:,.0f}",
                     font=FONT_SMALL,
                     text_color=CLR_DANGER if rem > 0 else CLR_TEXT_MUTED
                     ).pack(anchor="w")

        # Profile button
        cid = o["customer_id"]
        ctk.CTkButton(row, text="Profile", width=80, height=28,
                      font=FONT_SMALL,
                      fg_color=CLR_PRIMARY, hover_color=CLR_PRIMARY_DK,
                      command=lambda c=cid: self.nav_callback("customer", c)
                      ).grid(row=0, column=5, padx=PAD, pady=PAD_S)
