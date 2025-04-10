import tkinter as tk
from tkinter import ttk
from utils.text_formatting import handle_key_press, set_current_page

def add_new_page(app):
    a4_width = int(21/2.54*96)  # 794 pixels
    a4_height = int(29.7/2.54*96)  # 1123 pixels

    page_frame = ttk.Frame(app.container)
    page_frame.pack(pady=20, expand=True)

    page_canvas = tk.Canvas(page_frame, width=a4_width, height=a4_height,
                            bg="white", highlightthickness=0)
    page_canvas.pack()

    # Draw page border
    page_canvas.create_rectangle(2, 2, a4_width+2, a4_height+2, fill='#e0e0e0', outline='')
    page_canvas.create_rectangle(0, 0, a4_width, a4_height, fill="white")

    # Container frame for columns and labels
    container = ttk.Frame(page_canvas)
    container.place(x=0, y=0, width=a4_width, height=a4_height)

    # Configure grid columns for container
    app.column_pixel_widths = [50]*7 + [148]*3  # Pixel widths for each column
    text_char_widths = [6]*7 + [18]*3       # Character widths for Text widgets

    for i in range(10):
        container.grid_columnconfigure(i, minsize=app.column_pixel_widths[i], weight=1)

    # Configure grid rows: row 0 for labels, row 1 for text
    container.grid_rowconfigure(0, minsize=20)  # Label row height
    container.grid_rowconfigure(1, weight=1)    # Text row expands

    # Create labels A-J
    for i in range(10):
        label = ttk.Label(container, text=chr(65 + i), background='white')
        label.grid(row=0, column=i, sticky="nsew")

    # Create Text widgets for each column
    text_widgets = []
    for i in range(10):
        text = tk.Text(container, wrap="word", bg="white", bd=0,
                       font=('Arial', app.root.taille),
                       width=text_char_widths[i], height=1)
        text.grid(row=1, column=i, sticky="nsew")
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