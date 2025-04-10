def toggle_bold(app):
    app.bold_on = not app.bold_on
    app.bold_btn.state(['pressed' if app.bold_on else '!pressed'])

def handle_key_press(app, event):

    if event.keysym == 'b' and (event.state & 0x4):  # Ctrl+B
        current_tags = app.current_text_widget.tag_names("insert")
        if "bold" in current_tags:
            app.current_text_widget.tag_remove("bold", "sel.first", "sel.last")
        else:
            app.current_text_widget.tag_add("bold", "sel.first", "sel.last")
        return "break"
    if app.bold_on and event.char.isprintable():
        event.widget.insert("insert", event.char, "bold")
        return "break"

def set_current_page(app, text_widget):
    app.current_text_widget = text_widget
    for page in app.pages:
        if text_widget in page:
            app.current_page = page
            break