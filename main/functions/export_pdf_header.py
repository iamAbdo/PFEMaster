#      _    _     _____ ____ _____ 
#     / \  | |   | ____|  _ \_   _|
#    / _ \ | |   |  _| | |_) || |  
#   / ___ \| |___| |___|  _ < | |  
#  /_/   \_\_____|_____|_| \_\|_|  
#
#   This code is not used (its just a copy)
#

from reportlab.platypus.flowables import Flowable

class RotatedText(Flowable):
    def __init__(self, text, angle=90):
        Flowable.__init__(self)
        self.text = text
        self.angle = angle

    def draw(self):
        canvas = self.canv
        canvas.saveState()
        # Rotate from bottom-left corner
        canvas.rotate(self.angle)
        canvas.drawString(0, 0, self.text)
        canvas.restoreState()

    def wrap(self, *args):
        # Return dimensions needed for this flowable
        canvas = self.canv
        font_size = canvas._fontsize
        width = font_size
        height = canvas.stringWidth(self.text)  # Text length becomes height
        return width, height

def export_pdf_header(self, pdf, a4_width, y_position, margin):
    """Draw a header table at the given y_position on the PDF canvas.
        Returns the new y_position after drawing the header.
        
        Todo:
            - Fix merged cells - DONE
            - Verical Text - DONE
            - Text wraping 
            - Add styling
            - Add image
    """
    from reportlab.platypus import Table, TableStyle, Paragraph
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.enums import TA_CENTER

    def rotated_text(text, font_size=7):
        """Create properly rotated text element"""
        style = getSampleStyleSheet()['Normal']
        style.fontSize = font_size
        return RotatedText(text, angle=90)
    
    # Define paragraph style for wrapped text
    styles = getSampleStyleSheet()
    para_style = ParagraphStyle(
        'WrappedText',
        parent=styles['Normal'],
        fontSize=7,
        leading=8,
        alignment=TA_CENTER,
        wordWrap='LTR'
    )
    

    # Define table data (each row has 12 columns).
    # Empty strings for cells that are merged
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

    # Determine total available width (SOME HOW THIS WORKS!).
    total_width = a4_width - 2 * margin

    # Define row heights (last 6 columns dboule first 6 width)
    x = total_width / 24
    col_widths = [2*x] + [x] * 6 + [2*x] * 2 + [x*4] + [3*x] + [x*5]

    # # text vertical
    # col_widths[5] = 10  # Fissures column
    # col_widths[6] = 10  # Pendage column
    # col_widths[2] = 10  # Echant column
    # col_widths[3] = 10  # direct column
    # col_widths[4] = 10  # Indir. column

    # Define row heights (to be adjusted later)
    row_heights = [20, 15, 15, 15, 20, 20, 20, 15, 30, 20]

    # Create the Table
    table = Table(header_data, colWidths=col_widths, rowHeights=row_heights)

    # Apply spans to table
    style = TableStyle([
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
    ])
    table.setStyle(style)


    # Wrap the table to determine its height.
    table_width, table_height = table.wrap(total_width, 0)
    # Draw the table on the PDF at the specified y_position
    # (The table will be drawn inside the margins.)
    table.drawOn(pdf, margin, y_position - table_height)

    # Return the new y_position (subtract table height plus some spacing)
    return y_position - table_height - 10
