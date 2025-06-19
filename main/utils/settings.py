import os
import sys
from pathlib import Path

def get_settings_dir():
    """Return the platform-appropriate settings directory for the app 'sincus'."""
    if sys.platform.startswith('win'):
        appdata = os.getenv('APPDATA')
        if appdata:
            settings_dir = Path(appdata) / 'sincus'
        else:
            # fallback to home directory
            settings_dir = Path.home() / 'AppData' / 'Roaming' / 'sincus'
    else:
        # Linux and others: use ~/.config/sincus
        settings_dir = Path.home() / '.config' / 'sincus'
    settings_dir.mkdir(parents=True, exist_ok=True)
    return settings_dir

def get_settings_file(filename='settings.json'):
    """Return the full path to a settings file inside the settings directory."""
    return get_settings_dir() / filename 