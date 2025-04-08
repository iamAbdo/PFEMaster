import tkinter as tk

from tkinter import ttk, font as tkfont, filedialog
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas

from reportlab.platypus.flowables import Flowable
from reportlab.lib.units import mm

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

class WordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Application")
        self.root.state('zoomed')  
        
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.header_frame = ttk.Frame(self.root, height=80, style='Header.TFrame')
        self.header_frame.grid(row=0, column=0, sticky="nsew")
        
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        
        self.pages = []
        self.bold_on = False
        self.current_font = ("Arial", 12)
        self.taille = 12
        self.current_page = None 
        
        self.setup_styles()
        self.add_controls()
        
        self.setup_canvas()
        self.add_new_page()
        
        
    def setup_styles(self):
        """configure styling (like class's in css)"""
        style = ttk.Style()
        style.configure('Header.TFrame', background='#f0f0f0')
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'), padding=6)
        style.map('Primary.TButton',
                background=[('active', 'red'), ('!active', 'red')],
                foreground=[('active', 'black'), ('!active', 'black')])
        
    def add_controls(self):
        """Add control buttons to header with styling"""
        control_frame = ttk.Frame(self.header_frame)
        control_frame.pack(pady=10, padx=20, side=tk.LEFT)
        
        ttk.Button(control_frame, text="New Page", command=self.add_new_page,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        self.bold_btn = ttk.Button(control_frame, text="Bold", command=self.toggle_bold,
                                  style='Primary.TButton')
        self.bold_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Insert Table", command=self.insert_table,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Export PDF", command=self.export_pdf,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        
        spin_var = tk.IntVar(value=12)
        spin_rows = ttk.Spinbox(control_frame, from_=1, to=64, textvariable=spin_var).pack(side=tk.LEFT)
        
        spin_var.trace_add('write', lambda *args: self.EditSize(spin_var.get()))
        self.bold_on = False

    def EditSize(self, taille):
        self.root.taille = taille
        if self.current_page:
            self.current_page.configure(font=('Arial', self.root.taille))
            self.current_page.tag_configure("bold", font=('Arial', self.root.taille, 'bold'))
        
    def setup_canvas(self):
        """Configure scrollable canvas with centered pages"""
        self.canvas = tk.Canvas(self.content_frame, bg='#f5f5f5', highlightthickness=0)
        self.v_scroll = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.canvas.yview)
        
        self.canvas.configure(yscrollcommand=self.v_scroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Create centered container for pages
        self.container = ttk.Frame(self.canvas)
        self.canvas.create_window(
            (self.canvas.winfo_width()//2, 20), 
            window=self.container, 
            anchor="n",
            tags="container"
        )
        
        # events to update stuff
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.container.bind("<Configure>", self.on_frame_configure)

    def toggle_bold(self):
        """Toggle bold formatting state"""
        # TO DO: needs to work on export pdf !
        self.bold_on = not self.bold_on
        self.bold_btn.state(['pressed' if self.bold_on else '!pressed'])

    def create_header_table(self, parent, max_width):
        """
        Create the header

        TO DO: 
        - Style it
        - Fix width
        """
        header = tk.Frame(parent, width=max_width)
        # Width Fix attempt 1 (Calculate cell width based 12 columns)
        cell_width = int(max_width / 12)

        # 'wraplength=cell_width' to set width according to AI
        tk.Label(header,
                 text="EXPLORATION‐PRODUCTION\nDivision Exploration\nDirection des\nOperations\nExploration\nDpt: Géologie\nHASSI ‐ MESSAOUD",
                 relief="solid", borderwidth=1, padx=5, pady=5, anchor="w", justify="left")\
           .grid(row=0, column=0, columnspan=6, rowspan=4, sticky="nsew")
        tk.Label(header,
                 text="Carotté : 18 m\nRécupéré : 18m soit 100%\nDate d'extraction de la carotte: 27/06/17",
                 relief="solid", borderwidth=1, padx=5, pady=5, anchor="w", justify="left")\
           .grid(row=0, column=6, columnspan=4, rowspan=4, sticky="nsew")
        tk.Label(header, text="Puits :", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=0, column=10, sticky="nsew")
        tk.Label(header, text="Nord West Trig-2", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=0, column=11, sticky="nsew")

        # Row 2
        tk.Label(header, text="Sigle :", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=1, column=10, sticky="nsew")
        tk.Label(header, text="NWT-2", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=1, column=11, sticky="nsew")

        # Row 3
        tk.Label(header, text="Permis :", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=2, column=10, sticky="nsew")
        tk.Label(header, text="Ohanet II", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=2, column=11, sticky="nsew")

        # Row 4
        tk.Label(header, text="Bloc :", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=3, column=10, sticky="nsew")
        tk.Label(header, text="234a", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=3, column=11, sticky="nsew")

        # Row 5
        tk.Label(header, text="Echelle : 1/40", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=4, column=0, columnspan=6, rowspan=3, sticky="nsew")
        tk.Label(header, text="Carottier: 12440525", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=4, column=6, columnspan=3, sticky="nsew")
        tk.Label(header, text="Type de Boue : OBM", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=4, column=9, columnspan=2, sticky="nsew")
        tk.Label(header, text="Carrote: 11", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=4, column=11, sticky="nsew")

        # Row 6
        tk.Label(header, text='Couronne: 6" x 2 5/8"', relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=5, column=6, columnspan=3, sticky="nsew")
        tk.Label(header, text="D : 1,08", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=5, column=9, sticky="nsew")
        tk.Label(header, text="Tete: ", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=5, column=10, sticky="nsew")
        tk.Label(header, text="2930m", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=5, column=11, sticky="nsew")

        # Row 7
        tk.Label(header, text="Type: Ci3126", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=6, column=6, columnspan=3, sticky="nsew")
        tk.Label(header, text="FUN VIS (s/qt) : 46", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=6, column=9, sticky="nsew")
        tk.Label(header, text="Pied:", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=6, column=10, sticky="nsew")
        tk.Label(header, text="3948m", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=6, column=11, sticky="nsew")

        # Row 8
        tk.Label(header, text="Côtes (m)", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=7, column=0, rowspan=2, sticky="nsew")
        tk.Label(header, text="Log", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=7, column=1, rowspan=2, sticky="nsew")
        tk.Label(header, text="Nº", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=7, column=2, sticky="nsew")
        tk.Label(header, text="INDICES", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=7, column=3, columnspan=2, sticky="nsew")
        tk.Label(header, text="Fissures", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=7, column=5, rowspan=2, sticky="nsew")
        tk.Label(header, text="Pendage", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=7, column=6, rowspan=2, sticky="nsew")
        tk.Label(header, text="Calcimètrie", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=7, column=7, sticky="nsew")
        tk.Label(header, text="Age", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=7, column=8, sticky="nsew")
        tk.Label(header, text="D E S C R I P T I O N L I T H O L O G I Q U E & O B S E R V A T I O N S", 
                 relief="solid", borderwidth=1, padx=5, pady=5, anchor="w", justify="left")\
           .grid(row=7, column=9, columnspan=3, rowspan=2, sticky="nsew")

        # Row 9
        tk.Label(header, text="Echan", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=8, column=2, sticky="nsew")
        tk.Label(header, text="direct", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=8, column=3, sticky="nsew")
        tk.Label(header, text="Indir", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=8, column=4, sticky="nsew")
        tk.Label(header, text="25", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=8, column=7, sticky="nsew")
        tk.Label(header, text="75", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=8, column=8, sticky="nsew")

        # Row 10: Input row.
        for col in range(9):
            tk.Label(header, text="Input", relief="solid", borderwidth=1, padx=5, pady=5,
                     wraplength=cell_width)\
               .grid(row=9, column=col, sticky="nsew")
        tk.Label(header, text="Input", relief="solid", borderwidth=1, padx=5, pady=5)\
           .grid(row=9, column=9, columnspan=3, sticky="nsew")

        # Configure grid weight=1 now so each column/row expands equally.
        for col in range(12):
            header.grid_columnconfigure(col, weight=1)
        for row in range(10):
            header.grid_rowconfigure(row, weight=1)

        return header

    def add_new_page(self):
        """
        Create a new centered A4 page and add the header.
        
        Todo:
            - Adding zoom meaning could effect size
            - Remove add button after adding (max pages is 2)
        """
        # A4 dimensions in pixels (21cm x 29.7cm at 96dpi)
        a4_width, a4_height = int(21/2.54*96), int(29.7/2.54*96)

        # Page frame
        page_frame = ttk.Frame(self.container)
        page_frame.pack(pady=20, expand=True)

        # Create page canvas with A4 dimensions
        page_canvas = tk.Canvas(page_frame, width=a4_width, height=a4_height,
                                bg="white", highlightthickness=0)
        page_canvas.pack()

        # shadow effect
        page_canvas.create_rectangle(2, 2, a4_width+2, a4_height+2, fill='#e0e0e0', outline='')
        page_canvas.create_rectangle(0, 0, a4_width, a4_height, fill="white")

        # text inpit with margins
        text_widget = tk.Text(page_canvas, wrap="word", bg="white", bd=0,
                              font=('Arial', self.taille), padx=20, pady=50)
        text_widget.place(x=0, y=0, width=a4_width, height=a4_height)

        # Get width and add header
        available_width = a4_width - 40 
        header_frame = self.create_header_table(text_widget, available_width)
        text_widget.window_create("1.0", window=header_frame)
        text_widget.insert("end", "\n")  # new line after

        # Configure bindings, tags etc.
        text_widget.tag_configure("bold", font=('Arial', self.taille, 'bold'))
        text_widget.bind("<KeyPress>", self.handle_key_press)
        text_widget.bind("<FocusIn>", lambda e: self.set_current_page(text_widget))

        self.pages.append(text_widget)
        text_widget.focus_set()
        self.current_page = text_widget


    def set_current_page(self, page_widget):
        """Set the currently focused page"""
        self.current_page = page_widget

    def handle_key_press(self, event):
        """Handle bold formatting during typing"""
        if self.bold_on and event.char.isprintable():
            event.widget.insert("insert", event.char, "bold")
            return "break"

    def on_canvas_configure(self, event):
        """Center pages and prevent horizontal scroll"""
        self.canvas.itemconfigure("container", width=event.width)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_frame_configure(self, event):
        """Update scroll region when pages change"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def insert_table(self):
        """Insert a table into the current page
        
        Todo:
            - remove it useless
        """
        if not self.current_page:
            return

        # Create dialog to get table dimensions
        dialog = tk.Toplevel(self.root)
        dialog.title("Insert Table")
        dialog.transient(self.root)
        dialog.grab_set()

        rows_var = tk.IntVar(value=2)
        cols_var = tk.IntVar(value=2)

        ttk.Label(dialog, text="Rows:").grid(row=0, column=0, padx=5, pady=5)
        spin_rows = ttk.Spinbox(dialog, from_=1, to=20, textvariable=rows_var)
        spin_rows.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Columns:").grid(row=1, column=0, padx=5, pady=5)
        spin_cols = ttk.Spinbox(dialog, from_=1, to=20, textvariable=cols_var)
        spin_cols.grid(row=1, column=1, padx=5, pady=5)

        def on_ok():
            rows = rows_var.get()
            cols = cols_var.get()
            dialog.destroy()
            self.current_page.focus_set() 
            self.create_table(rows, cols)

        ttk.Button(dialog, text="OK", command=on_ok).grid(row=2, column=0, columnspan=2, pady=5)

    def create_table(self, rows, cols):
        """Create a table with specified dimensions in the current page"""
        text_widget = self.current_page
        table_frame = ttk.Frame(text_widget)
        entries = []
        for i in range(rows):
            row_entries = []
            for j in range(cols):
                entry = ttk.Entry(table_frame, width=10)
                entry.grid(row=i, column=j, sticky="nsew", padx=1, pady=1)
                row_entries.append(entry)
            entries.append(row_entries)
            table_frame.rowconfigure(i, weight=1)
        for j in range(cols):
            table_frame.columnconfigure(j, weight=1)

        # Store entries in the frame for PDF export
        table_frame.table_entries = entries

        # Insert table at current cursor position
        text_widget.window_create("insert", window=table_frame)

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


    def export_pdf(self):
        """Export all pages to PDF including header and tables."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not file_path:
            return

        pdf = pdf_canvas.Canvas(file_path, pagesize=A4)
        a4_width, a4_height = A4
        margin = 20
        line_height = 14
        cell_height = 20
        cell_width = 60

        for page in self.pages:
            y_position = a4_height - margin
            pdf.setFont("Helvetica", 12)
            # Draw the header at the top of the PDF page.
            y_position = self.export_pdf_header(pdf, a4_width, y_position, margin)

            # Rest of the page.
            # This sample code “dumps” the text content and any inserted tables.
            # MEANING NEEDS FIX (Too long of a text goes outsid page)
            content = page.dump("1.0", "end-1c", window=True, text=True)
            elements = []
            current_text = []
            for part in content:
                if part[0] == 'text':
                    current_text.append(part[1])
                elif part[0] == 'window':
                    if current_text:
                        elements.append(('text', ''.join(current_text)))
                        current_text = []
                    widget = page.window_cget(part[2], 'window')
                    if hasattr(widget, 'table_entries'):
                        elements.append(('table', widget.table_entries))
            if current_text:
                elements.append(('text', ''.join(current_text)))

            for elem in elements:
                if elem[0] == 'text':
                    text = elem[1]
                    lines = []
                    for line in text.split('\n'):
                        words = line.split()
                        current_line = []
                        current_width = 0
                        for word in words:
                            word_width = pdf.stringWidth(word, "Helvetica", 12)
                            space_width = pdf.stringWidth(' ', "Helvetica", 12)
                            if current_line and (current_width + word_width + space_width > (a4_width - 2*margin)):
                                lines.append(' '.join(current_line))
                                current_line = [word]
                                current_width = word_width
                            else:
                                if current_line:
                                    current_width += space_width
                                current_line.append(word)
                                current_width += word_width
                        if current_line:
                            lines.append(' '.join(current_line))
                    for line in lines:
                        if y_position < margin:
                            pdf.showPage()
                            y_position = a4_height - margin
                            pdf.setFont("Helvetica", 12)
                        pdf.drawString(margin, y_position, line)
                        y_position -= line_height
                elif elem[0] == 'table':
                    entries = elem[1]
                    rows = len(entries)
                    cols = len(entries[0]) if rows > 0 else 0
                    table_height = rows * cell_height
                    if y_position - table_height < margin:
                        pdf.showPage()
                        y_position = a4_height - margin
                    table_x = margin
                    table_y = y_position - cell_height
                    for i in range(rows):
                        for j in range(cols):
                            entry = entries[i][j]
                            text = entry.get()
                            pdf.rect(table_x + j*cell_width, table_y - i*cell_height, cell_width, cell_height)
                            pdf.drawString(table_x + j*cell_width + 2, table_y - i*cell_height + 2, text)
                    y_position = table_y - rows * cell_height - line_height
            pdf.showPage()
        pdf.save()


if __name__ == "__main__":
    root = tk.Tk()
    app = WordApp(root)
    root.mainloop()