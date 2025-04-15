import tkinter as tk
from gui.project_info import ProjectInfoWindow
from core.app import WordApp

def start_main_app(project_info):
    # Destroy any existing widgets
    for widget in root.winfo_children():
        widget.destroy()
    
    # Start main application
    app = WordApp(root, project_info)

if __name__ == "__main__":
    root = tk.Tk()
    ProjectInfoWindow(root, start_main_app)
    root.mainloop()