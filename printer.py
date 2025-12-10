"""
Printer interface module for XPrinter XP-365B thermal printer
Uses direct Windows printing with proper image handling
"""
import win32print
import win32ui
from PIL import Image, ImageWin
import config
from utils import log_event


class PrinterManager:
    """Manage thermal printer connections and print jobs"""
    
    def __init__(self):
        self.printer_name = config.PRINTER_CONFIG['printer_name']
    
    def get_available_printers(self) -> list:
        """Get list of available Windows printers"""
        try:
            printers = [printer[2] for printer in win32print.EnumPrinters(2)]
            log_event(f"Found {len(printers)} available printers")
            return printers
        except Exception as e:
            log_event(f"Error getting printer list: {e}", 'error')
            return []
    
    def is_printer_available(self) -> bool:
        """Check if the configured printer is available"""
        available_printers = self.get_available_printers()
        
        # Try exact match first
        if self.printer_name in available_printers:
            return True
        
        # Try case-insensitive partial match
        for printer in available_printers:
            if self.printer_name.lower() in printer.lower():
                self.printer_name = printer  # Update to exact name
                log_event(f"Matched printer: {printer}")
                return True
        
        log_event(f"Printer '{self.printer_name}' not found", 'warning')
        return False
    
    def get_default_printer(self) -> str:
        """Get the default Windows printer"""
        try:
            return win32print.GetDefaultPrinter()
        except Exception as e:
            log_event(f"Error getting default printer: {e}", 'error')
            return None
    
    def print_image(self, image: Image, job_name: str = "Barcode Label") -> bool:
        """Print a single image to the thermal printer"""
        return self.print_images([image], job_name)

    def print_images(self, images: list, job_name: str = "Barcode Batch", 
                    x_offset: int = 0, y_offset: int = 0) -> bool:
        """Print multiple images in a single print job (one image per page)"""
        try:
            if not self.is_printer_available():
                log_event(f"Printer '{self.printer_name}' is not available", 'error')
                return False
            
            log_event(f"Starting print job '{job_name}' with {len(images)} pages...")
            
            # Create device context for printer
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(self.printer_name)
            
            # Get printer dimensions
            printable_width = hdc.GetDeviceCaps(8)   # HORZRES  
            printable_height = hdc.GetDeviceCaps(10) # VERTRES
            
            # Start print job
            hdc.StartDoc(job_name)
            
            for i, image in enumerate(images):
                try:
                    hdc.StartPage()
                    
                    # Convert to RGB if necessary
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # Get image dimensions
                    img_width, img_height = image.size
                    
                    # Calculate scaling to fit printable area
                    scale_x = printable_width / img_width
                    scale_y = printable_height / img_height
                    scale = min(scale_x, scale_y)
                    
                    # If scale is very close to 1 (e.g. > 0.9), just use 1 to avoid artifacts
                    if scale > 0.9:
                        scale = 1.0
                    
                    # Calculate destination size
                    dest_width = int(img_width * scale)
                    dest_height = int(img_height * scale)
                    
                    # Alignment Logic
                    if printable_width > dest_width * 1.5:
                        # Big paper, small label -> Center
                        x = (printable_width - dest_width) // 2
                    else:
                        # Label printer -> Align left (usually better for barcode scanners/labels)
                        x = 0
                        
                    if printable_height > dest_height * 1.5:
                         y = (printable_height - dest_height) // 2
                    else:
                         y = 0
                    
                    # Apply manual offsets (convert mm to pixels approx, but passed as pixels)
                    # Offsets are passed in pixels by the caller (main.py will convert mm->px)
                    x += x_offset
                    y += y_offset
                    
                    log_event(f"Page {i+1}: {img_width}x{img_height} -> {dest_width}x{dest_height} at ({x},{y})")
                    
                    # Create DIB and draw to printer
                    dib = ImageWin.Dib(image)
                    dib.draw(hdc.GetHandleOutput(), (x, y, x + dest_width, y + dest_height))
                    
                    hdc.EndPage()
                    
                except Exception as e:
                    log_event(f"Error printing page {i+1}: {e}", 'error')
                    # Continue to next page? Or abort? Let's continue.
            
            # End print job
            hdc.EndDoc()
            hdc.DeleteDC()
            
            log_event(f"Print job '{job_name}' completed successfully")
            return True
            
        except Exception as e:
            log_event(f"Print job error: {e}", 'error')
            import traceback
            log_event(traceback.format_exc(), 'error')
            return False
    
    def print_test_page(self) -> bool:
        """Print a test page"""
        try:
            from PIL import ImageDraw, ImageFont
            
            # Create a simple test image
            test_img = Image.new('RGB', (400, 200), 'white')
            draw = ImageDraw.Draw(test_img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            draw.text((50, 80), "XPrinter XP-365B", fill='black', font=font)
            draw.text((80, 120), "Test Print", fill='black', font=font)
            
            return self.print_image(test_img, "Test Page")
        
        except Exception as e:
            log_event(f"Error printing test page: {e}", 'error')
            return False
    def send_raw_data(self, data: bytes, job_name: str = "Raw Print Job") -> bool:
        """Send raw bytes directly to the printer"""
        try:
            if not self.is_printer_available():
                log_event(f"Printer '{self.printer_name}' not available for raw printing", 'error')
                return False
            
            hPrinter = win32print.OpenPrinter(self.printer_name)
            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, (job_name, None, "RAW"))
                try:
                    win32print.StartPagePrinter(hPrinter)
                    win32print.WritePrinter(hPrinter, data)
                    win32print.EndPagePrinter(hPrinter)
                finally:
                    win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
                
            log_event(f"Sent {len(data)} bytes of raw data to printer")
            return True
        except Exception as e:
            log_event(f"Error sending raw data: {e}", 'error')
            return False

    def print_tspl_data(self, students: list) -> bool:
        """
        Generate and print TSPL commands for a list of students.
        Each student dict must have: StudentID, SeatNo, VenueName
        """
        try:
            # TSPL Configuration for 60mm x 40mm
            # 8 dots/mm -> 480 dots width, 320 dots height
            cmds = [
                "SIZE 60 mm, 40 mm",
                "GAP 2 mm, 0 mm",
                "DIRECTION 1",
                "CLS"
            ]
            
            for student in students:
                sid = student.get('StudentID', 'UNKNOWN')
                barcode_val = student.get('Barcode', sid) # Use Barcode field if avail, else SID
                seat = student.get('SeatNo', '')
                hall = student.get('VenueName', '')
                
                # Clean up hall name if necessary
                hall = str(hall).replace('"', '\"')
                
                # Barcode: Code 128, Height 100, centered
                # Human Readable = 2 (Below, Centered) or 1 (Below, Left). 
                # Let's use 1 (standard) or 2 if supported. Safe bet is 1 or manually provided.
                # User asked to "show the Barcode". 
                # Enabling native text: BARCODE X, Y, "128", Height, HumanReadable=1, ...
                cmd = f'BARCODE 30,30,"128",100,1,0,2,2,"{barcode_val}"'
                cmds.append(cmd)
                
                # Hall Name (Bottom)
                # Removed Seat Number as requested
                # Font "3" (Standard alphanumeric)
                cmd = f'TEXT 30,150,"3",0,1,1,"{hall}"'
                cmds.append(cmd)
                
                # Print 1 Label
                cmds.append("PRINT 1")
                cmds.append("CLS") # Clear buffer for next label
            
            # Join with newlines and encode
            tspl_command = "\n".join(cmds).encode('utf-8')
            
            return self.send_raw_data(tspl_command, f"TSPL Batch ({len(students)})")
            
        except Exception as e:
            log_event(f"Error generating TSPL data: {e}", 'error')
            return False
