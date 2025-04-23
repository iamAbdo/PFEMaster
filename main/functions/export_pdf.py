from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from tkinter import filedialog
from utils.pdf_helpers import RotatedText
import tkinter as tk


class PDFExporter:
    def __init__(self, app):
        self.app = app
        self.styles = getSampleStyleSheet()
        # Use ReportLab's A4 dimensions (points)
        self.a4_width, self.a4_height = A4

    def export(self):
        """Main export method"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not file_path:
            return

        # Create the Canvas with A4 pagesize
        pdf = pdf_canvas.Canvas(file_path, pagesize=(self.a4_width, self.a4_height))
        margin = 40  # Adjust margin if necessary
        line_height = self.app.root.taille + 2

        # Process each page from the application
        for page_num, page in enumerate(self.app.pages):
            pdf.setPageSize((self.a4_width, self.a4_height))
            self._current_page_index = page_num
            y_position = self.a4_height - margin

            # Draw header and other content
            y_position = self._draw_header(pdf, y_position, margin)

            # Complete the current page
            pdf.showPage()


        # Append an extra, blank A4 page for comparison
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
            wordWrap='LTR'
        )

        def rotated_text(text):
            return RotatedText(text, angle=90)

        input_values = [tw.get("1.0", "end").strip() for tw in self.app.current_page]

        def get_paragraph_style(widget):
            """Helper function to get the correct style for the text"""
            try:
                start = widget.index("sel.first")
                end = widget.index("sel.last")
                current_tags = widget.tag_names(start)
            except tk.TclError:
                # If no text is selected, default to normal style
                return ParagraphStyle(name="Normal", fontName="Helvetica", fontSize=7)
            
            if "bold" in current_tags:
                return ParagraphStyle(name="Bold", fontName="Helvetica-Bold", fontSize=7)
            else:
                return ParagraphStyle(name="Normal", fontName="Helvetica", fontSize=7)


        header_data = [
            [ 
                Paragraph("EXPLORATION‐PRODUCTION Division Exploration Direction des Operations Exploration Dpt: Géologie HASSI ‐ MESSAOUD", para_style), 
                "", "", "", "", "",
                self.app.project_info["carotte_summary"], 
                "", "", "", 
                "Puits :", 
                self.app.project_info["puits"]
            ],
            [ 
                "", "", "", "", "", "", "", "", "", "", 
                "Sigle :", 
                self.app.project_info["sigle"]
            ],
            [ 
                "", "", "", "", "", "", "", "", "", "", 
                "Permis :", 
                self.app.project_info["permis"]
            ],
            [ 
                "", "", "", "", "", "", "", "", "", "", 
                "Bloc :", 
                self.app.project_info["bloc"]
            ],
            [ 
                Paragraph(f"Echelle : {self.app.project_info['echelle']}", para_style), 
                "", "", "", "", "",
                Paragraph(f"Carottier: {self.app.project_info['carottier']}", para_style), 
                "", "", 
                Paragraph(f"Type de Boue : {self.app.project_info['mud_type']}", para_style), 
                "", 
                f"Carrote: {self.app.project_info['carotte']}"
            ],
            [ 
                "", "", "", "", "", "",
                Paragraph(f"Couronne: {self.app.project_info['couronne']}", para_style), 
                "", "", 
                Paragraph(f"D : {self.app.project_info['d_value']}", para_style), 
                "", 
                f"Tete: {self.app.project_info['tete']}"
            ],
            [ 
                "", "", "", "", "", "",
                Paragraph(f"Type: {self.app.project_info['core_type']}", para_style), 
                "", "", 
                Paragraph(f"FUN VIS (s/qt) : {self.app.project_info['fun_vis']}", para_style), 
                "", 
                f"Pied: {self.app.project_info['pied']}"
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


        # get_paragraph_style(self.app.current_page[0])
        # Calculate dimensions
        total_width = self.a4_width - 2 * margin
        x = total_width / 24
        col_widths = [2*x] + [x]*6 + [2*x]*2 + [x*4] + [3*x] + [x*5]

        header_row_heights = [20, 15, 15, 15, 20, 20, 20, 15, 30]

        sum_header_row_heights = sum(header_row_heights)
        available_height = self.a4_height - margin*2 - sum_header_row_heights
        last_row_height = max(available_height, 0)
        row_heights = header_row_heights + [last_row_height]

        # Create table
        table = Table(header_data, colWidths=col_widths, rowHeights=row_heights)

        # Apply table style commands
        table.setStyle(TableStyle([
            # Row 0: Merge columns and rows (big blocks)
            ('SPAN', (0,0), (5,3)),  # LOGO
            ('SPAN', (6,0), (9,3)),  # Date and info
            # Row 4: Merge columns (0-5, 6-8, 9-10)
            ('SPAN', (0,4), (5,6)),  # Echelle
            ('SPAN', (6,4), (8,4)),  # Carottier
            ('SPAN', (9,4), (10,4)), # Type de Boue
            # Row 5 & 6: Single block per row (spanning three columns)
            ('SPAN', (6,5), (8,5)),  # Couronne
            ('SPAN', (6,6), (8,6)),  # Type
            # Row 7: Merge columns 3-4 and 9-11.
            ('SPAN', (3,7), (4,7)),  # Indices
            ('SPAN', (9,7), (11,8)), # Description
            # Row 7 and 8: Cells spanning two rows: columns 0, 1, 5, 6.
            ('SPAN', (0,7), (0,8)),  # Côtes
            ('SPAN', (1,7), (1,8)),  # Log
            ('SPAN', (5,7), (5,8)),  # Fissures
            ('SPAN', (6,7), (6,8)),  # Pendage
            # Inputs row
            ('SPAN', (9,9), (11,9)),

            ('GRID', (0,0), (-1,-1), 0.25, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTSIZE', (0,0), (-1,-1), 7),
        ]))

        
        # Draw the table on the PDF
        table.wrap(total_width, 0)

        table_bottom_y = y_position - table._height
        table.drawOn(pdf, margin, table_bottom_y)

        # diagnostic backgrounds
        first_col_width = table._colWidths[0]; last_row_height = table._rowHeights[-1]
        pdf.setFillColor(colors.red); pdf.rect(margin, table_bottom_y, first_col_width, last_row_height, stroke=0, fill=1); pdf.setFillColor(colors.black)
        x_log_col = margin + first_col_width; log_width = table._colWidths[1]
        pdf.setFillColor(colors.cyan); pdf.rect(x_log_col, table_bottom_y, log_width, last_row_height, stroke=0, fill=1); pdf.setFillColor(colors.black)

        # draw overlays
        self._draw_pdf_ruler(pdf, margin, table_bottom_y, first_col_width, last_row_height)
        self._draw_pdf_log_boxes(pdf, x_log_col, table_bottom_y, log_width, last_row_height)


        return table_bottom_y - 10
    
    def _draw_pdf_squares(self, pdf, x_start, y_start, width, height):
        """
        Tile the given rectangle (x_start→x_start+width,
        y_start→y_start+height) with perfect squares of side=width.
        """
        # how many full squares fit vertically?
        pdf.setLineWidth(0.25)
        num = int(height // width)
        for i in range(num):
            y = y_start + i * width
            # draw one square
            pdf.rect(x_start, y, width, width, stroke=1, fill=0)
    
    def _draw_pdf_ruler(self, pdf, x_start, y_start, width, height):
        """Draw ruler markings directly on the PDF canvas"""
        division_height = height / 9
        line_end = x_start + width

        # Draw background box (already drawn in header) if needed

        for j in range(9):
            y_pos = y_start + height - j * division_height

            # Main bold line
            pdf.setLineWidth(1.5)
            pdf.line(line_end - 15, y_pos, line_end, y_pos)

            # Subdivisions
            pdf.setLineWidth(0.5)
            for k in range(1, 5):
                sub_y = y_pos - (k * division_height/5)
                pdf.line(line_end - 8, sub_y, line_end, sub_y)

            # Number labels: invert numbers
            pdf.setFont("Helvetica", 8)
            label = str(3000 + j )
            if j==0: 
                pdf.drawRightString(line_end - 18, y_pos - 12, label)
            else:
                pdf.drawRightString(line_end - 18, y_pos - 2, label)
            print(f"number {label} at: {y_pos}")

        # Last line
        y_pos = y_start + height - 9 * division_height
        pdf.setLineWidth(1.5)
        pdf.line(line_end - 15, y_pos, line_end, y_pos)
        # Number labels: invert numbers
        pdf.setFont("Helvetica", 8)
        label = str( 3000 + 9 )
        pdf.drawRightString(line_end - 18, y_pos + 12, label)

        # Final top line of the ruler
        pdf.setLineWidth(1.5)
        pdf.line(line_end - 15, y_start + height, line_end, y_start + height)

    def _draw_pdf_log_boxes(self, pdf, x_start, y_start, width, height):
        """
        Draw one rectangle per on-screen log-box. Add a white filler box as the last entry in page_data['boxes'] if needed.
        """
        from reportlab.lib.colors import HexColor
        pdf.setLineWidth(0.25)
        page_data = self.app.log_boxes[self._current_page_index]

        # compute total GUI height
        gui_heights = [entry["frame"].winfo_height() for entry in page_data["boxes"]]
        gui_total = sum(h for h in gui_heights if h > 0)
        scale = 0.7 #(height / gui_total) if gui_total > 0 else 1

        # compute leftover PDF space
        pdf_filled = sum(h * scale for h in gui_heights)
        leftover = height - pdf_filled
        if leftover > 0:
            # add a dummy white box entry
            dummy_gui_h = leftover / scale
            class DummyFrame:
                def __init__(self, h): self._h = h; self.bg_color = "#ffffff"
                def winfo_height(self): return self._h
            page_data["boxes"].append({"frame": DummyFrame(dummy_gui_h)})

        # now draw all boxes, bottom-up
        y = y_start
        for entry in page_data["boxes"][::-1]:
            gui_h = entry["frame"].winfo_height()
            h_pdf = gui_h * scale
            col = getattr(entry["frame"], "bg_color", None)
            if col:
                pdf.setFillColor(HexColor(col)); pdf.rect(x_start, y, width, h_pdf, stroke=1, fill=1); pdf.setFillColor(colors.black)
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