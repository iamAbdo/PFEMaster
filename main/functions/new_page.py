import tkinter as tk
from tkinter import ttk
from utils.text_formatting import handle_key_press, set_current_page

# Not used here yet Wrote it directly in the export_pdf.py file
def get_column_values(page):
    """Get first line of text from each column in the page and returns it"""
    return [text_widget.get("1.0", "1.end") for text_widget in page]

def add_new_page(app):

    # Last line Column configuration at the top
    app.column_labels = [
        "Côtes (m)", 
        "Log", 
        "Echan", 
        "direct", 
        "Indir", 
        "Fissures", 
        "Pendage", 
        "Calcimètrie", 
        "Age", 
        "DESCRIPTION LITHOLOGIQUE & OBSERVATIONS"
    ]

    # a4_width = int(21/2.54*96)  # 794 pixels
    # a4_height = int(29.7/2.54*96)  # 1123 pixels

    from reportlab.lib.pagesizes import A4
    a4_width, a4_height = A4
    
    a4_width = int(a4_width)
    a4_height = int(a4_height)

    page_frame = ttk.Frame(app.container)
    page_frame.pack(pady=20, expand=True)

    page_canvas = tk.Canvas(page_frame, width=a4_width, height=a4_height,
                            bg="white", highlightthickness=0)
    page_canvas.pack()


    # Container frame for columns and labels
    container = ttk.Frame(page_canvas)
    container.place(x=0, y=0, width=a4_width, height=a4_height)

    # Configure grid columns for container
    app.column_pixel_widths = [50]*7 + [148]*3  
    text_char_widths = [6]*7 + [18]*3      

    x = (a4_width-2) / 24
    col_widths = [2*x] + [x]*6 + [2*x]*2 + [x*4 + 3*x + 5*x]
    text_char_widths = [int(width / 8) for width in col_widths]
    app.column_pixel_widths = col_widths  

    for i in range(10):
        container.grid_columnconfigure(i, minsize=app.column_pixel_widths[i], weight=1)

    # Configure grid rows: row 0 for labels, row 1 for text
    container.grid_rowconfigure(0, minsize=20)  # Label row height
    container.grid_rowconfigure(1, weight=1)    # Text row expands

    
    text_widgets = []
    for i in range(10):
        # Column container frame
        col_frame = ttk.Frame(container, style='Column.TFrame')
        col_frame.grid(row=0, column=i, rowspan=2, sticky="nsew")
        

        # Label
        label = ttk.Label(col_frame, text=app.column_labels[i], style='ColumnHeader.TLabel')
        label.pack(fill='x')
        
        # Text widget with border
        text = tk.Text(col_frame, wrap="word", bg="white", bd=1, relief="solid",
                      font=('Arial', app.root.taille),
                      width=text_char_widths[i], height=1)
        text.pack(fill='both', expand=True)
        text.bind("<KeyPress>", lambda e: handle_key_press(app, e))
        text.bind("<FocusIn>", lambda e, t=text: set_current_page(app, t))
        
        text_widgets.append(text)


    # Add footer with page number
    page_number = len(app.pages) + 1
    footer = ttk.Label(page_frame, text=f"Page {page_number}")
    footer.pack(side='bottom')

    # Add all text widgets to app.pages and set focus
    app.pages.append(text_widgets)
    text_widgets[0].focus_set()
    app.current_page = text_widgets
    app.current_text_widget = text_widgets[0]

    # Update status bar
    app.status_bar.config(text=f"Total pages: {len(app.pages)}")