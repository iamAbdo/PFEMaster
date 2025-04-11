from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from tkinter import filedialog
from utils.pdf_helpers import RotatedText

class PDFExporter:
    def __init__(self, app):
        self.app = app
        self.styles = getSampleStyleSheet()
        self.a4_width = int(21/2.54*96)  # 794 pixels
        self.a4_height = int(29.7/2.54*96)  # 1123 pixels

    def export(self):
        """Main export method"""
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
            y_position = self.a4_height - margin
            
            # Draw header
            y_position = self._draw_header(pdf, y_position, margin)
            
            # Draw main content
            self._draw_columns(pdf, page, y_position, margin, line_height)
            
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

        header_data = [
            [ 
                Paragraph("EXPLORATION‐PRODUCTION Division Exploration Direction des Operations Exploration Dpt: Géologie HASSI ‐ MESSAOUD", para_style), 
                "", "", "", "", "",
                "Carotté : 18 m \nRécupéré : 18m soit 100% \nDate d'extraction de la carotte: 27/06/17", 
                "", "", "", "Puits :", "Nord West Trig-2" 
            ],
            [ "", "", "", "", "", "", "", "", "", "", "Sigle :", "NWT-2" ],
            [ "", "", "", "", "", "", "", "", "", "", "Permis :", "Ohanet II" ],
            [ "", "", "", "", "", "", "", "", "", "", "Bloc :", "234a" ],
            [ 
                Paragraph("Echelle : 1/40", para_style), "", "", "", "", "",
                Paragraph("Carottier: 12440525", para_style), "", "", 
                Paragraph("Type de Boue : OBM", para_style), "", "Carrote: 11" 
            ],
            [ "", "", "", "", "", "",
                Paragraph("Couronne: 6\" x 2 5/8\"", para_style), "", "", 
                Paragraph("D : 1,08", para_style), "", "Tete: 2930m" 
            ],
            [ "", "", "", "", "", "",
                Paragraph("Type: Ci3126", para_style), "", "", 
                Paragraph("FUN VIS (s/qt) : 46", para_style), "", "Pied: 3948m" 
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
            [ "Input", "Input", "Input", "Input", "Input", "Input", "Input", "Input", "Input", "Input", "", "" ]
        ]


        # Calculate dimensions
        total_width = self.a4_width - 2 * margin
        x = total_width / 24
        col_widths = [2*x] + [x]*6 + [2*x]*2 + [x*4] + [3*x] + [x*5]
        row_heights = [20, 15, 15, 15, 20, 20, 20, 15, 30, 20]

        # Create table
        table = Table(header_data, colWidths=col_widths, rowHeights=row_heights)
        
        # Apply table style (KEEP YOUR EXISTING TABLE STYLE COMMANDS)
        table.setStyle(TableStyle([
            # Row 0: Merge columns and rows (big blocks)
            ('SPAN', (0,0), (5,3)), # LOGO
            ('SPAN', (6,0), (9,3)), # Date et info
            # Row 4: merge columns (0-5, 6-8, 9-10)
            ('SPAN', (0,4), (5,6)), # Echele
            ('SPAN', (6,4), (8,4)), # carrotier
            ('SPAN', (9,4), (10,4)), # Type boue
            # Row 5 & 6: only one block per row (take 3 columns)
            ('SPAN', (6,5), (8,5)), # Couronne
            ('SPAN', (6,6), (8,6)), # Type
            # Row 7: merge columns 3-4 and 9-11.
            ('SPAN', (3,7), (4,7)), # indices
            ('SPAN', (9,7), (11,8)), # Description
            # Row 7 and 8: cells that take two rows: columns 0, 1, 5, 6.
            ('SPAN', (0,7), (0,8)), # Cotes
            ('SPAN', (1,7), (1,8)), # LOG
            ('SPAN', (5,7), (5,8)), # Fissures
            ('SPAN', (6,7), (6,8)), # Pondage
            # inputs
            ('SPAN', (9,9), (11,9)),

            ('GRID', (0,0), (-1,-1), 0.25, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTSIZE', (0,0), (-1,-1), 7),
        ]))

        # Draw table
        table.wrap(total_width, 0)
        table.drawOn(pdf, margin, y_position - table._height)
        return y_position - table._height - 10

    def _draw_columns(self, pdf, page, start_y, margin, line_height):
        """Draw the main content columns"""
        for col_num, text_widget in enumerate(page):
            content = text_widget.get("1.0", "end-1c")
            x_pos = sum(self.app.column_pixel_widths[:col_num]) + margin
            y_pos = start_y
            
            bold_ranges = self._get_bold_ranges(text_widget)
            
            for line in content.split('\n'):
                if y_pos < margin + 50:
                    pdf.showPage()
                    y_pos = self.a4_height - margin
                
                self._draw_line(pdf, line, x_pos, y_pos, bold_ranges)
                y_pos -= line_height

    def _get_bold_ranges(self, text_widget):
        """Detect bold text ranges"""
        bold_ranges = []
        start_idx = "1.0"
        while True:
            range_start = text_widget.tag_nextrange("bold", start_idx)
            if not range_start:
                break
            bold_ranges.append((
                text_widget.count("1.0", range_start[0], "chars")[0],
                text_widget.count("1.0", range_start[1], "chars")[0]
            ))
            start_idx = range_start[1]
        return bold_ranges

    def _draw_line(self, pdf, text, x, y, bold_ranges):
        """Draw a single line with bold formatting"""
        char_pos = 0
        while char_pos < len(text):
            in_bold = any(start <= char_pos < end for (start, end) in bold_ranges)
            
            if in_bold:
                pdf.setFont("Helvetica-Bold", self.app.root.taille)
                bold_end = min([end for (start, end) in bold_ranges if start <= char_pos < end])
                chunk = text[char_pos:bold_end]
            else:
                pdf.setFont("Helvetica", self.app.root.taille)
                next_bold = min([start for (start, end) in bold_ranges if start > char_pos], default=len(text))
                chunk = text[char_pos:next_bold]

            pdf.drawString(x, y, chunk)
            char_pos += len(chunk)
            x += pdf.stringWidth(chunk, "Helvetica", self.app.root.taille)