"""
ui/pages/print_receipt.py  –  Order receipt printer
Generates a text/PDF-style receipt for any order
"""
import customtkinter as ctk
import os
import tkinter.font as tkfont
from tkinter import messagebox, filedialog
from ui.theme import *
from database import db_manager as db
from datetime import datetime


class PrintReceiptDialog(ctk.CTkToplevel):
    """Shows a formatted order receipt and allows saving to text file."""

    def __init__(self, master, order_id: int):
        super().__init__(master)
        self.order_id = order_id
        self.title("🧾  Order Receipt")
        self.geometry("520x680")
        self.resizable(False, False)
        self.configure(fg_color=CLR_BG)
        self.grab_set()

        order  = db.get_order_by_id(order_id)
        cust   = db.get_customer_by_id(order["customer_id"]) if order else None
        meas   = db.get_measurements(order["customer_id"]) if order else None

        self._receipt_text = self._build_receipt(order, cust, meas)
        self._build_ui()
        self.lift()
        self.focus()

    def _build_receipt(self, order, cust, meas) -> str:
        sep  = "─" * 48
        sep2 = "═" * 48
        now  = datetime.now().strftime("%Y-%m-%d %H:%M")

        lines = [
            sep2,
            "       ✂  FAZIAN TAILOR SHOP",
            "       Expert Stitching Services",
            sep2,
            f"  Receipt Date : {now}",
            f"  Order #      : {order['id']:04d}",
            sep,
        ]

        if cust:
            lines += [
                f"  Customer     : {cust['name']}",
                f"  Phone        : {cust['phone']}",
                f"  Address      : {cust['address'] if cust['address'] else '—'}",
                sep,
            ]

        qty = order["quantity"] if "quantity" in order.keys() and order["quantity"] else 1
        lines += [
            f"  Suit Type    : {order['suit_type']}",
            f"  Quantity     : {qty}",
            f"  Order Date   : {order['order_date']}",
            f"  Delivery     : {order['delivery_date'] or '—'}",
            f"  Status       : {order['status']}",
            sep,
        ]

        if meas:
            lines.append("  MEASUREMENTS (inches)")
            lines.append(sep)
            meas_pairs = [
                ("Length",             meas["length"]),
                ("Shoulder",           meas["shoulder"]),
                ("Neck",               meas["neck"]),
                ("Chest",              meas["chest"]),
                ("Waist",              meas["waist"]),
                ("Sleeves",            meas["sleeves"]),
                ("Armhole",            meas["armhole"]),
                ("Bottom / Ghera",     meas["bottom_ghera"]),
                ("Trouser Length",     meas["trouser_length"]),
                ("Trouser Poncha",     meas["trouser_poncha"]),
            ]
            for label, val in meas_pairs:
                v = f'{val}"' if val is not None else "—"
                lines.append(f"  {label:<20} {v}")
                
            # Add Style Fields
            lines.append(sep)
            lines.append("  STYLE / PREFERENCES")
            lines.append(sep)
            color = order["color"] if "color" in order.keys() and order["color"] else None
            o_collar = order["collar_type"] if "collar_type" in order.keys() and order["collar_type"] else meas["collar_type"] if meas["collar_type"] else None
            o_cuffs = order["cuff_type"] if "cuff_type" in order.keys() and order["cuff_type"] else meas["cuffs"] if meas["cuffs"] else None
            o_front = order["front_pocket"] if "front_pocket" in order.keys() and order["front_pocket"] else meas["front_pocket"] if meas["front_pocket"] else None
            o_side = order["side_pocket"] if "side_pocket" in order.keys() and order["side_pocket"] else meas["side_pocket"] if meas["side_pocket"] else None
            o_shal = order["shalwar_pocket"] if "shalwar_pocket" in order.keys() and order["shalwar_pocket"] else meas["shalwar_pocket"] if meas["shalwar_pocket"] else None
            shal_bot = order["shalwar_bottom"] if "shalwar_bottom" in order.keys() and order["shalwar_bottom"] else None
            kam_bot = order["kameez_bottom"] if "kameez_bottom" in order.keys() and order["kameez_bottom"] else None
            
            style_pairs = [
                ("Color", color),
                ("Collar / Baan", o_collar),
                ("Cuffs", o_cuffs),
                ("Front Pocket", o_front),
                ("Side Pocket", o_side),
                ("Shalwar Pocket", o_shal),
                ("Shalwar Bottom", shal_bot),
                ("Kameez Bottom", kam_bot),
            ]
            for label, val in style_pairs:
                v = val if val else "—"
                lines.append(f"  {label:<20} {v}")

            if meas["special_notes"]:
                lines.append(sep)
                lines.append("  Special Notes:")
                lines.append(f"  {meas['special_notes']}")

        lines += [
            sep,
            "  FINANCIAL SUMMARY",
            sep,
            f"  Total Amount  :  Rs {order['total_amount']:>10,.0f}",
            f"  Advance Paid  :  Rs {order['advance_paid']:>10,.0f}",
            f"  Balance Due   :  Rs {order['remaining']:>10,.0f}",
            sep2,
            "     Thank you for choosing Fazian Tailor!",
            sep2,
        ]

        if order["remarks"]:
            lines += ["", f"  Note: {order['remarks']}"]

        return "\n".join(lines)

    def _build_ui(self):
        ctk.CTkLabel(self, text="🧾  Order Receipt",
                     font=FONT_HEADING, text_color=CLR_PRIMARY
                     ).pack(pady=(PAD, PAD_S), padx=PAD*2, anchor="w")

        # Receipt text box (monospaced)
        txt = ctk.CTkTextbox(self, font=("Courier New", 11),
                             fg_color=CLR_SURFACE, text_color=CLR_TEXT,
                             border_width=1, border_color=CLR_BORDER)
        txt.pack(fill="both", expand=True, padx=PAD, pady=PAD_S)
        txt.insert("1.0", self._receipt_text)
        txt.configure(state="disabled")

        # Action buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=PAD, padx=PAD)

        ctk.CTkButton(btn_row, text="💾  Save as PDF", width=160, height=36,
                      fg_color=CLR_PRIMARY, hover_color=CLR_PRIMARY_DK,
                      font=FONT_BODY,
                      command=self._save_pdf).pack(side="left", padx=PAD_S)

        ctk.CTkButton(btn_row, text="❌  Close", width=100, height=36,
                      fg_color=CLR_SURFACE2, hover_color=CLR_BORDER,
                      text_color=CLR_TEXT_MUTED, font=FONT_BODY,
                      command=self.destroy).pack(side="left")

    def _save_pdf(self):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF File", "*.pdf"), ("All Files", "*.*")],
                initialfile=f"receipt_order_{self.order_id:04d}.pdf",
                title="Save Receipt"
            )
            
            if not path:
                return
                
            doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            elements = []
            styles = getSampleStyleSheet()
            
            # Custom Styles
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontName='Helvetica-Bold',
                fontSize=24,
                textColor=colors.HexColor("#4F46E5"),
                alignment=1, # Center
                spaceAfter=6
            )
            subtitle_style = ParagraphStyle(
                'SubTitleStyle',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=12,
                textColor=colors.HexColor("#64748b"),
                alignment=1,
                spaceAfter=20
            )
            h2_style = ParagraphStyle(
                'H2Style',
                parent=styles['Heading2'],
                fontName='Helvetica-Bold',
                fontSize=14,
                textColor=colors.HexColor("#1e293b"),
                spaceAfter=10,
                spaceBefore=15
            )
            
            # Header
            elements.append(Paragraph("FAZIAN TAILOR SHOP", title_style))
            elements.append(Paragraph("Premium Stitching & Custom Alterations", subtitle_style))
            
            order = db.get_order_by_id(self.order_id)
            cust = db.get_customer_by_id(order["customer_id"]) if order else None
            meas = db.get_measurements(order["customer_id"]) if order else None
            
            # Order & Customer Info Table
            info_data = [
                [Paragraph("<b>Order Number:</b>", styles["Normal"]), f"#{order['id']:04d}", Paragraph("<b>Customer:</b>", styles["Normal"]), cust['name'] if cust else "—"],
                [Paragraph("<b>Order Date:</b>", styles["Normal"]), order['order_date'], Paragraph("<b>Phone:</b>", styles["Normal"]), cust['phone'] if cust else "—"],
                [Paragraph("<b>Delivery Date:</b>", styles["Normal"]), order['delivery_date'] or "—", Paragraph("<b>Suit Type:</b>", styles["Normal"]), f"{order.get('quantity', 1)}x {order['suit_type']}"],
            ]
            info_table = Table(info_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
                ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#334155")),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 11),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 15))
            
            # Measurements & Styles
            if meas:
                elements.append(Paragraph("Measurements & Specifications", h2_style))
                
                # Split into two columns for compact view
                m_labels = [
                    ("Length", meas["length"]), ("Trouser Length", meas["trouser_length"]),
                    ("Shoulder", meas["shoulder"]), ("Trouser Poncha", meas["trouser_poncha"]),
                    ("Neck", meas["neck"]), ("Collar / Baan", order.get("collar_type") or meas.get("collar_type")),
                    ("Chest", meas["chest"]), ("Cuffs", order.get("cuff_type") or meas.get("cuffs")),
                    ("Waist", meas["waist"]), ("Front Pocket", order.get("front_pocket") or meas.get("front_pocket")),
                    ("Sleeves", meas["sleeves"]), ("Side Pocket", order.get("side_pocket") or meas.get("side_pocket")),
                    ("Armhole", meas["armhole"]), ("Shalwar Pocket", order.get("shalwar_pocket") or meas.get("shalwar_pocket")),
                    ("Bottom / Ghera", meas["bottom_ghera"]), ("Color", order.get("color")),
                ]
                
                meas_data = []
                for i in range(0, len(m_labels), 2):
                    row = []
                    for j in range(2):
                        if i+j < len(m_labels):
                            lbl, val = m_labels[i+j]
                            v_str = str(val) if val is not None and val != "" else "—"
                            row.extend([Paragraph(f"<b>{lbl}</b>", styles["Normal"]), v_str])
                        else:
                            row.extend(["", ""])
                    meas_data.append(row)
                    
                meas_table = Table(meas_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                meas_table.setStyle(TableStyle([
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                    ('FONTSIZE', (0,0), (-1,-1), 10),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#f1f5f9")),
                ]))
                elements.append(meas_table)
                elements.append(Spacer(1, 15))
                
                if meas["special_notes"]:
                    elements.append(Paragraph("Special Instructions:", h2_style))
                    elements.append(Paragraph(meas["special_notes"], styles["Normal"]))
                    elements.append(Spacer(1, 15))
                    
            # Financials
            elements.append(Paragraph("Financial Summary", h2_style))
            fin_data = [
                ["Total Amount:", f"Rs {order['total_amount']:,.0f}"],
                ["Advance Paid:", f"Rs {order['advance_paid']:,.0f}"],
                ["Balance Due:", f"Rs {order['remaining']:,.0f}"]
            ]
            fin_table = Table(fin_data, colWidths=[5*inch, 2*inch])
            fin_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (0,-1), 'RIGHT'),
                ('ALIGN', (1,0), (1,-1), 'RIGHT'),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 12),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor("#e2e8f0")),
                ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
                ('TEXTCOLOR', (1,-1), (1,-1), colors.HexColor("#EF4444") if order['remaining'] > 0 else colors.HexColor("#10B981")),
            ]))
            elements.append(fin_table)
            
            if order["remarks"]:
                elements.append(Spacer(1, 20))
                elements.append(Paragraph(f"<b>Note:</b> {order['remarks']}", styles["Normal"]))
                
            elements.append(Spacer(1, 40))
            elements.append(Paragraph("Thank you for choosing Fazian Tailor!", subtitle_style))
            
            doc.build(elements)
            messagebox.showinfo("Saved", f"PDF Receipt saved to:\n{path}", parent=self)
            
        except ImportError:
            messagebox.showwarning("Missing Library", "ReportLab is not installed.\nSaving as .txt instead.", parent=self)
            self._save_txt()

    def _save_txt(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt"), ("All Files", "*.*")],
            initialfile=f"receipt_order_{self.order_id:04d}.txt",
            title="Save Receipt"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._receipt_text)
            messagebox.showinfo("Saved", f"Receipt saved to:\n{path}", parent=self)
