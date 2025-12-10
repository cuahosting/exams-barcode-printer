import json
import os
import config

SETTINGS_FILE = 'settings.json'

def load_settings():
    """Load settings from JSON file or return defaults"""
    defaults = {
        'label_width_mm': config.PRINTER_CONFIG['card_width_mm'],
        'label_height_mm': config.PRINTER_CONFIG['card_height_mm'],
        'offset_x_mm': 0.0,
        'offset_y_mm': 0.0,
        'printer_name': config.PRINTER_CONFIG['printer_name']
    }
    
    if not os.path.exists(SETTINGS_FILE):
        return defaults
        
    try:
        with open(SETTINGS_FILE, 'r') as f:
            saved = json.load(f)
            # Merge with defaults to ensure all keys exist
            return {**defaults, **saved}
    except Exception as e:
        print(f"Error loading settings: {e}")
        return defaults

def save_settings(settings):
    """Save settings to JSON file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

DB_SETTINGS_FILE = 'db_settings.json'

def load_db_settings():
    """Load database settings from JSON or return defaults from config"""
    defaults = config.DB_CONFIG.copy()
    
    if not os.path.exists(DB_SETTINGS_FILE):
        return defaults
        
    try:
        with open(DB_SETTINGS_FILE, 'r') as f:
            saved = json.load(f)
            return {**defaults, **saved}
    except Exception as e:
        print(f"Error loading DB settings: {e}")
        return defaults

def save_db_settings(settings):
    """Save database settings to JSON"""
    try:
        with open(DB_SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving DB settings: {e}")
        return False
