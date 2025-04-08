def on_canvas_configure(app, event):
    app.canvas.itemconfigure("container", width=event.width)
    app.canvas.configure(scrollregion=app.canvas.bbox("all"))

def on_frame_configure(app, event):
    app.canvas.configure(scrollregion=app.canvas.bbox("all"))
