"""
ui/pages/customer_profile.py  –  Full customer profile page
(measurements + order history)
"""
import customtkinter as ctk
from ui.theme import *
from ui.widgets import HSep, SectionHeader, StatCard, StatusBadge
from database import db_manager as db


class CustomerProfilePage(ctk.CTkFrame):

    def __init__(self, master, customer_id: int, nav_callback, **kw):
        super().__init__(master, fg_color=CLR_BG, **kw)
        self.customer_id  = customer_id
        self.nav_callback = nav_callback
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # ── Toolbar ────────────────────────────────────────────────────
        toolbar = ctk.CTkFrame(self, fg_color=CLR_SURFACE,
                               corner_radius=0, height=54)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)

        ctk.CTkButton(toolbar, text="← Back", width=90, height=32,
                      fg_color="transparent", hover_color=CLR_SURFACE2,
                      text_color=CLR_TEXT_MUTED, font=FONT_BODY,
                      command=lambda: self.nav_callback("dashboard")
                      ).pack(side="left", padx=PAD)

        self.lbl_title = ctk.CTkLabel(toolbar, text="Customer Profile",
                                       font=FONT_HEADING, text_color=CLR_TEXT)
        self.lbl_title.pack(side="left", padx=PAD)

        ctk.CTkButton(toolbar, text="✏ Edit Customer", width=130, height=32,
                      fg_color=CLR_SURFACE2, hover_color=CLR_BORDER,
                      text_color=CLR_TEXT_MUTED, font=FONT_BODY,
                      command=self._edit_customer
                      ).pack(side="right", padx=PAD)

        ctk.CTkButton(toolbar, text="+ New Order", width=120, height=32,
                      fg_color=CLR_PRIMARY, hover_color=CLR_PRIMARY_DK,
                      font=FONT_BODY,
                      command=self._new_order
                      ).pack(side="right", padx=PAD_S)

        HSep(self).pack(fill="x")

        # ── Main scroll area ───────────────────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=PAD*2, pady=PAD)

    # ── Populate ──────────────────────────────────────────────────────────
    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        cust  = db.get_customer_by_id(self.customer_id)
        meas  = db.get_measurements(self.customer_id)
        orders = db.get_orders_for_customer(self.customer_id)

        if not cust:
            ctk.CTkLabel(self.scroll, text="Customer not found.",
                         font=FONT_BODY, text_color=CLR_DANGER).pack(pady=PAD)
            return

        self.lbl_title.configure(text=f"👤  {cust['name']}")

        # ── Customer info card ─────────────────────────────────────────
        info_card = ctk.CTkFrame(self.scroll, fg_color=CLR_SURFACE,
                                  corner_radius=RAD, border_width=1,
                                  border_color=CLR_BORDER)
        info_card.pack(fill="x", pady=(0, PAD))

        info_card.columnconfigure(0, weight=1)
        info_card.columnconfigure(1, weight=1)
        info_card.columnconfigure(2, weight=1)

        ctk.CTkLabel(info_card,
                     text=f"📞  {cust['phone']}",
                     font=FONT_SUBHEAD, text_color=CLR_PRIMARY
                     ).grid(row=0, column=0, sticky="w", padx=PAD*2, pady=PAD)
        ctk.CTkLabel(info_card,
                     text=f"📍  {cust['address'] if cust['address'] else '—'}",
                     font=FONT_BODY, text_color=CLR_TEXT_MUTED
                     ).grid(row=0, column=1, sticky="w", padx=PAD, pady=PAD)
        ctk.CTkLabel(info_card,
                     text=f"📅  Since {(cust['created_at'] if cust['created_at'] else '')[:10]}",
                     font=FONT_BODY, text_color=CLR_TEXT_MUTED
                     ).grid(row=0, column=2, sticky="w", padx=PAD, pady=PAD)

        # ── Financial summary ──────────────────────────────────────────
        fin_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        fin_row.pack(fill="x", pady=(0, PAD))

        conn = db.get_connection()
        fin = conn.execute(
            "SELECT SUM(total_amount),SUM(advance_paid),SUM(remaining) "
            "FROM orders WHERE customer_id=?", (self.customer_id,)
        ).fetchone()
        conn.close()

        total_amt  = fin[0] or 0
        total_adv  = fin[1] or 0
        total_rem  = fin[2] or 0

        StatCard(fin_row, "Total Billed",   f"Rs {total_amt:,.0f}",  CLR_INFO
                 ).pack(side="left", fill="y", expand=True, padx=(0, PAD), ipady=8)
        StatCard(fin_row, "Total Received", f"Rs {total_adv:,.0f}",  CLR_SUCCESS
                 ).pack(side="left", fill="y", expand=True, padx=(0, PAD), ipady=8)
        StatCard(fin_row, "Total Balance",  f"Rs {total_rem:,.0f}",  CLR_DANGER
                 ).pack(side="left", fill="y", expand=True, ipady=8)

        # ── Measurements ──────────────────────────────────────────────
        SectionHeader(self.scroll, "📐  Measurements").pack(anchor="w",
                                                            pady=(PAD, PAD_S))
        HSep(self.scroll).pack(fill="x")

        meas_card = ctk.CTkFrame(self.scroll, fg_color=CLR_SURFACE,
                                  corner_radius=RAD, border_width=1,
                                  border_color=CLR_BORDER)
        meas_card.pack(fill="x", pady=(PAD_S, PAD))

        MEAS_LABELS = [
            ("length",         "Length"),
            ("shoulder",       "Shoulder"),
            ("neck",           "Neck"),
            ("chest",          "Chest"),
            ("waist",          "Waist"),
            ("sleeves",        "Sleeves"),
            ("armhole",        "Armhole"),
            ("bottom_ghera",   "Bottom / Ghera"),
            ("trouser_length", "Trouser Length"),
            ("trouser_poncha", "Trouser Bottom (Poncha)"),
            ("collar_type",    "Collar / Baan"),
            ("front_pocket",   "Front Pocket"),
            ("side_pocket",    "Side Pocket"),
            ("cuffs",          "Cuffs"),
            ("shalwar_pocket", "Shalwar Pocket"),
        ]

        cols = 5
        for i, (key, label) in enumerate(MEAS_LABELS):
            row_i = i // cols
            col_i = i % cols
            
            # Show empty or "—" for blank ones
            val = "—"
            if meas and meas[key] is not None:
                if isinstance(meas[key], float):
                    val = f"{meas[key]}″"
                else:
                    val = str(meas[key])
                    
            cell  = ctk.CTkFrame(meas_card, fg_color=CLR_SURFACE2,
                                  corner_radius=8)
            cell.grid(row=row_i, column=col_i, padx=PAD_S, pady=PAD_S,
                      sticky="nsew")
            meas_card.columnconfigure(col_i, weight=1)
            ctk.CTkLabel(cell, text=label, font=FONT_SMALL,
                         text_color=CLR_TEXT_MUTED).pack(pady=(PAD_S, 0), padx=PAD)
            ctk.CTkLabel(cell,
                         text=val,
                         font=FONT_SUBHEAD, text_color=CLR_TEXT
                         ).pack(pady=(0, PAD_S), padx=PAD)

        if meas and meas["special_notes"]:
            notes_card = ctk.CTkFrame(self.scroll, fg_color=CLR_SURFACE,
                                       corner_radius=RAD, border_width=1,
                                       border_color=CLR_BORDER)
            notes_card.pack(fill="x", pady=(0, PAD))
            ctk.CTkLabel(notes_card, text="📝  Special Instructions",
                         font=FONT_SUBHEAD, text_color=CLR_ACCENT
                         ).pack(anchor="w", padx=PAD, pady=(PAD_S, 0))
            ctk.CTkLabel(notes_card, text=meas["special_notes"],
                         font=FONT_BODY, text_color=CLR_TEXT, wraplength=700,
                         justify="left"
                         ).pack(anchor="w", padx=PAD, pady=(0, PAD))

        # ── Order history ──────────────────────────────────────────────
        SectionHeader(self.scroll,
                      f"📋  Order History ({len(orders)})").pack(anchor="w",
                                                                  pady=(PAD, PAD_S))
        HSep(self.scroll).pack(fill="x")

        if not orders:
            ctk.CTkLabel(self.scroll,
                         text="No orders yet. Click '+ New Order' to create one.",
                         font=FONT_BODY, text_color=CLR_TEXT_MUTED
                         ).pack(pady=PAD*2)
        else:
            for order in orders:
                self._render_order_row(dict(order))

    def _render_order_row(self, order: dict):
        from ui.widgets import OrderRow
        row = OrderRow(self.scroll, order,
                       on_edit=self._edit_order,
                       on_delete=self._delete_order,
                       on_receipt=self._print_receipt)
        row.pack(fill="x", pady=3)

    # ── Actions ───────────────────────────────────────────────────────────
    def _new_order(self):
        from ui.dialogs import OrderDialog
        OrderDialog(self, self.customer_id, on_save=self.refresh)

    def _edit_customer(self):
        from ui.dialogs import CustomerDialog
        CustomerDialog(self, customer_id=self.customer_id,
                       on_save=lambda cid: self.refresh())

    def _edit_order(self, order_id: int):
        from ui.dialogs import OrderDialog
        OrderDialog(self, self.customer_id, order_id=order_id,
                    on_save=self.refresh)

    def _delete_order(self, order_id: int):
        from tkinter import messagebox
        if messagebox.askyesno("Confirm Delete",
                               "Delete this order? This cannot be undone.",
                               parent=self):
            db.delete_order(order_id)
            self.refresh()

    def _print_receipt(self, order_id: int):
        from ui.pages.print_receipt import PrintReceiptDialog
        PrintReceiptDialog(self, order_id)
