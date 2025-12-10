"""
Utility functions for the Barcode Printer Application
"""
import logging
from datetime import datetime
from typing import Optional
import config


def setup_logging():
    """Configure application logging"""
    logging.basicConfig(
        filename=config.APP_SETTINGS['log_file'],
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Also log to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def log_event(message: str, level: str = 'info'):
    """Log an event with specified level"""
    logger = logging.getLogger(__name__)
    if level.lower() == 'error':
        logger.error(message)
    elif level.lower() == 'warning':
        logger.warning(message)
    else:
        logger.info(message)


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email or '@' not in email:
        return False
    return email.lower() in [user.lower() for user in config.AUTHORIZED_USERS]


def format_datetime(dt: datetime = None) -> str:
    """Format datetime for display"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def mm_to_pixels(mm: float, dpi: int = 300) -> int:
    """Convert millimeters to pixels at given DPI"""
    inches = mm / 25.4
    return int(inches * dpi)


class SessionManager:
    """Manage user session data"""
    
    def __init__(self):
        self.current_user: Optional[str] = None
        self.selected_semester: Optional[dict] = None
        self.selected_module: Optional[dict] = None
        self.barcode_data: Optional[dict] = None
    
    def login(self, email: str):
        """Log in a user"""
        if validate_email(email):
            self.current_user = email
            log_event(f"User logged in: {email}")
            return True
        return False
    
    def logout(self):
        """Log out current user and clear session"""
        log_event(f"User logged out: {self.current_user}")
        self.current_user = None
        self.selected_semester = None
        self.selected_module = None
        self.barcode_data = None
    
    def set_semester(self, semester_data: dict):
        """Set selected semester"""
        self.selected_semester = semester_data
        self.selected_module = None
        self.barcode_data = None
    
    def set_module(self, module_data: dict):
        """Set selected module"""
        self.selected_module = module_data
        self.barcode_data = None
    
    def set_barcode(self, barcode_data: dict):
        """Set barcode data"""
        self.barcode_data = barcode_data
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        return self.current_user is not None
