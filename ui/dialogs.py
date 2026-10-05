"""
ui/dialogs.py  –  Modal dialogs: Add/Edit Customer, Add/Edit Order
"""
import customtkinter as ctk
from ui.theme import *
from ui.widgets import LabelEntry, LabelOptionMenu, HSep, SectionHeader
from database import db_manager as db
from tkinter import messagebox
import re


def _num(s: str):
    """Convert string to float, return None if blank."""
    s = s.strip()
    return float(s) if s else None


# ═══════════════════════════════════════════════════════════════════════════
#  Customer Dialog
# ═══════════════════════════════════════════════════════════════════════════
class CustomerDialog(ctk.CTkToplevel):
    """Add / Edit a customer and their measurements."""

    def __init__(self, master, customer_id: int = None, prefill_phone: str = "",
                 on_save=None):
        super().__init__(master)
        self.customer_id = customer_id
        self.on_save_cb  = on_save
        self._editing    = customer_id is not None

        title = "Edit Customer" if self._editing else "New Customer"
        self.title(title)
        self.geometry("720x780")
        self.resizable(False, False)
        self.configure(fg_color=CLR_BG)
        self.grab_set()

        self._build_ui(prefill_phone)
        if self._editing:
            self._load_existing()

        self.lift()
        self.focus()

    # ── Layout ───────────────────────────────────────────────────────────
    def _build_ui(self, prefill_phone: str):
        # Title bar
        ctk.CTkLabel(self, text="👤  Customer & Measurements",
                     font=FONT_TITLE, text_color=CLR_PRIMARY
                     ).pack(pady=(PAD*2, PAD), padx=PAD*2, anchor="w")
        HSep(self).pack(fill="x", padx=PAD*2)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=PAD*2, pady=PAD)
        f = scroll

        # ── Customer info ─────────────────────────────────────────────
        SectionHeader(f, "Customer Information").pack(anchor="w", pady=(0, PAD_S))

        self.e_name    = LabelEntry(f, "Full Name *", "e.g. Ahmed Khan", 280)
        self.e_name.pack(anchor="w", pady=3)

        self.e_phone   = LabelEntry(f, "Phone Number *", "e.g. 0300-1234567", 280)
        self.e_phone.pack(anchor="w", pady=3)
        if prefill_phone:
            self.e_phone.set(prefill_phone)
        if self._editing:
            self.e_phone.entry.configure(state="disabled")

        self.e_address = LabelEntry(f, "Address", "Street / City", 280)
        self.e_address.pack(anchor="w", pady=3)

        HSep(f).pack(fill="x", pady=PAD)

        # ── Measurements ──────────────────────────────────────────────
        SectionHeader(f, "Measurements (inches)").pack(anchor="w", pady=(0, PAD_S))

        meas_grid = ctk.CTkFrame(f, fg_color="transparent")
        meas_grid.pack(fill="x")

        fields_kameez = [
            ("length",       "Length"),
            ("shoulder",     "Shoulder"),
            ("neck",         "Neck"),
            ("chest",        "Chest"),
            ("waist",        "Waist"),
            ("sleeves",      "Sleeves"),
            ("armhole",      "Armhole"),
            ("bottom_ghera", "Bottom / Ghera"),
        ]
        fields_trouser = [
            ("trouser_length", "Trouser Length"),
            ("trouser_poncha", "Trouser Bottom (Poncha)"),
        ]

        self.meas_entries = {}
        self.meas_options = {}

        left_col = ctk.CTkFrame(meas_grid, fg_color="transparent")
        left_col.pack(side="left", anchor="n", fill="x", expand=True, padx=(0, PAD))
        right_col = ctk.CTkFrame(meas_grid, fg_color="transparent")
        right_col.pack(side="left", anchor="n", fill="x", expand=True, padx=(PAD, 0))

        for i, (key, lbl) in enumerate(fields_kameez):
            col = left_col if i < 4 else right_col
            e = LabelEntry(col, lbl, "0.0", 160)
            e.pack(anchor="w", pady=4)
            self.meas_entries[key] = e

        HSep(f).pack(fill="x", pady=PAD)
        SectionHeader(f, "Trouser / Shalwar").pack(anchor="w", pady=(0, PAD_S))
        t_row = ctk.CTkFrame(f, fg_color="transparent")
        t_row.pack(anchor="w", fill="x")
        for key, lbl in fields_trouser:
            e = LabelEntry(t_row, lbl, "0.0", 160)
            e.pack(side="left", padx=(0, PAD*2), pady=4)
            self.meas_entries[key] = e

        HSep(f).pack(fill="x", pady=PAD)
        SectionHeader(f, "Style / Preferences").pack(anchor="w", pady=(0, PAD_S))
        s_row1 = ctk.CTkFrame(f, fg_color="transparent")
        s_row1.pack(anchor="w", fill="x", pady=2)
        
        c_collar = LabelOptionMenu(s_row1, "Collar / Baan", ["Collar", "Baan", "Half Baan", "Magzi"], 160)
        c_collar.pack(side="left", padx=(0, PAD*2))
        self.meas_options["collar_type"] = c_collar

        c_cuffs = LabelOptionMenu(s_row1, "Sleeves / Cuffs", ["Open / Goal", "Cuff", "Cut"], 160)
        c_cuffs.pack(side="left", padx=(0, PAD*2))
        self.meas_options["cuffs"] = c_cuffs

        s_row2 = ctk.CTkFrame(f, fg_color="transparent")
        s_row2.pack(anchor="w", fill="x", pady=2)

        c_fp = LabelOptionMenu(s_row2, "Front Pocket", ["1", "2", "None"], 160)
        c_fp.pack(side="left", padx=(0, PAD*2))
        self.meas_options["front_pocket"] = c_fp

        c_sp = LabelOptionMenu(s_row2, "Side Pocket", ["2", "1", "None"], 160)
        c_sp.pack(side="left", padx=(0, PAD*2))
        self.meas_options["side_pocket"] = c_sp

        c_shp = LabelOptionMenu(s_row2, "Shalwar Pocket", ["No", "Yes"], 160)
        c_shp.pack(side="left", padx=(0, PAD*2))
        self.meas_options["shalwar_pocket"] = c_shp

        HSep(f).pack(fill="x", pady=PAD)

        # ── Special notes ─────────────────────────────────────────────
        SectionHeader(f, "Special Instructions").pack(anchor="w", pady=(0, PAD_S))
        self.txt_notes = ctk.CTkTextbox(f, height=80, fg_color=CLR_SURFACE2,
                                        border_color=CLR_BORDER, border_width=1,
                                        font=FONT_BODY, text_color=CLR_TEXT)
        self.txt_notes.pack(fill="x", pady=3)

        # ── Action buttons ────────────────────────────────────────────
        HSep(self).pack(fill="x", padx=PAD*2)
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=PAD, padx=PAD*2, anchor="e")

        ctk.CTkButton(btn_row, text="Cancel", width=100,
                      fg_color=CLR_SURFACE2, hover_color=CLR_BORDER,
                      text_color=CLR_TEXT_MUTED,
                      command=self.destroy).pack(side="left", padx=PAD_S)

        label = "💾  Update" if self._editing else "💾  Save Customer"
        ctk.CTkButton(btn_row, text=label, width=160,
                      fg_color=CLR_PRIMARY, hover_color=CLR_PRIMARY_DK,
                      command=self._save).pack(side="left")

    # ── Load existing data ────────────────────────────────────────────────
    def _load_existing(self):
        cust = db.get_customer_by_id(self.customer_id)
        if cust:
            self.e_name.set(cust["name"])
            self.e_phone.set(cust["phone"])
            self.e_address.set(cust["address"] or "")

        meas = db.get_measurements(self.customer_id)
        if meas:
            for key, widget in self.meas_entries.items():
                widget.set(meas[key] if meas[key] is not None else "")
            for key, widget in self.meas_options.items():
                widget.set(meas[key] if meas[key] is not None else "")
            notes = meas["special_notes"] or ""
            self.txt_notes.insert("1.0", notes)

    # ── Validate & Save ───────────────────────────────────────────────────
    def _save(self):
        name  = self.e_name.get().strip()
        phone = self.e_phone.get().strip()
        addr  = self.e_address.get().strip()

        if not name:
            messagebox.showerror("Validation", "Please enter customer name.", parent=self)
            return
        if not phone:
            messagebox.showerror("Validation", "Please enter phone number.", parent=self)
            return
        # Basic phone validation (digits, dashes, spaces, + allowed)
        if not re.match(r"^[\d\s\-\+]{7,15}$", phone):
            messagebox.showerror("Validation",
                                 "Invalid phone number format.\nUse digits, dashes or + only.",
                                 parent=self)
            return

        if self._editing:
            db.update_customer(self.customer_id, name, addr)
            cid = self.customer_id
        else:
            cid = db.add_customer(phone, name, addr)
            if cid is None:
                messagebox.showerror("Duplicate",
                                     "A customer with this phone number already exists.",
                                     parent=self)
                return

        # Collect measurements
        meas_data = {k: _num(w.get()) for k, w in self.meas_entries.items()}
        for k, w in self.meas_options.items():
            meas_data[k] = w.get().strip()
            
        meas_data["special_notes"] = self.txt_notes.get("1.0", "end").strip()
        db.save_measurements(cid, meas_data)

        if self.on_save_cb:
            self.on_save_cb(cid)
        self.destroy()


