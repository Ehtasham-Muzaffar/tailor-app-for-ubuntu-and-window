"""
ui/pages/dashboard.py  –  Main Dashboard Page
"""
import customtkinter as ctk
from ui.theme import *
from ui.widgets import StatCard, HSep, SectionHeader, StatusBadge
from database import db_manager as db


class DashboardPage(ctk.CTkFrame):

    def __init__(self, master, nav_callback, **kw):
        super().__init__(master, fg_color=CLR_BG, **kw)
        self.nav_callback = nav_callback
        self._build_ui()
        self.refresh()

    # ── UI skeleton ───────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Top header ─────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=CLR_SURFACE,
                              corner_radius=0, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="✂  Fazian Tailor Shop",
                     font=("Segoe UI", 20, "bold"),
                     text_color=CLR_PRIMARY).pack(side="left", padx=PAD*2)
        ctk.CTkLabel(header, text="Management System",
                     font=FONT_BODY, text_color=CLR_TEXT_MUTED
                     ).pack(side="left")

        # ── Search bar ─────────────────────────────────────────────────
        search_frame = ctk.CTkFrame(self, fg_color=CLR_SURFACE,
                                    corner_radius=0)
        search_frame.pack(fill="x")
        ctk.CTkLabel(search_frame, text="🔍  Search Customer:",
                     font=FONT_BODY, text_color=CLR_TEXT_MUTED
                     ).pack(side="left", padx=(PAD*2, PAD_S), pady=PAD)
        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Enter phone number or name…",
            width=340, font=FONT_BODY, fg_color=CLR_SURFACE2,
            border_color=CLR_BORDER, text_color=CLR_TEXT, height=38
        )
        self.search_entry.pack(side="left", pady=PAD)
        self.search_entry.bind("<KeyRelease>", lambda e: self._do_search())

        ctk.CTkButton(search_frame, text="+ New Customer", width=140, height=38,
                      font=FONT_BODY,
                      fg_color=CLR_PRIMARY, hover_color=CLR_PRIMARY_DK,
                      command=self._new_customer
                      ).pack(side="left", padx=PAD*2, pady=PAD)

        HSep(self).pack(fill="x")

        # ── Stat cards row ─────────────────────────────────────────────
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=PAD*2, pady=PAD)

        self.card_customers = StatCard(cards_frame, "Total Customers",
                                       "0", CLR_PRIMARY)
        self.card_customers.pack(side="left", fill="y", expand=True,
                                  padx=(0, PAD), ipady=PAD)
        self.card_due_today = StatCard(cards_frame, "Due Today",
                                     "0", CLR_ACCENT)
        self.card_due_today.pack(side="left", fill="y", expand=True,
                               padx=(0, PAD), ipady=PAD)
        self.card_pending = StatCard(cards_frame, "Pending",
                                     "0", CLR_WARNING)
        self.card_pending.pack(side="left", fill="y", expand=True,
                                padx=(0, PAD), ipady=PAD)
        self.card_ready = StatCard(cards_frame, "Ready for Pickup",
                                   "0", CLR_SUCCESS)
        self.card_ready.pack(side="left", fill="y", expand=True,
                              padx=(0, PAD), ipady=PAD)
        self.card_revenue = StatCard(cards_frame, "Total Revenue",
                                     "Rs 0", CLR_INFO)
        self.card_revenue.pack(side="left", fill="y", expand=True, ipady=PAD)

        # ── Search results / Customer list ─────────────────────────────
        SectionHeader(self, "  Customers").pack(anchor="w",
                                                padx=PAD*2, pady=(PAD, PAD_S))
        HSep(self).pack(fill="x", padx=PAD*2)

        self.cust_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.cust_scroll.pack(fill="both", expand=True, padx=PAD*2, pady=(PAD_S, 0))

    # ── Refresh / populate ────────────────────────────────────────────────
    def refresh(self):
        stats = db.get_dashboard_stats()
        self.card_customers.update_value(str(stats["total_customers"]))
        self.card_due_today.update_value(str(stats["due_today"]))
        self.card_pending.update_value(str(stats["pending_orders"]))
        self.card_ready.update_value(str(stats["ready_orders"]))
        self.card_revenue.update_value(f"Rs {stats['total_revenue']:,.0f}")
        self._do_search()

    def _do_search(self):
        q = self.search_entry.get().strip()
        if q:
            customers = db.search_customers(q)
        else:
            customers = db.get_all_customers()
        self._render_customers(customers)

    def _render_customers(self, customers):
        for w in self.cust_scroll.winfo_children():
            w.destroy()

        if not customers:
            ctk.CTkLabel(self.cust_scroll,
                         text="No customers found. Click '+ New Customer' to add one.",
                         font=FONT_BODY, text_color=CLR_TEXT_MUTED
                         ).pack(pady=PAD*4)
            return

        for cust in customers:
            self._render_customer_row(dict(cust))

    def _render_customer_row(self, cust: dict):
        row = ctk.CTkFrame(self.cust_scroll, fg_color=CLR_SURFACE,
                           corner_radius=8, border_width=1,
                           border_color=CLR_BORDER)
        row.pack(fill="x", pady=3)
        row.columnconfigure(0, weight=0)
        row.columnconfigure(1, weight=1)
        row.columnconfigure(2, weight=0)

        # Avatar circle
        av = ctk.CTkFrame(row, width=46, height=46,
                          fg_color=CLR_PRIMARY, corner_radius=23)
        av.grid(row=0, column=0, padx=PAD, pady=PAD_S)
        av.pack_propagate(False)
        initials = "".join(p[0].upper() for p in cust["name"].split()[:2])
        ctk.CTkLabel(av, text=initials, font=FONT_SUBHEAD,
                     text_color="#fff").pack(expand=True)

        # Info
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.grid(row=0, column=1, sticky="w", pady=PAD_S)
        ctk.CTkLabel(info, text=cust["name"], font=FONT_SUBHEAD,
                     text_color=CLR_TEXT).pack(anchor="w")
        ctk.CTkLabel(info, text=f"📞 {cust['phone']}  |  📍 {cust['address'] if cust['address'] else '—'}",
                     font=FONT_SMALL, text_color=CLR_TEXT_MUTED).pack(anchor="w")
        ctk.CTkLabel(info, text=f"Added: {(cust['created_at'] if cust['created_at'] else '')[:10]}",
                     font=FONT_SMALL, text_color=CLR_TEXT_DARK).pack(anchor="w")

        # Buttons
        btn_f = ctk.CTkFrame(row, fg_color="transparent")
        btn_f.grid(row=0, column=2, padx=PAD)

        cid = cust["id"]
        ctk.CTkButton(btn_f, text="👤 Profile", width=100, height=30,
                      font=FONT_SMALL,
                      fg_color=CLR_PRIMARY, hover_color=CLR_PRIMARY_DK,
                      command=lambda c=cid: self.nav_callback("customer", c)
                      ).pack(pady=2)
        ctk.CTkButton(btn_f, text="✏ Edit", width=100, height=30,
                      font=FONT_SMALL,
                      fg_color=CLR_SURFACE2, hover_color=CLR_BORDER,
                      text_color=CLR_TEXT_MUTED,
                      command=lambda c=cid: self._edit_customer(c)
                      ).pack(pady=2)
        ctk.CTkButton(btn_f, text="🗑 Delete", width=100, height=30,
                      font=FONT_SMALL,
                      fg_color="#3d1515", hover_color=CLR_DANGER,
                      text_color=CLR_DANGER,
                      command=lambda c=cid: self._delete_customer(c)
                      ).pack(pady=2)

    # ── Actions ───────────────────────────────────────────────────────────
    def _new_customer(self):
        from ui.dialogs import CustomerDialog
        CustomerDialog(self, on_save=lambda cid: self.refresh())

    def _edit_customer(self, customer_id: int):
        from ui.dialogs import CustomerDialog
        CustomerDialog(self, customer_id=customer_id,
                       on_save=lambda cid: self.refresh())

    def _delete_customer(self, customer_id: int):
        from tkinter import messagebox
        cust = db.get_customer_by_id(customer_id)
        if messagebox.askyesno(
                "Confirm Delete",
                f"Delete customer '{cust['name']}'?\n"
                "All their measurements and orders will be removed.",
                parent=self):
            db.delete_customer(customer_id)
            self.refresh()
