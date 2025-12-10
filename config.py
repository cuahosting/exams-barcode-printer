"""
Configuration file for Barcode Printer Application
Update the values below with your actual database and printer settings
"""

# MySQL Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'cosmopolitanedu2',
    'user': 'root',
    'password': 'Password',
    'port': 3306,
    'raise_on_warnings': True,
    'autocommit': False
}

# Authorized Users
AUTHORIZED_USERS = [
    'zainab.attahiru@cosmopolitan.edu.ng',
    'hayat.suleiman@cosmopolitan.edu.ng'
]

# Printer Configuration - XPrinter XP-365B Thermal Label Printer
PRINTER_CONFIG = {
    'printer_name': 'Xprinter XP-365B',  # Exact Windows printer name
    'card_width_mm': 60.0,   # Label width (updated to 60mm)
    'card_height_mm': 40.0,  # Label height (updated to 40mm)
    'dpi': 203,              # Thermal printer standard DPI (203 or 300)
}

# Note: XPrinter XP-365B specs:
# - Direct thermal printing (no ink/ribbon needed)
# - Media width: 20mm to 82mm
# - Supports gap/black mark sensors
# - Roll diameter: up to 82mm
# - Ideal for labels, barcodes, receipts

# Application Settings
APP_SETTINGS = {
    'title': 'Cosmopolitan EDU - Barcode Printer',
    'window_width': 800,
    'window_height': 600,
    'log_file': 'barcode_printer.log'
}
