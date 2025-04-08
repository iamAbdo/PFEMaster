def toggle_bold(app):
    app.bold_on = not app.bold_on
    app.bold_btn.state(['pressed' if app.bold_on else '!pressed'])

def handle_key_press(app, event):
    if app.bold_on and event.char.isprintable():
        event.widget.insert("insert", event.char, "bold")
        return "break"

def set_current_page(app, page_widget):
    app.current_page = page_widget
