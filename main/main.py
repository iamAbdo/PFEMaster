import tkinter as tk
from gui.splash import SplashWindow
from gui.project_info import ProjectInfoWindow
from core.app import Sincus

def start_main_app(project_info):
    # Destroy any existing widgets
    for widget in root.winfo_children():
        widget.destroy()
    
    # Start main application
    app = Sincus(root, project_info)

if __name__ == "__main__":
    root = tk.Tk()

    # show splash first
    def on_splash_create(jwt_token=None):
        # now open your existing project‑info dialog
        ProjectInfoWindow(root, start_main_app, jwt_token=jwt_token)

    SplashWindow(root, on_splash_create)
    root.mainloop()