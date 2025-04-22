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
        
        if i == 0: 
            # Ruler container with border
            ruler_frame = tk.Frame(col_frame, bd=1, relief="solid", bg="white")
            ruler_frame.pack(fill='both', expand=True, padx=0, pady=0)
            
            # Create canvas for ruler drawing
            ruler_canvas = tk.Canvas(ruler_frame, bg="white", highlightthickness=0)
            ruler_canvas.pack(fill='both', expand=True, padx=0, pady=0)
            
            def draw_ruler(event):
                ruler_canvas.delete("all")
                canvas_width = event.width
                canvas_height = event.height
                
                # Calculate division height
                division_height = canvas_height / 9
                
                # Draw ruler elements
                for j in range(9):
                    y_pos = j * division_height
                    
                    # Main bold line (right side)
                    ruler_canvas.create_line(canvas_width-15, y_pos, canvas_width, y_pos, width=2)
                    
                    # Subdivision lines (4 between main numbers)
                    for k in range(1, 5):
                        sub_y = y_pos + (k * division_height/5)
                        ruler_canvas.create_line(canvas_width-8, sub_y, canvas_width, sub_y)
                    
                    # Number labels (left-aligned to ruler lines)
                    ruler_canvas.create_text(
                        canvas_width-20,  # Position text to left of lines
                        y_pos,
                        text=str(3000 + j),
                        anchor="ne",  # Northeast anchor
                        font=('Arial', max(6, app.root.taille - 4)),  # Smaller font size
                        fill="black"
                    )
                
                ruler_canvas.create_text(
                    canvas_width-20, 
                    9*division_height - 12,
                    text=str(3000 + 9),
                    anchor="ne",  
                    font=('Arial', max(6, app.root.taille - 4)), 
                    fill="black"
                )
                # Final bold line at bottom
                ruler_canvas.create_line(canvas_width-15, canvas_height, canvas_width, canvas_height, width=2)
            
            ruler_canvas.bind("<Configure>", draw_ruler)

        elif i == 1:
            # Create a frame for the lines with a border
            lines_frame = tk.Frame(col_frame, bd=1, relief="solid", bg="white")
            lines_frame.pack(fill='both', expand=True, padx=0, pady=0)
            
            # Create canvas to draw the lines and handle clicks
            lines_canvas = tk.Canvas(lines_frame, bg="white", highlightthickness=0)
            lines_canvas.pack(fill='both', expand=True)
            
            # Initialize box states storage
            if not hasattr(lines_canvas, 'box_states'):
                lines_canvas.box_states = [{
                    'color': 'white', 
                    'texture': None
                } for _ in range(45)]

            def show_selection_dialog(box_index):
                popup = tk.Toplevel(app.root)
                popup.title("Box Formatting")
                popup.geometry("300x200")
                
                # Color selection
                color_var = tk.StringVar(value=lines_canvas.box_states[box_index]['color'])
                ttk.Label(popup, text="Choose Color:").pack(pady=5)
                
                color_frame = ttk.Frame(popup)
                color_frame.pack()
                colors = [('Red', 'red'), ('Green', 'green'), ('Blue', 'blue'), 
                        ('Yellow', 'yellow'), ('White', 'white')]
                for text, color in colors:
                    btn = ttk.Radiobutton(
                        color_frame, text=text, value=color, variable=color_var,
                        command=lambda c=color: color_var.set(c)
                    )
                    btn.pack(side='left', padx=2)

                # Texture selection
                texture_var = tk.StringVar(value=lines_canvas.box_states[box_index]['texture'] or 'none')
                ttk.Label(popup, text="Choose Texture:").pack(pady=5)
                
                texture_frame = ttk.Frame(popup)
                texture_frame.pack()
                textures = [
                    ('None', 'none'), 
                    ('Dashes', 'dashes'), 
                    ('Pluses', 'pluses'), 
                    ('Slashes', 'slashes')
                ]
                for text, texture in textures:
                    btn = ttk.Radiobutton(
                        texture_frame, text=text, value=texture, variable=texture_var,
                        command=lambda t=texture: texture_var.set(t)
                    )
                    btn.pack(side='left', padx=2)

                def apply_changes():
                    # Update box state
                    lines_canvas.box_states[box_index]['color'] = color_var.get()
                    lines_canvas.box_states[box_index]['texture'] = (
                        texture_var.get() if texture_var.get() != 'none' else None
                    )
                    # Redraw canvas
                    width = lines_canvas.winfo_width()
                    height = lines_canvas.winfo_height()
                    fake_event = type('Event', (), {'width': width, 'height': height})()
                    draw_lines(fake_event)
                    popup.destroy()

                ttk.Button(popup, text="Apply", command=apply_changes).pack(pady=10)

            def draw_lines(event):
                lines_canvas.delete("all")
                canvas_width = event.width
                canvas_height = event.height
                division_height = canvas_height / 45

                for j in range(45):
                    y_top = j * division_height
                    y_bottom = (j + 1) * division_height
                    state = lines_canvas.box_states[j]

                    # Draw background
                    box_id = lines_canvas.create_rectangle(
                        0, y_top, canvas_width, y_bottom,
                        fill=state['color'], outline='',
                        tags=(f"box_{j}",)
                    )
                    lines_canvas.tag_bind(box_id, '<Button-1>', 
                        lambda e, idx=j: show_selection_dialog(idx))

                    # Draw texture
                    if state['texture'] == 'dashes':
                        step = division_height / 5
                        for y in range(int(y_top), int(y_bottom), int(step)):
                            lines_canvas.create_line(0, y, canvas_width, y, dash=(2, 2))
                    elif state['texture'] == 'pluses':
                        x_step = canvas_width // 4
                        y_step = division_height // 4
                        for x in range(10, int(canvas_width), x_step):
                            for y in range(int(y_top)+5, int(y_bottom), y_step):
                                lines_canvas.create_line(x-3, y, x+3, y, width=1)
                                lines_canvas.create_line(x, y-3, x, y+3, width=1)
                    elif state['texture'] == 'slashes':
                        for offset in range(-10, 10, 3):
                            lines_canvas.create_line(
                                offset, y_top, 
                                canvas_width+offset, y_bottom,
                                fill='black'
                            )

                    # Draw separation line
                    lines_canvas.create_line(0, y_bottom, canvas_width, y_bottom)

            lines_canvas.bind("<Configure>", draw_lines)
        
        else:
            # Text widget with border
            text = tk.Text(
                col_frame,
                wrap="word",
                bg="white",
                bd=1,
                relief="solid",
                font=('Arial', app.root.taille),
                width=text_char_widths[i],
                height=1
            )
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


