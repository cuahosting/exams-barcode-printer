"""
Barcode generation module for the Barcode Printer Application
"""
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import io
import config
from utils import log_event, mm_to_pixels


class BarcodeGenerator:
    """Generate barcode images formatted for card printing"""
    
    def __init__(self, settings=None):
        if settings:
            self.card_width_px = mm_to_pixels(
                settings.get('label_width_mm', 40.0),
                config.PRINTER_CONFIG['dpi']
            )
            self.card_height_px = mm_to_pixels(
                settings.get('label_height_mm', 60.0),
                config.PRINTER_CONFIG['dpi']
            )
            self.dpi = config.PRINTER_CONFIG['dpi']
        else:
            self.card_width_px = mm_to_pixels(
                config.PRINTER_CONFIG['card_width_mm'],
                config.PRINTER_CONFIG['dpi']
            )
            self.card_height_px = mm_to_pixels(
                config.PRINTER_CONFIG['card_height_mm'],
                config.PRINTER_CONFIG['dpi']
            )
            self.dpi = config.PRINTER_CONFIG['dpi']
    
    def generate_barcode_image(self, barcode_value: str) -> Image:
        """Generate a Code128 barcode image optimized for thermal label printing"""
        try:
            # Create Code128 barcode
            code128 = barcode.get_barcode_class('code128')
            
            # Configure writer for thermal printing
            writer = ImageWriter()
            writer.dpi = 203  # Standard thermal printer DPI
            
            # Generate barcode
            barcode_instance = code128(str(barcode_value), writer=writer)
            
            # Render to bytes - smaller barcode to fit 60x40mm label
            buffer = io.BytesIO()
            barcode_instance.write(buffer, options={
                'module_width': 0.25,     # Thinner bars to fit label
                'module_height': 8.0,     # Shorter height to fit label
                'quiet_zone': 1.0,        # Minimal margins
                'font_size': 0,           # No text (we'll add it ourselves)
                'text_distance': 0,
                'write_text': False,
                'foreground': 'black',
                'background': 'white',
            })
            
            # Load as PIL Image
            buffer.seek(0)
            barcode_img = Image.open(buffer).convert('RGB')
            
            log_event(f"Generated barcode for value: {barcode_value}")
            return barcode_img, barcode_value
        
        except Exception as e:
            log_event(f"Error generating barcode: {e}", 'error')
            raise
    
    def create_barcode_card(self, barcode_value: str, module_code: str = None, 
                           module_name: str = None, semester: str = None,
                           width_mm: float = None, height_mm: float = None) -> Image:
        """Create a barcode label that fits within 60mm x 40mm thermal label"""
        try:
            # Generate barcode image (without text)
            barcode_img, value_text = self.generate_barcode_image(barcode_value)
            
            # Use overrides if provided, otherwise use class defaults
            if width_mm is not None and height_mm is not None:
                label_width_px = mm_to_pixels(width_mm, self.dpi)
                label_height_px = mm_to_pixels(height_mm, self.dpi)
            else:
                label_width_px = self.card_width_px
                label_height_px = self.card_height_px
            
            # Calculate exact label dimensions in pixels at 203 DPI
            # 60mm x 40mm at 203 DPI
            # Calculate exact label dimensions in pixels from config
            label_width_px = self.card_width_px
            label_height_px = self.card_height_px
            
            # Create white label background
            label = Image.new('RGB', (label_width_px, label_height_px), 'white')
            draw = ImageDraw.Draw(label)
            
            # Load font for text - smaller font
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            # Calculate text dimensions
            text_bbox = draw.textbbox((0, 0), value_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Margins
            margin_x = 20
            margin_top = 15
            margin_bottom = 10
            text_spacing = 8  # Space between barcode and text
            
            # Available area for barcode
            available_width = label_width_px - (margin_x * 2)
            available_height = label_height_px - margin_top - margin_bottom - text_height - text_spacing
            
            # Rotate barcode if label is portrait (taller than wide) to maximize size
            # Standard barcodes are wide. If we have a narrow label (40mm), we should rotate.
            if label_width_px < label_height_px:
                barcode_img = barcode_img.rotate(90, expand=True)

            # Scale barcode to fit available space (don't exceed)
            barcode_width, barcode_height = barcode_img.size
            scale_x = available_width / barcode_width
            scale_y = available_height / barcode_height
            scale = min(scale_x, scale_y, 1.0)  # Never upscale
            
            new_width = int(barcode_width * scale)
            new_height = int(barcode_height * scale)
            
            # Resize barcode
            barcode_img = barcode_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Center barcode horizontally and vertically on the label
            barcode_x = (label_width_px - new_width) // 2
            
            # For portrait, we might want to center vertically or bias towards top
            # Let's simple center it for now as it's safe
            barcode_y = (label_height_px - new_height) // 2
            
            # Paste barcode
            label.paste(barcode_img, (barcode_x, barcode_y))
            
            # Draw text centered below barcode
            text_x = (label_width_px - text_width) // 2
            text_y = barcode_y + new_height + text_spacing
            draw.text((text_x, text_y), value_text, fill='black', font=font)
            
            log_event(f"Created label: barcode {new_width}x{new_height}px on {label_width_px}x{label_height_px}px label")
            return label
        
        except Exception as e:
            log_event(f"Error creating barcode label: {e}", 'error')
            raise


def mm_to_pixels(mm: float, dpi: int = 203) -> int:
    """Convert millimeters to pixels at given DPI"""
    inches = mm / 25.4
    return int(inches * dpi)
    
    def save_card(self, card: Image, filename: str) -> str:
        """Save card to file"""
        try:
            card.save(filename, 'PNG', dpi=(self.dpi, self.dpi))
            log_event(f"Saved barcode card to {filename}")
            return filename
        except Exception as e:
            log_event(f"Error saving card: {e}", 'error')
            raise