# ═══════════════════════════════════════════════════════════════════════════
#  Order Dialog
# ═══════════════════════════════════════════════════════════════════════════
class OrderDialog(ctk.CTkToplevel):
    """Add / Edit a single order."""

    def __init__(self, master, customer_id: int, order_id: int = None,
                 on_save=None):
        super().__init__(master)
        self.customer_id = customer_id
        self.order_id    = order_id
        self.on_save_cb  = on_save
        self._editing    = order_id is not None

        title = "Edit Order" if self._editing else "New Order"
        self.title(title)
        self.geometry("600x700")
        self.resizable(False, False)
        self.configure(fg_color=CLR_BG)
        self.grab_set()

        self._build_ui()
        if self._editing:
            self._load_existing()

        self.lift()
        self.focus()

    def _build_ui(self):
        from datetime import datetime, date
        ctk.CTkLabel(self, text="📋  Order Details",
                     font=FONT_TITLE, text_color=CLR_PRIMARY
                     ).pack(pady=(PAD*2, PAD), padx=PAD*2, anchor="w")
        HSep(self).pack(fill="x", padx=PAD*2)

        f = ctk.CTkScrollableFrame(self, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=PAD*2, pady=PAD)

        today = date.today().strftime("%Y-%m-%d")

        row0 = ctk.CTkFrame(f, fg_color="transparent")
        row0.pack(fill="x", pady=3)

        # Suit type
        type_f = ctk.CTkFrame(row0, fg_color="transparent")
        type_f.pack(side="left")
        ctk.CTkLabel(type_f, text="Suit Type *", font=FONT_SMALL,
                     text_color=CLR_TEXT_MUTED).pack(anchor="w")
        self.suit_var = ctk.StringVar(value=db.SUIT_TYPES[0])
        self.suit_om  = ctk.CTkOptionMenu(type_f, values=db.SUIT_TYPES,
                                           variable=self.suit_var,
                                           fg_color=CLR_SURFACE2,
                                           button_color=CLR_PRIMARY,
                                           dropdown_fg_color=CLR_SURFACE2,
                                           font=FONT_BODY, width=160)
        self.suit_om.pack(anchor="w", pady=(2, PAD))

        # Quantity
        self.e_qty = LabelEntry(row0, "Quantity *", "1", 100)
        self.e_qty.pack(side="left", padx=(PAD*2, 0), anchor="n")
        self.e_qty.set("1")

        # Dates
        row1 = ctk.CTkFrame(f, fg_color="transparent")
        row1.pack(fill="x", pady=3)
        self.e_order_date    = LabelEntry(row1, "Order Date *",    today, 160)
        self.e_order_date.pack(side="left")
        self.e_delivery_date = LabelEntry(row1, "Delivery Date",   "YYYY-MM-DD", 160)
        self.e_delivery_date.pack(side="left", padx=(PAD*2, 0))
        self.e_order_date.set(today)

        # Status
        ctk.CTkLabel(f, text="Status", font=FONT_SMALL,
                     text_color=CLR_TEXT_MUTED).pack(anchor="w", pady=(PAD, 0))
        self.status_var = ctk.StringVar(value="Pending")
        self.status_om  = ctk.CTkOptionMenu(f, values=db.ORDER_STATUSES,
                                             variable=self.status_var,
                                             fg_color=CLR_SURFACE2,
                                             button_color=CLR_PRIMARY,
                                             dropdown_fg_color=CLR_SURFACE2)
        self.status_om.pack(anchor="w", pady=(2, PAD))

        # Worker & Urgent & Fabric
        wu_row = ctk.CTkFrame(f, fg_color="transparent")
        wu_row.pack(fill="x", pady=3)
        
        self.e_worker = LabelEntry(wu_row, "Assigned Worker", "e.g. Master Ali", 140)
        self.e_worker.pack(side="left")
        
        self.e_fabric = LabelEntry(wu_row, "Fabric Given", "e.g. 4.5 meters", 140)
        self.e_fabric.pack(side="left", padx=(PAD*2, 0))
        
        self.urgent_var = ctk.IntVar(value=0)
        self.chk_urgent = ctk.CTkCheckBox(wu_row, text="Urgent Order", variable=self.urgent_var,
                                          fg_color=CLR_DANGER, hover_color=CLR_DANGER)
        self.chk_urgent.pack(side="left", padx=(PAD*2, 0), pady=(24, 0))

        # ── Order Specific Styles
        HSep(f).pack(fill="x", pady=PAD)
        SectionHeader(f, "Suit Styles / Design").pack(anchor="w", pady=(0, PAD_S))
        
        style_r1 = ctk.CTkFrame(f, fg_color="transparent")
        style_r1.pack(fill="x", pady=2)
        self.e_color = LabelEntry(style_r1, "Color", "e.g. Black", 160)
        self.e_color.pack(side="left")
        self.cuff_om = LabelOptionMenu(style_r1, "Cuff Type", ["Standard", "Cut", "Goal / Open"], 160)
        self.cuff_om.pack(side="left", padx=(PAD*2, 0))

        style_r2 = ctk.CTkFrame(f, fg_color="transparent")
        style_r2.pack(fill="x", pady=2)
        self.shalwar_om = LabelOptionMenu(style_r2, "Shalwar Bottom", ["Simple", "Design", "Embroidered"], 160)
        self.shalwar_om.pack(side="left")
        self.kameez_om = LabelOptionMenu(style_r2, "Kameez Bottom", ["Goal", "Straight (Chauras)"], 160)
        self.kameez_om.pack(side="left", padx=(PAD*2, 0))

        style_r3 = ctk.CTkFrame(f, fg_color="transparent")
        style_r3.pack(fill="x", pady=2)
        self.collar_om = LabelOptionMenu(style_r3, "Collar / Neck", ["Collar", "Baan", "Sherwani"], 160)
        self.collar_om.pack(side="left")
        self.front_pocket_om = LabelOptionMenu(style_r3, "Front Pocket", ["1", "2", "None"], 160)
        self.front_pocket_om.pack(side="left", padx=(PAD*2, 0))

        style_r4 = ctk.CTkFrame(f, fg_color="transparent")
        style_r4.pack(fill="x", pady=2)
        self.side_pocket_om = LabelOptionMenu(style_r4, "Side Pocket", ["Both Sides", "Left Only", "Right Only", "None"], 160)
        self.side_pocket_om.pack(side="left")
        self.shalwar_pocket_om = LabelOptionMenu(style_r4, "Shalwar Pocket", ["Yes (With Zip)", "Yes (Without Zip)", "No"], 160)
        self.shalwar_pocket_om.pack(side="left", padx=(PAD*2, 0))

        HSep(f).pack(fill="x", pady=PAD)
        SectionHeader(f, "Financial").pack(anchor="w", pady=(0, PAD_S))

        fin_row = ctk.CTkFrame(f, fg_color="transparent")
        fin_row.pack(fill="x")
        self.e_total   = LabelEntry(fin_row, "Total (Rs)", "0", 140)
        self.e_total.pack(side="left")
        self.e_advance = LabelEntry(fin_row, "Advance (Rs)", "0", 140)
        self.e_advance.pack(side="left", padx=(PAD*2, 0))

        # Live balance label
        self.lbl_balance = ctk.CTkLabel(f, text="Balance: Rs 0",
                                        font=FONT_SUBHEAD, text_color=CLR_DANGER)
        self.lbl_balance.pack(anchor="w", pady=(PAD_S, 0))
        self.e_total.entry.bind("<KeyRelease>", lambda e: self._update_balance())
        self.e_advance.entry.bind("<KeyRelease>", lambda e: self._update_balance())

        HSep(f).pack(fill="x", pady=PAD)

        # Remarks
        SectionHeader(f, "Remarks / Notes").pack(anchor="w", pady=(0, PAD_S))
        self.txt_remarks = ctk.CTkTextbox(f, height=70, fg_color=CLR_SURFACE2,
                                          border_color=CLR_BORDER, border_width=1,
                                          font=FONT_BODY, text_color=CLR_TEXT)
        self.txt_remarks.pack(fill="x")

        # Buttons
        HSep(self).pack(fill="x", padx=PAD*2)
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=PAD, padx=PAD*2, anchor="e")

        ctk.CTkButton(btn_row, text="Cancel", width=100,
                      fg_color=CLR_SURFACE2, hover_color=CLR_BORDER,
                      text_color=CLR_TEXT_MUTED,
                      command=self.destroy).pack(side="left", padx=PAD_S)

        label = "💾  Update Order" if self._editing else "💾  Save Order"
        ctk.CTkButton(btn_row, text=label, width=160,
                      fg_color=CLR_PRIMARY, hover_color=CLR_PRIMARY_DK,
                      command=self._save).pack(side="left")

    def _update_balance(self):
        try:
            total   = float(self.e_total.get() or 0)
            advance = float(self.e_advance.get() or 0)
            bal     = total - advance
            color   = CLR_DANGER if bal > 0 else CLR_SUCCESS
            self.lbl_balance.configure(text=f"Balance: Rs {bal:,.0f}", text_color=color)
        except ValueError:
            pass

    def _load_existing(self):
        order = db.get_order_by_id(self.order_id)
        if order:
            self.suit_var.set(order["suit_type"])
            self.status_var.set(order["status"])
            self.e_order_date.set(order["order_date"])
            self.e_delivery_date.set(order["delivery_date"] or "")
            self.e_total.set(order["total_amount"])
            self.e_advance.set(order["advance_paid"])
            qty = order["quantity"] if "quantity" in order.keys() and order["quantity"] else 1
            self.e_qty.set(qty)
            self.e_color.set(order["color"] if "color" in order.keys() and order["color"] else "")
            self.cuff_om.set(order["cuff_type"] if "cuff_type" in order.keys() and order["cuff_type"] else "")
            self.shalwar_om.set(order["shalwar_bottom"] if "shalwar_bottom" in order.keys() and order["shalwar_bottom"] else "")
            self.kameez_om.set(order["kameez_bottom"] if "kameez_bottom" in order.keys() and order["kameez_bottom"] else "")
            self.collar_om.set(order["collar_type"] if "collar_type" in order.keys() and order["collar_type"] else "")
            self.front_pocket_om.set(order["front_pocket"] if "front_pocket" in order.keys() and order["front_pocket"] else "")
            self.side_pocket_om.set(order["side_pocket"] if "side_pocket" in order.keys() and order["side_pocket"] else "")
            self.shalwar_pocket_om.set(order["shalwar_pocket"] if "shalwar_pocket" in order.keys() and order["shalwar_pocket"] else "")
            
            self.e_worker.set(order["worker_name"] if "worker_name" in order.keys() and order["worker_name"] else "")
            self.urgent_var.set(order["is_urgent"] if "is_urgent" in order.keys() and order["is_urgent"] is not None else 0)
            self.e_fabric.set(order["fabric_details"] if "fabric_details" in order.keys() and order["fabric_details"] else "")
            
            self.txt_remarks.insert("1.0", order["remarks"] or "")
            self._update_balance()

    def _save(self):
        try:
            total   = float(self.e_total.get() or 0)
            advance = float(self.e_advance.get() or 0)
            qty     = int(self.e_qty.get() or 1)
        except ValueError:
            messagebox.showerror("Invalid Input", "Total, Advance, and Quantity must be numbers.")
            return

        if advance > total:
            messagebox.showerror("Error", "Advance cannot be greater than Total Amount.")
            return

        data = {
            "suit_type":     self.suit_var.get(),
            "quantity":      qty,
            "status":        self.status_var.get(),
            "color":         self.e_color.get().strip(),
            "cuff_type":     self.cuff_om.get().strip(),
            "shalwar_bottom": self.shalwar_om.get().strip(),
            "kameez_bottom": self.kameez_om.get().strip(),
            "collar_type":   self.collar_om.get().strip(),
            "front_pocket":  self.front_pocket_om.get().strip(),
            "side_pocket":   self.side_pocket_om.get().strip(),
            "shalwar_pocket": self.shalwar_pocket_om.get().strip(),
            "order_date":    self.e_order_date.get().strip(),
            "delivery_date": self.e_delivery_date.get().strip() or None,
            "total_amount":  self.e_total.get().strip() or "0",
            "advance_paid":  self.e_advance.get().strip() or "0",
            "remarks":       self.txt_remarks.get("1.0", "end").strip(),
            "worker_name":   self.e_worker.get().strip(),
            "is_urgent":     self.urgent_var.get(),
            "fabric_details":self.e_fabric.get().strip(),
        }
        if not data["suit_type"]:
            messagebox.showerror("Validation", "Please select a suit type.", parent=self)
            return
        if not data["order_date"]:
            messagebox.showerror("Validation", "Please enter order date.", parent=self)
            return

        if self._editing:
            db.update_order(self.order_id, data)
        else:
            db.add_order(self.customer_id, data)

        if self.on_save_cb:
            self.on_save_cb()
        self.destroy()
