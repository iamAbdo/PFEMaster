from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from pathlib import Path 
from reportlab.platypus import Table, TableStyle, Image, Paragraph, KeepTogether
import os
from tkinter import filedialog, messagebox
from utils.pdf_helpers import RotatedText
import tkinter as tk
import requests
import json
from utils.settings import get_settings_file
from utils.auth_state import get_jwt_token_global
from datetime import datetime


class PDFExporter:
    def __init__(self, app):
        self.app = app
        self.styles = getSampleStyleSheet()
        self.a4_width, self.a4_height = A4

    def export(self):
        """Main export method with backend integration"""
        # Load settings to get save directory
        settings_path = get_settings_file()
        settings = {}
        if settings_path.exists():
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            except Exception:
                pass
        
        save_dir = settings.get('save_dir', str(Path.home() / 'Documents'))
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"export_{timestamp}.pdf"
        
        # Create the PDF in memory first
        pdf_data = self._create_pdf_in_memory()
        
        if not pdf_data:
            return
        
        # Save to local directory from settings
        local_path = Path(save_dir) / default_filename
        try:
            with open(local_path, 'wb') as f:
                f.write(pdf_data)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder le fichier localement : {e}")
            return
        
        # Send to backend
        success = self._send_to_backend(pdf_data, default_filename)
        
        if success:
            messagebox.showinfo("Succès", f"PDF exporté avec succès!\nSauvegardé dans : {local_path}")
        else:
            messagebox.showwarning("Attention", f"PDF sauvegardé localement mais erreur lors de l'envoi au serveur.\nFichier : {local_path}")

    def _create_pdf_in_memory(self):
        """Create PDF in memory and return the bytes"""
        try:
            from io import BytesIO
            buffer = BytesIO()
            
            pdf = pdf_canvas.Canvas(buffer, pagesize=(self.a4_width, self.a4_height))
            margin = 40
            line_height = self.app.root.taille + 2

            for page_num, page in enumerate(self.app.pages):
                pdf.setPageSize((self.a4_width, self.a4_height))
                self._current_page_index = page_num
                y_position = self.a4_height - margin

                y_position = self._draw_header(pdf, y_position, margin)
                pdf.showPage()

            pdf.setPageSize((self.a4_width, self.a4_height))
            pdf.showPage()
            pdf.save()
            
            return buffer.getvalue()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création du PDF : {e}")
            return None

    def _send_to_backend(self, pdf_data, filename):
        """Send PDF to backend"""
        try:
            token = get_jwt_token_global()
            if not token:
                return False
            
            # Prepare the file for upload
            from io import BytesIO
            files = {'file': (filename, BytesIO(pdf_data), 'application/pdf')}
            headers = {'Authorization': f'Bearer {token}'}
            
            # Send to backend using the export-pdf endpoint
            response = requests.post(
                'https://localhost:5000/api/user/files/export-pdf',
                files=files,
                headers=headers,
                verify=False  # For self-signed certificate
            )
            
            if response.status_code == 201:
                return True
            else:
                print(f"Backend error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending to backend: {e}")
            return False

    def export_legacy(self):
        """Legacy export method with file dialog"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not file_path:
            return

        pdf = pdf_canvas.Canvas(file_path, pagesize=(self.a4_width, self.a4_height))
        margin = 40
        line_height = self.app.root.taille + 2

        for page_num, page in enumerate(self.app.pages):
            pdf.setPageSize((self.a4_width, self.a4_height))
            self._current_page_index = page_num
            y_position = self.a4_height - margin

            y_position = self._draw_header(pdf, y_position, margin)
            pdf.showPage()

        pdf.setPageSize((self.a4_width, self.a4_height))
        pdf.showPage()
        pdf.save()

    def _draw_header(self, pdf, y_position, margin):
        """Draw the complex header table"""
        para_style = ParagraphStyle(
            'WrappedText',
            parent=self.styles['Normal'],
            fontSize=7,
            leading=8,
            alignment=TA_CENTER,
            wordWrap='LTR',
            fontName='Helvetica-Bold'
        )
        para_style2 = ParagraphStyle(
            'WrappedText',
            parent=self.styles['Normal'],
            fontSize=6,
            leading=8,
            alignment=TA_CENTER,
            wordWrap='LTR',
            fontName='Helvetica-Bold'
        )

        def rotated_text(text):
            return RotatedText(text, angle=90)

        input_values = [tw.get("1.0", "end").strip() for tw in self.app.current_page]

        def get_paragraph_style(widget):
            try:
                start = widget.index("sel.first")
                end = widget.index("sel.last")
                current_tags = widget.tag_names(start)
            except tk.TclError:
                return ParagraphStyle(name="Normal", fontName="Helvetica", fontSize=7)
            
            if "bold" in current_tags:
                return ParagraphStyle(name="Bold", fontName="Helvetica-Bold", fontSize=7)
            else:
                return ParagraphStyle(name="Normal", fontName="Helvetica", fontSize=7)

        # Handle the logo and header text
        current_script_dir = Path(__file__).parent
        project_root = current_script_dir.parent
        image_path = project_root / "images" / "Sonatrach.png"

        # get as
        logo_img = Image(str(image_path))
        img_width, img_height = logo_img.drawWidth, logo_img.drawHeight
        aspect_ratio = img_width / img_height

        total_height = 20 + 15 + 15 + 15
        logo_height = total_height - 5  # Leave some padding
        logo_width = logo_height * aspect_ratio
        
        logo = Image(str(image_path), width=logo_width, height=logo_height)
        header_content = [[logo, Paragraph("EXPLORATION‐PRODUCTION \nDivision Exploration Direction des Operations Exploration \nDpt: Géologie HASSI ‐ MESSAOUD", para_style)]]
       
        # 1. Create the image and paragraph
        logo = Image(str(image_path), width=logo_width, height=logo_height)
        text_para = Paragraph(
    "EXPLORATION-PRODUCTION <br/> Division Exploration Direction des Operations Exploration <br/> Dpt: Géologie HASSI - MESSAOUD", 
    para_style2
)

        # 2. Create a simple 2-column table for the image+text combo
        image_text_table = Table([
            [logo, text_para]
        ], colWidths=[logo_width, "*"])

        image_text_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))

        # Convert all values to Paragraphs or strings
        header_data = [
            [ 
                [image_text_table],
                "", "", "", "", "",
                Paragraph(str(self.app.project_info["carotte_summary"]), para_style), 
                "", "", "", 
                "Puits :", 
                Paragraph(str(self.app.project_info["puits"]), para_style)
            ],
            [ 
                "", "", "", "", "", "", "", "", "", "", 
                "Sigle :", 
                Paragraph(str(self.app.project_info["sigle"]), para_style)
            ],
            [ 
                "", "", "", "", "", "", "", "", "", "", 
                "Permis :", 
                Paragraph(str(self.app.project_info["permis"]), para_style)
            ],
            [ 
                "", "", "", "", "", "", "", "", "", "", 
                "Bloc :", 
                Paragraph(str(self.app.project_info["bloc"]), para_style)
            ],
            [ 
                Paragraph(f"Echelle : {self.app.project_info['echelle']}", para_style), 
                "", "", "", "", "",
                Paragraph(f"Carottier: {self.app.project_info['carottier']}", para_style), 
                "", "", 
                Paragraph(f"Type de Boue : {self.app.project_info['mud_type']}", para_style), 
                "", 
                Paragraph(f"Carrote: {self.app.project_info['carotte']}", para_style)
            ],
            [ 
                "", "", "", "", "", "",
                Paragraph(f"Couronne: {self.app.project_info['couronne']}", para_style), 
                "", "", 
                Paragraph(f"D : {self.app.project_info['d_value']}", para_style), 
                "", 
                Paragraph(f"Tete: {self.app.project_info['tete']}", para_style)
            ],
            [ 
                "", "", "", "", "", "",
                Paragraph(f"Type: {self.app.project_info['core_type']}", para_style), 
                "", "", 
                Paragraph(f"FUN VIS (s/qt) : {self.app.project_info['fun_vis']}", para_style), 
                "", 
                Paragraph(f"Pied: {self.app.project_info['pied']}", para_style)
            ],
            ["Côtes (m)", "Log", "Nº", "INDICES", "", 
                rotated_text("Fissures"), 
                rotated_text("Pendage"), 
                "Calcimètrie", "Age",
                Paragraph("DESCRIPTION LITHOLOGIQUE & OBSERVATIONS", para_style), "", ""],
            ["", "", 
                rotated_text("Echant"), 
                rotated_text("direct"), 
                rotated_text("Indir."), 
                "", "", "25", "75", "", "", ""],
            ["", ""] + [Paragraph(val, get_paragraph_style(self.app.current_page[index])) if val else "" for index, val in enumerate(input_values)] + ["", ""]
        ]

        total_width = self.a4_width - 2 * margin
        x = total_width / 24
        col_widths = [2*x] + [x]*6 + [2*x]*2 + [x*4] + [3*x] + [x*5]
        header_row_heights = [20, 15, 15, 15, 20, 20, 20, 15, 30]
        sum_header_row_heights = sum(header_row_heights)
        available_height = self.a4_height - margin*2 - sum_header_row_heights
        last_row_height = max(available_height, 0)
        row_heights = header_row_heights + [last_row_height]

        table = Table(header_data, colWidths=col_widths, rowHeights=row_heights)
        table.setStyle(TableStyle([
            ('SPAN', (0,0), (5,3)),
            ('SPAN', (6,0), (9,3)),
            ('SPAN', (0,4), (5,6)),
            ('SPAN', (6,4), (8,4)),
            ('SPAN', (9,4), (10,4)),
            ('SPAN', (6,5), (8,5)),
            ('SPAN', (6,6), (8,6)),
            ('SPAN', (3,7), (4,7)),
            ('SPAN', (9,7), (11,8)),
            ('SPAN', (0,7), (0,8)),
            ('SPAN', (1,7), (1,8)),
            ('SPAN', (5,7), (5,8)),
            ('SPAN', (6,7), (6,8)),
            ('SPAN', (9,9), (11,9)),
            ('GRID', (0,0), (-1,-1), 0.25, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTSIZE', (0,0), (-1,-1), 7),
        ]))

        table.wrap(total_width, 0)
        table_bottom_y = y_position - table._height
        table.drawOn(pdf, margin, table_bottom_y)

        first_col_width = table._colWidths[0]
        last_row_height = table._rowHeights[-1]
        pdf.rect(margin, table_bottom_y, first_col_width, last_row_height, stroke=0, fill=0)
        x_log_col = margin + first_col_width
        log_width = table._colWidths[1]
        pdf.setFillColor(colors.cyan)
        pdf.rect(x_log_col, table_bottom_y, log_width, last_row_height, stroke=0, fill=1)
        pdf.setFillColor(colors.black)

        self._draw_pdf_ruler(pdf, margin, table_bottom_y, first_col_width, last_row_height)
        self._draw_pdf_log_boxes(pdf, x_log_col, table_bottom_y, log_width, last_row_height)

        return table_bottom_y - 10
    def _draw_pdf_squares(self, pdf, x_start, y_start, width, height):
        num = int(height // width)
        for i in range(num):
            y = y_start + i * width
            pdf.rect(x_start, y, width, width, stroke=1, fill=0)
    
    def _draw_pdf_ruler(self, pdf, x_start, y_start, width, height):
        division_height = height / 9
        line_end = x_start + width

        for j in range(9):
            y_pos = y_start + height - j * division_height
            pdf.setLineWidth(1.5)
            pdf.line(line_end - 15, y_pos, line_end, y_pos)
            pdf.setLineWidth(0.5)
            for k in range(1, 5):
                sub_y = y_pos - (k * division_height/5)
                pdf.line(line_end - 8, sub_y, line_end, sub_y)
            pdf.setFont("Helvetica", 8)
            label = str(self.app.TeteStart + j)
            if j==0: 
                pdf.drawRightString(line_end - 18, y_pos - 12, label)
            else:
                pdf.drawRightString(line_end - 18, y_pos - 2, label)

        y_pos = y_start + height - 9 * division_height
        pdf.setLineWidth(1.5)
        pdf.line(line_end - 15, y_pos, line_end, y_pos)
        pdf.setFont("Helvetica", 8)
        label = str(self.app.TeteStart + 9)
        pdf.drawRightString(line_end - 18, y_pos + 12, label)
        pdf.setLineWidth(1.5)
        pdf.line(line_end - 15, y_start + height, line_end, y_start + height)

    def _draw_pdf_log_boxes(self, pdf, x_start, y_start, width, height):
        from reportlab.lib.colors import HexColor
        pdf.setLineWidth(0.25)
        page_data = self.app.log_boxes[self._current_page_index]

        gui_heights = [entry["frame"].winfo_height() for entry in page_data["boxes"]]
        scale = 0.714

        pdf_filled = sum(h * scale for h in gui_heights)
        leftover = height - pdf_filled
        if leftover > 0:
            dummy_gui_h = leftover / scale
            class DummyFrame:
                def __init__(self, h): self._h = h; self.bg_color = "#ffffff"
                def winfo_height(self): return self._h
            page_data["boxes"].append({"frame": DummyFrame(dummy_gui_h)})

        y = y_start
        for entry in page_data["boxes"][::-1]:
            gui_h = entry["frame"].winfo_height()
            h_pdf = gui_h * scale
            col = getattr(entry["frame"], "bg_color", None)
            if col:
                pdf.setFillColor(HexColor(col))
                pdf.rect(x_start, y, width, h_pdf, stroke=1, fill=1)
                pdf.setFillColor(colors.black)
            else:
                pdf.rect(x_start, y, width, h_pdf, stroke=1, fill=0)
            y += h_pdf


    #   _   _ _   _ _   _ ____  _____ ____         ____ ___  ____  _____ 
    #  | | | | \ | | | | / ___|| ____|  _ \       / ___/ _ \|  _ \| ____|
    #  | | | |  \| | | | \___ \|  _| | | | |     | |  | | | | | | |  _|  
    #  | |_| | |\  | |_| |___) | |___| |_| |     | |__| |_| | |_| | |___ 
    #   \___/|_| \_|\___/|____/|_____|____/       \____\___/|____/|_____|
    #
                                                               

    # def _draw_columns(self, pdf, page, start_y, margin, line_height):
    #     """Draw the main content columns"""
    #     for col_num, text_widget in enumerate(page):
    #         content = text_widget.get("1.0", "end-1c")
    #         x_pos = sum(self.app.column_pixel_widths[:col_num]) + margin
    #         y_pos = start_y
            
    #         bold_ranges = self._get_bold_ranges(text_widget)
            
    #         for line in content.split('\n'):
    #             if y_pos < margin + 50:
    #                 pdf.showPage()
    #                 y_pos = self.a4_height - margin
                
    #             self._draw_line(pdf, line, x_pos, y_pos, bold_ranges)
    #             y_pos -= line_height

    # def _get_bold_ranges(self, text_widget):
    #     """Detect bold text ranges"""
    #     bold_ranges = []
    #     start_idx = "1.0"
    #     while True:
    #         range_start = text_widget.tag_nextrange("bold", start_idx)
    #         if not range_start:
    #             break
    #         bold_ranges.append((
    #             text_widget.count("1.0", range_start[0], "chars")[0],
    #             text_widget.count("1.0", range_start[1], "chars")[0]
    #         ))
    #         start_idx = range_start[1]
    #     return bold_ranges

    # def _draw_line(self, pdf, text, x, y, bold_ranges):
    #     """Draw a single line with bold formatting"""
    #     char_pos = 0
    #     while char_pos < len(text):
    #         in_bold = any(start <= char_pos < end for (start, end) in bold_ranges)
            
    #         if in_bold:
    #             pdf.setFont("Helvetica-Bold", self.app.root.taille)
    #             bold_end = min([end for (start, end) in bold_ranges if start <= char_pos < end])
    #             chunk = text[char_pos:bold_end]
    #         else:
    #             pdf.setFont("Helvetica", self.app.root.taille)
    #             next_bold = min([start for (start, end) in bold_ranges if start > char_pos], default=len(text))
    #             chunk = text[char_pos:next_bold]

    #         pdf.drawString(x, y, chunk)
    #         char_pos += len(chunk)
    #         x += pdf.stringWidth(chunk, "Helvetica", self.app.root.taille)