import tkinter as tk
from gui.splash import SplashWindow
from gui.project_info import ProjectInfoWindow
from core.app import Sincus
from utils.auth_state import set_jwt_token_global, get_jwt_token_global

def start_main_app(project_info, jwt_token=None):
    # Update global token if provided
    if jwt_token:
        set_jwt_token_global(jwt_token)
    
    # Destroy any existing widgets
    for widget in root.winfo_children():
        widget.destroy()
    
    # Start main application with global JWT token
    app = Sincus(root, project_info, get_jwt_token_global())

if __name__ == "__main__":
    root = tk.Tk()

    # show splash first
    def on_splash_create(jwt_token=None):
        # Update global token if provided
        if jwt_token:
            set_jwt_token_global(jwt_token)
        # now open your existing project‑info dialog
        ProjectInfoWindow(root, start_main_app, jwt_token=jwt_token)

    SplashWindow(root, on_splash_create)
    root.mainloop()