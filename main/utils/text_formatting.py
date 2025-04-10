import tkinter as tk

def toggle_bold(app):
    text_widget = app.current_text_widget
    try:
        start = text_widget.index("sel.first")
        end = text_widget.index("sel.last")
    except tk.TclError:
        return  # No selection
    
    current_tags = text_widget.tag_names("sel.first")
    if "bold" in current_tags:
        text_widget.tag_remove("bold", start, end)
        app.bold_btn.state(['!pressed'])
    else:
        text_widget.tag_add("bold", start, end)
        app.bold_btn.state(['pressed'])

def handle_key_press(app, event):

    if event.keysym == 'b' and (event.state & 0x4):
        toggle_bold(app)
        return "break"

def set_current_page(app, text_widget):
    app.current_text_widget = text_widget
    for page in app.pages:
        if text_widget in page:
            app.current_page = page
            break