import tkinter as tk

from tkinter import ttk, font as tkfont, filedialog
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas

class WordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Application")
        self.root.state('zoomed')  # Maximize window
        
        # Configure grid layout
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create header frame with improved styling
        self.header_frame = ttk.Frame(self.root, height=80, style='Header.TFrame')
        self.header_frame.grid(row=0, column=0, sticky="nsew")
        
        # Create main content frame
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        
        self.pages = []
        self.bold_on = False
        self.current_font = ("Arial", 12)
        self.root.taille = 12
        self.current_page = None  # Track the currently focused page
        
        # Configure styles
        self.setup_styles()
        
        # Add control buttons
        self.add_controls()
        
        # Setup canvas and pages
        self.setup_canvas()
        self.add_new_page()
        
        
    def setup_styles(self):
        style = ttk.Style()
        style.configure('Header.TFrame', background='#f0f0f0')
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'), padding=6)
        style.map('Primary.TButton',
                background=[('active', 'red'), ('!active', 'red')],
                foreground=[('active', 'black'), ('!active', 'black')])
        
    def add_controls(self):
        """Add control buttons to header with improved styling"""
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
        
        # Bind events
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.container.bind("<Configure>", self.on_frame_configure)

    def toggle_bold(self):
        """Toggle bold formatting state"""
        self.bold_on = not self.bold_on
        self.bold_btn.state(['pressed' if self.bold_on else '!pressed'])

    def add_new_page(self):
        """Create a new centered A4 page with proper dimensions"""
        # A4 dimensions in pixels (21cm x 29.7cm at 96dpi)
        a4_width, a4_height = int(21/2.54*96), int(29.7/2.54*96)
        
        # Page frame with improved shadow
        page_frame = ttk.Frame(self.container)
        page_frame.pack(pady=20, expand=True)
        
        # Create page canvas with exact A4 dimensions
        page_canvas = tk.Canvas(page_frame, width=a4_width, height=a4_height,
                              bg="white", highlightthickness=0)
        page_canvas.pack()
        
        # Add subtle shadow effect
        page_canvas.create_rectangle(2, 2, a4_width+2, a4_height+2, fill='#e0e0e0', outline='')
        page_canvas.create_rectangle(0, 0, a4_width, a4_height, fill="white")

        # Add text widget with proper margins
        text_widget = tk.Text(page_canvas, wrap="word", bg="white", bd=0,
                            font=('Arial', self.root.taille), padx=40, pady=50)
        text_widget.place(x=0, y=0, width=a4_width, height=a4_height)
        
        # Configure tags and bindings
        text_widget.tag_configure("bold", font=('Arial', 12, 'bold'))
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
        """Insert a table into the current page"""
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
            self.current_page.focus_set()  # Refocus the text widget
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

    def export_pdf(self):
        """Export all pages to PDF including tables"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not file_path:
            return

        pdf = pdf_canvas.Canvas(file_path, pagesize=A4)
        a4_width, a4_height = A4
        margin = 40
        line_height = 14
        cell_height = 20
        cell_width = 60

        for page in self.pages:
            # Collect elements (text and tables) in order
            content = page.dump("1.0", "end-1c", window=True, text=True)
            elements = []
            current_text = []
            for part in content:
                if part[0] == 'text':
                    current_text.append(part[1])
                elif part[0] == 'window':
                    # Flush current text
                    if current_text:
                        elements.append(('text', ''.join(current_text)))
                        current_text = []
                    # Check if the window is a table
                    widget = page.window_cget(part[2], 'window')
                    if hasattr(widget, 'table_entries'):
                        elements.append(('table', widget.table_entries))
            # Add any remaining text
            if current_text:
                elements.append(('text', ''.join(current_text)))

            y_position = a4_height - margin
            pdf.setFont("Helvetica", 12)

            for elem in elements:
                if elem[0] == 'text':
                    text = elem[1]
                    # Split into lines and wrap
                    lines = []
                    for line in text.split('\n'):
                        words = line.split()
                        current_line = []
                        current_width = 0
                        for word in words:
                            word_width = pdf.stringWidth(word, "Helvetica", 12)
                            if current_line and (current_width + word_width + pdf.stringWidth(' ', "Helvetica", 12) > (a4_width - 2*margin)):
                                lines.append(' '.join(current_line))
                                current_line = [word]
                                current_width = word_width
                            else:
                                if current_line:
                                    current_width += pdf.stringWidth(' ', "Helvetica", 12)
                                current_line.append(word)
                                current_width += word_width
                        if current_line:
                            lines.append(' '.join(current_line))
                    # Add each line to the PDF
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

                    # Calculate required height for the table
                    table_height = rows * cell_height
                    # Check if there's enough space
                    if y_position - table_height < margin:
                        pdf.showPage()
                        y_position = a4_height - margin

                    # Draw table
                    table_x = margin
                    table_y = y_position - cell_height  # Start from top
                    for i in range(rows):
                        for j in range(cols):
                            entry = entries[i][j]
                            text = entry.get()
                            # Draw cell border
                            pdf.rect(table_x + j*cell_width, table_y - i*cell_height, cell_width, cell_height)
                            # Draw cell text
                            pdf.drawString(table_x + j*cell_width + 2, table_y - i*cell_height + 2, text)
                    # Update y_position
                    y_position = table_y - (rows * cell_height) - line_height

            pdf.showPage()

        pdf.save()

if __name__ == "__main__":
    root = tk.Tk()
    app = WordApp(root)
    root.mainloop()