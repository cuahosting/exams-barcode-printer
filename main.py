"""
Main GUI Application for Barcode Printer
Cosmopolitan EDU - Barcode Card Printing System
"""
import tkinter as tk
from tkinter import messagebox, simpledialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.scrolled import ScrolledText
import time
from PIL import Image, ImageTk
import threading
from typing import Optional

import config
from utils import setup_logging, log_event, SessionManager
from database import DatabaseManager
from barcode_generator import BarcodeGenerator
from printer import PrinterManager


class BarcodeprinterApp:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(config.APP_SETTINGS['title'])
        # Set to full screen
        self.root.state('zoomed')
        
        # Initialize components
        setup_logging()
        self.session = SessionManager()
        self.db = DatabaseManager()
        self.barcode_gen = BarcodeGenerator()
        self.printer = PrinterManager()
        
        # UI Variables
        self.current_barcode_image: Optional[Image.Image] = None
        self.current_student_index: int = 0
        self.all_barcode_images: list = []
        self.preview_photo = None
        
        # Main container for all views
        self.container = ttk.Frame(self.root)
        self.container.pack(fill=BOTH, expand=True)
        
        # Initial View
        self.check_login_status()
        
        log_event("Application started")

    def clear_container(self):
        """Clear the main container"""
        for widget in self.container.winfo_children():
            widget.destroy()

    def check_login_status(self):
        """Determine which view to show based on login status"""
        if self.session.current_user:
             self.show_main_interface()
        else:
             self.show_login_interface()

    def show_login_interface(self):
        """Show embedded login interface"""
        self.clear_container()
        
        # Center frame
        center_frame = ttk.Frame(self.container)
        center_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        # Styling
        chk_frame = ttk.Frame(center_frame, padding=40, bootstyle="secondary") # Card-like background
        chk_frame.pack(fill=BOTH, expand=True)
        
        ttk.Label(chk_frame, text="🔒", font=('Segoe UI', 64), bootstyle="inverse-secondary").pack(pady=(0, 20))
        ttk.Label(chk_frame, text="Cosmopolitan EDU", font=('Segoe UI', 24, 'bold'), bootstyle="inverse-secondary").pack()
        ttk.Label(chk_frame, text="Barcode System Login", font=('Segoe UI', 16), bootstyle="inverse-secondary").pack(pady=(0, 30))
        
        # Input area
        input_frame = ttk.Frame(chk_frame, padding=20)
        input_frame.pack(fill=X)
        
        ttk.Label(input_frame, text="Email Address:", font=('Segoe UI', 10, 'bold')).pack(anchor=W)
        self.email_entry = ttk.Entry(input_frame, font=('Segoe UI', 12), width=30)
        self.email_entry.pack(fill=X, pady=(5, 20))
        self.email_entry.focus()
        self.email_entry.bind('<Return>', lambda e: self.perform_login())
        
        login_btn = ttk.Button(
            input_frame, 
            text="Login", 
            command=self.perform_login, 
            bootstyle="primary", 
            width=20
        )
        login_btn.pack(pady=10, fill=X)
        
        self.login_status = ttk.Label(input_frame, text="", foreground="red", wraplength=300)
        self.login_status.pack(pady=10)

    def perform_login(self):
        email = self.email_entry.get().strip()
        if not email:
            self.login_status.config(text="Please enter an email address")
            return
            
        self.login_status.config(text="Verifying...", foreground="blue")
        
        def verify():
            try:
                is_valid, error = self.db.validate_user(email)
                if is_valid:
                    self.session.login(email)
                    self.root.after(0, lambda: self.show_main_interface())
                else:
                    self.root.after(0, lambda: self.login_status.config(text=error, foreground="red"))
            except Exception as e:
                self.root.after(0, lambda: self.login_status.config(text=f"Login error: {str(e)}", foreground="red"))
        
        threading.Thread(target=verify, daemon=True).start()

    def logout(self):
        """Logout and return to login screen"""
        self.session.logout()
        self.show_login_interface()

    def show_main_interface(self):
        """Show the main application interface"""
        self.clear_container()
        
        # Header
        header_frame = ttk.Frame(self.container, bootstyle="primary")
        header_frame.pack(fill=X, padx=0, pady=0)
        
        title_lbl = ttk.Label(
            header_frame, 
            text="🏷️ Barcode Printing System", 
            font=('Segoe UI', 16, 'bold'),
            bootstyle="inverse-primary",
            padding=15
        )
        title_lbl.pack(side=LEFT)
        
        # Current User & Logout
        user_frame = ttk.Frame(header_frame, bootstyle="primary")
        user_frame.pack(side=RIGHT, padx=15)
        
        self.user_label = ttk.Label(
            user_frame, 
            text=f"👤 {self.session.current_user}", 
            font=('Segoe UI', 10),
            bootstyle="inverse-primary"
        )
        self.user_label.pack(side=LEFT, padx=(0, 15))
        
        logout_btn = ttk.Button(
            user_frame,
            text="Logout",
            command=self.logout,
            bootstyle="light-outline",
            style="Logout.TButton" # Custom style if needed
        )
        logout_btn.pack(side=LEFT)

        # Main Content Area
        main_content = ttk.Frame(self.container, padding=20)
        main_content.pack(fill=BOTH, expand=True)
        
        # --- RIGHT PANEL (Logs) ---
        right_panel = ttk.Labelframe(main_content, text="📝 Activity Log", padding=15)
        right_panel.pack(side=RIGHT, fill=Y, expand=False, padx=(10, 0), ipadx=5)
        
        # Settings Buttons Frame (Added to Right Panel)
        settings_frame = ttk.Frame(right_panel)
        settings_frame.pack(fill=X, pady=(0, 10))
        
        self.settings_btn = ttk.Button(
            settings_frame, 
            text="⚙️ Printer", 
            command=self.show_settings_dialog,
            bootstyle="secondary-outline",
            width=10
        )
        self.settings_btn.pack(side=LEFT, fill=X, expand=True, padx=(0, 2))

        self.db_settings_btn = ttk.Button(
            settings_frame, 
            text="🗄️ DB", 
            command=self.show_database_settings_dialog,
            bootstyle="warning-outline",
            width=8
        )
        self.db_settings_btn.pack(side=LEFT, fill=X, expand=True, padx=(2, 0))

        self.status_text = ScrolledText(right_panel, width=40, wrap=WORD, state='disabled')
        self.status_text.pack(fill=BOTH, expand=True)

        # --- LEFT PANEL (Controls) ---
        left_panel = ttk.Labelframe(main_content, text="⚙️ Controls", padding=15)
        left_panel.pack(side=LEFT, fill=Y, expand=False, padx=(0, 10), ipadx=5)
        
        # Semester
        ttk.Label(left_panel, text="📅 Semester", font=('Segoe UI', 9, 'bold')).pack(anchor=W, pady=(5,0))
        self.semester_combo = ttk.Combobox(left_panel, state="readonly", width=35)
        self.semester_combo.pack(fill=X, pady=(2, 10))
        self.semester_combo.bind('<<ComboboxSelected>>', self.on_semester_selected)

        # Date (Added)
        ttk.Label(left_panel, text="📅 Date", font=('Segoe UI', 9, 'bold')).pack(anchor=W, pady=(5,0))
        self.date_combo = ttk.Combobox(left_panel, state="readonly", width=35)
        self.date_combo.pack(fill=X, pady=(2, 10))
        self.date_combo.bind('<<ComboboxSelected>>', self.on_date_selected)
        
        # Module
        ttk.Label(left_panel, text="📚 Module", font=('Segoe UI', 9, 'bold')).pack(anchor=W, pady=(5,0))
        self.module_combo = ttk.Combobox(left_panel, state="readonly", width=35)
        self.module_combo.pack(fill=X, pady=(2, 10))
        self.module_combo.bind('<<ComboboxSelected>>', self.on_module_selected)
        
        # Student List
        ttk.Label(left_panel, text="👥 Students", font=('Segoe UI', 9, 'bold')).pack(anchor=W, pady=(5,0))
        
        list_frame = ttk.Frame(left_panel)
        list_frame.pack(fill=BOTH, expand=True, pady=(2, 10))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.student_listbox = tk.Listbox(
            list_frame, 
            yscrollcommand=scrollbar.set,
            height=20, # Increased height since logs are gone
            selectmode=tk.SINGLE,
            font=('Consolas', 9),
            relief="flat",
            bd=1,
            highlightthickness=1,
            highlightbackground="#ccc"
        )
        self.student_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.student_listbox.yview)
        
        # Action Buttons
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill=X, pady=10)
        
        self.generate_btn = ttk.Button(
            btn_frame, 
            text="⚡ Generate Barcodes", 
            command=self.generate_barcode, 
            state='disabled',
            bootstyle="success-outline"
        )
        self.generate_btn.pack(fill=X, pady=5)
        
        self.preview_btn = ttk.Button(
            btn_frame, 
            text="🖼️ Print Preview", 
            command=self.show_print_preview, 
            state='disabled',
            bootstyle="info-outline"
        )
        self.preview_btn.pack(fill=X, pady=5)
        
        ttk.Button(
            btn_frame,
            text="🔍 Scan Barcode",
            command=self.show_scan_dialog,
            bootstyle="danger"
        ).pack(fill=X, pady=5)
        
        ttk.Separator(btn_frame, orient=HORIZONTAL).pack(fill=X, pady=10)

        self.print_btn = ttk.Button(
            btn_frame, 
            text="🖨️ Print Barcodes", 
            command=self.print_barcode, 
            state='disabled',
            bootstyle="primary"
        )
        self.print_btn.pack(fill=X, pady=5)
        
        # Printer Status
        self.printer_status_label = ttk.Label(left_panel, text="Checking printer...", font=('Segoe UI', 8), foreground="gray")
        self.printer_status_label.pack(anchor=W, pady=(5, 0))

        # --- CENTER PANEL (Preview) ---
        center_panel = ttk.Labelframe(main_content, text="👁️ Live Preview", padding=15)
        center_panel.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.preview_container = ttk.Frame(center_panel, bootstyle="secondary", padding=2) # Border effect
        self.preview_container.pack(fill=BOTH, expand=True)
        
        self.preview_label = ttk.Label(
            self.preview_container, 
            text="Waiting for generation...", 
            background='#f8f9fa', 
            anchor='center'
        )
        self.preview_label.pack(fill=BOTH, expand=True)
        
        # Load initial data
        self.load_semesters()
        self.check_printer_status()

    def add_status(self, message: str, error: bool = False):
        """Add message to status log"""
        # Only try to update text if we are in main view and widget exists
        if not hasattr(self, 'status_text') or not self.status_text.winfo_exists():
            # If not in main view, just log to file/console
            if error:
                log_event(message, 'error')
            else:
                log_event(message)
            return

        timestamp = time.strftime("%H:%M:%S")
        try:
            self.status_text.text.config(state='normal')
            
            tag = 'error' if error else 'info'
            self.status_text.text.tag_config('error', foreground='red')
            self.status_text.text.tag_config('info', foreground='black')
            
            self.status_text.text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
            self.status_text.text.see(tk.END)
            self.status_text.text.config(state='disabled')
        except Exception as e:
            log_event(f"Error updating status log: {e}", 'error')

        if error:
            log_event(message, 'error')
        else:
            log_event(message)

    def check_printer_status(self):
        """Check printer availability"""
        printers = self.printer.get_available_printers()
        self.add_status(f"Found {len(printers)} available printers")
        
        def check():
            try:
                if self.printer.is_printer_available():
                    status = f"Printer: {self.printer.printer_name} - Ready"
                    color = "success"
                else:
                    status = f"Printer: {self.printer.printer_name} - Offline"
                    color = "danger"
                
                # Check existence before config
                if hasattr(self, 'printer_status_label') and self.printer_status_label.winfo_exists():
                    self.root.after(0, lambda: self.printer_status_label.config(
                        text=status, bootstyle=color
                    ))
            except Exception as e:
                 if hasattr(self, 'printer_status_label') and self.printer_status_label.winfo_exists():
                    self.root.after(0, lambda: self.printer_status_label.config(
                        text=f"Printer Error: {str(e)}", bootstyle="danger"
                    ))
        
        threading.Thread(target=check, daemon=True).start()
    
    def load_semesters(self):
        """Load semesters from database"""
        self.add_status("Loading semesters...")
        
        def load():
            try:
                semesters = self.db.get_semesters()
                self.root.after(0, lambda: self.update_semesters(semesters))
            except Exception as e:
                self.root.after(0, lambda: self.add_status(f"Error loading semesters: {e}", error=True))
        
        threading.Thread(target=load, daemon=True).start()
    
    def update_semesters(self, semesters):
        """Update semester combobox"""
        # Safety check
        if not hasattr(self, 'semester_combo') or not self.semester_combo.winfo_exists():
            return
            
        if not semesters:
            self.add_status("No semesters found in database", error=True)
            return
        
        # Store semester data
        self.semesters = semesters
        
        # Create display values using actual column names
        semester_displays = []
        for sem in semesters:
            # Table has SemesterName column
            display = sem.get('SemesterName', f"Semester {sem.get('EntryID', '?')}")
            semester_displays.append(display)
        
        self.semester_combo['values'] = semester_displays
        self.add_status(f"Loaded {len(semesters)} semesters")
    
    def on_semester_selected(self, event):
        """Handle semester selection"""
        selected_index = self.semester_combo.current()
        if selected_index >= 0:
            semester = self.semesters[selected_index]
            self.session.set_semester(semester)
            
            semester_code = semester.get('SemesterCode')
            self.add_status(f"Loading dates for {semester.get('SemesterName', semester_code)}...")
            
            # Reset dependent combos
            self.date_combo.set('')
            self.date_combo['values'] = []
            self.module_combo.set('')
            self.module_combo['values'] = []
            
            # Load dates
            def load():
                try:
                    dates = self.db.get_exam_dates(semester_code)
                    self.root.after(0, lambda: self.update_dates(dates))
                except Exception as e:
                    self.root.after(0, lambda: self.add_status(f"Error loading dates: {e}", error=True))
            
            threading.Thread(target=load, daemon=True).start()
    
    def update_dates(self, dates):
        """Update date combobox"""
        if not hasattr(self, 'date_combo') or not self.date_combo.winfo_exists():
            return
            
        if not dates:
            self.add_status("No exam dates found for semester", error=True)
            return

        self.exam_dates = dates
        self.date_combo['values'] = dates
        self.add_status(f"Loaded {len(dates)} exam dates")

    def on_date_selected(self, event):
        """Handle date selection"""
        date = self.date_combo.get()
        if date:
            semester_code = self.session.selected_semester.get('SemesterCode')
            self.add_status(f"Loading modules for {date}...")
            
            # Load modules for this date
            def load():
                try:
                    modules = self.db.get_modules_by_date(date, semester_code)
                    self.root.after(0, lambda: self.update_modules(modules))
                except Exception as e:
                    self.root.after(0, lambda: self.add_status(f"Error loading modules: {e}", error=True))
            
            threading.Thread(target=load, daemon=True).start()
    
    def update_modules(self, modules):
        """Update module combobox"""
         # Safety check
        if not hasattr(self, 'module_combo') or not self.module_combo.winfo_exists():
            return

        if not modules:
            self.add_status("No modules found for selected semester", error=True)
            self.module_combo['values'] = []
            return
        
        # Store module data
        self.modules = modules
        
        # Get module names
        module_displays = []
        for mod in modules:
            module_code = mod.get('ModuleCode', '')
            
            # Get module name from database function
            module_name = self.db.get_module_name(module_code)
            
            if module_name:
                display = f"{module_code} - {module_name}"
            else:
                display = module_code
            
            module_displays.append(display)
        
        self.module_combo['values'] = module_displays
        self.add_status(f"Loaded {len(modules)} modules")
    
    def on_module_selected(self, event):
        """Handle module selection"""
        selected_index = self.module_combo.current()
        if selected_index >= 0:
            module = self.modules[selected_index]
            self.session.set_module(module)
            
            module_code = module.get('ModuleCode')
            semester_code = self.session.selected_semester.get('SemesterCode')
            
            self.add_status(f"Module selected: {module_code}")
            self.add_status(f"Loading students for {module_code}...")
            
            # Load students for this module
            def load_students():
                try:
                    barcode_list = self.db.get_barcode_data(module_code, semester_code)
                    self.root.after(0, lambda: self.update_student_list(barcode_list))
                except Exception as e:
                    self.root.after(0, lambda: self.add_status(f"Error loading students: {e}", error=True))
            
            threading.Thread(target=load_students, daemon=True).start()
    
    def update_student_list(self, barcode_list):
        """Update student listbox with barcode data"""
         # Safety check
        if not hasattr(self, 'student_listbox') or not self.student_listbox.winfo_exists():
            return

        self.student_listbox.delete(0, tk.END)
        self.students_data = barcode_list
        self.print_status = {}
        
        if not barcode_list:
            self.add_status("No students found for this module", error=True)
            return
        
        self.add_status(f"Found {len(barcode_list)} student(s)")
        
        # Add students to listbox with status icons
        for i, student in enumerate(barcode_list):
            student_id = student.get('StudentID', 'Unknown')
            seat_no = student.get('SeatNo', '?')
            barcode = student.get('Barcode', 'N/A')
            
            # Initial status is pending (yellow)
            self.print_status[i] = 'pending'
            status_icon = '⚠'  # Yellow caution
            
            # Format: [Status] Barcode - Seat: XX - Hall
            hall = student.get('VenueName', 'Hall ?')
            # User request: "instead of studentid show exam_barcode.Barcode"
            display = f"{status_icon} {barcode} - Seat {seat_no} - {hall}"
            self.student_listbox.insert(tk.END, display)
        
        # Enable generate button
        self.generate_btn.config(state='normal')
    
    def generate_barcode(self):
        """Generate barcodes for ALL students in the module"""
        if not self.students_data:
            messagebox.showwarning("No Students", "Please select a module first")
            return
        
        total_students = len(self.students_data)
        self.add_status(f"Generating {total_students} barcode(s)...")
        
        def generate():
            try:
                all_barcodes = []
                
                # Generate barcode for each student
                for i, student in enumerate(self.students_data):
                    barcode_value = student.get('Barcode')
                    student_id = student.get('StudentID', 'Unknown')
                    
                    if not barcode_value:
                        self.root.after(0, lambda sid=student_id: self.add_status(
                            f"Skipping {sid} - no barcode value", error=True
                        ))
                        continue
                    
                    # Generate barcode using Barcode field if available, else StudentID
                    barcode_val = student.get('Barcode', student_id)
                    
                    # Generate image
                    card_image = self.barcode_gen.create_barcode_card(barcode_value=str(barcode_val))
                    if card_image:
                        all_barcodes.append(card_image)
                        self.root.after(0, lambda p=i+1, t=total_students:
                                       self.add_status(f"Generated {p}/{t} barcodes"))
                
                # Store all barcodes
                self.all_barcode_images = all_barcodes
                
                # Create preview showing all barcodes
                if all_barcodes:
                    preview_image = self.create_preview_grid(all_barcodes)
                    self.root.after(0, lambda: self.update_preview(preview_image))
                    self.root.after(0, lambda: self.add_status(
                        f"✓ Generated {len(all_barcodes)} barcode(s) - Ready to print!"
                    ))
                    self.root.after(0, lambda: self.print_btn.config(state='normal'))
                    self.root.after(0, lambda: self.preview_btn.config(state='normal'))
                
            except Exception as e:
                self.root.after(0, lambda: self.add_status(
                    f"Error generating barcodes: {str(e)}", error=True
                ))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def create_preview_grid(self, images: list) -> Image.Image:
        """Create a grid preview showing all barcode cards in rows and columns"""
        if not images:
            return None
        
        # Use 4 columns for compact grid layout
        cols = 4
        rows = (len(images) + cols - 1) // cols
        
        # Get size of first image
        img_width, img_height = images[0].size
        
        # Use full resolution (no scaling down)
        scaled_width = img_width
        scaled_height = img_height
        
        # Add spacing between images
        spacing = 10
        
        # Calculate grid dimensions
        grid_width = (scaled_width * cols) + (spacing * (cols + 1))
        grid_height = (scaled_height * rows) + (spacing * (rows + 1))
        
        # Create light gray background
        grid = Image.new('RGB', (grid_width, grid_height), (240, 240, 240))
        
        # Paste each barcode into grid
        for i, img in enumerate(images):
            # Scale the barcode for preview
            
            row = i // cols
            col = i % cols
            
            x = spacing + (col * (scaled_width + spacing))
            y = spacing + (row * (scaled_height + spacing))
            
            grid.paste(img, (x, y))
        
        log_event(f"Created preview grid: {len(images)} barcodes in {rows} row(s) x {cols} column(s)")
        return grid
    
    def update_preview(self, image: Image.Image):
        """Update preview with generated barcode(s)"""
        if not hasattr(self, 'preview_label') or not self.preview_label.winfo_exists():
            return
            
        if not image:
            return
            
        # Resize for preview - fit to preview area width, allow vertical scrolling
        preview_max_width = 1200 
        
        # Calculate scaling
        if image.width > preview_max_width:
            scale = preview_max_width / image.width
            preview_width = int(image.width * scale)
            preview_height = int(image.height * scale)
            preview_img = image.resize((preview_width, preview_height), Image.Resampling.LANCZOS)
        else:
            preview_img = image
        
        self.preview_photo = ImageTk.PhotoImage(preview_img)
        self.preview_label.config(image=self.preview_photo, text="", anchor='nw') # Anchor to Top-Left

    def show_print_preview(self):
        """Show dedicated print preview window"""
        if not hasattr(self, 'all_barcode_images') or not self.all_barcode_images:
            return

        preview_window = tk.Toplevel(self.root)
        preview_window.title(f"Print Preview - {config.PRINTER_CONFIG['card_width_mm']}mm x {config.PRINTER_CONFIG['card_height_mm']}mm Labels")
        preview_window.geometry("600x800")
        
        # Main scrollable container
        container = ttk.Frame(preview_window)
        container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(container, background='#e0e0e0')
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add labels to preview
        ttk.Label(scrollable_frame, text=f"Print Preview: {len(self.all_barcode_images)} Labels", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Keep references to images
        preview_window.images = []
        
        for i, img in enumerate(self.all_barcode_images):
            # Frame for each label (simulating paper)
            page_frame = ttk.Frame(scrollable_frame, padding=10)
            page_frame.pack(pady=5)
            
            # Label info
            student = self.students_data[i]
            hall = student.get('VenueName', 'Hall ?')
            barcode_val = student.get('Barcode', student.get('StudentID'))
            info_text = f"#{i+1}: {barcode_val} (Seat: {student.get('SeatNo')} - {hall})"
            ttk.Label(page_frame, text=info_text).pack()
            
            # Show image with border (simulating cut line)
            photo = ImageTk.PhotoImage(img)
            preview_window.images.append(photo)
            
            lbl = tk.Label(page_frame, image=photo, relief='solid', borderwidth=1)
            lbl.pack(pady=2)
            
            ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', padx=50, pady=5)
    
    def show_database_settings_dialog(self):
        """Show dialog to configure database settings"""
        import settings_manager
        
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Database Connection Settings")
        dialog.geometry("400x550")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Current settings
        current = self.db.db_config
        
        # Form frame
        form = ttk.Frame(dialog, padding="20")
        form.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form, text="MySQL Connection Details", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 20))
        
        # Fields
        entries = {}
        fields = [
            ('Host:', 'host'),
            ('Port:', 'port'),
            ('Database:', 'database'),
            ('User:', 'user'),
            ('Password:', 'password')
        ]
        
        for i, (label, key) in enumerate(fields):
            row = i + 1
            ttk.Label(form, text=label).grid(row=row, column=0, sticky='w', pady=10)
            
            val = current.get(key, '')
            var = tk.StringVar(value=str(val))
            
            if key == 'password':
                entry = ttk.Entry(form, textvariable=var, show="*", width=25)
            else:
                entry = ttk.Entry(form, textvariable=var, width=25)
                
            entry.grid(row=row, column=1, sticky='w', pady=10)
            entries[key] = var
            
        # Test Connection Logic
        status_lbl = ttk.Label(form, text="", foreground="gray")
        status_lbl.grid(row=len(fields)+1, column=0, columnspan=2, pady=10)
        
        def test_conn():
            status_lbl.config(text="Testing connection...", foreground="blue")
            dialog.update()
            
            # Temporary config
            test_config = {
                'host': entries['host'].get(),
                'user': entries['user'].get(),
                'password': entries['password'].get(),
                'database': entries['database'].get(),
                'port': int(entries['port'].get() or 3306),
                'raise_on_warnings': True,
                'connection_timeout': 5
            }
            
            import mysql.connector
            try:
                conn = mysql.connector.connect(**test_config)
                if conn.is_connected():
                    conn.close()
                    status_lbl.config(text="✅ Connection Successful!", foreground="green", bootstyle="success")
                    return True
            except Exception as e:
                status_lbl.config(text=f"❌ Failed: {str(e)}", foreground="red", bootstyle="danger")
                return False
                
        def save():
            try:
                # Build new config
                new_settings = settings_manager.load_db_settings() # Start with current to keep other keys
                new_settings.update({
                    'host': entries['host'].get(),
                    'user': entries['user'].get(),
                    'password': entries['password'].get(),
                    'database': entries['database'].get(),
                    'port': int(entries['port'].get() or 3306)
                })
                
                # Save
                if settings_manager.save_db_settings(new_settings):
                    self.db.db_config = new_settings
                    # Re-init pool? Ideally yes, but complex. 
                    # For now just save, user might need to restart app or we can try to re-init
                    self.add_status("Database settings saved. Please restart if connection fails.")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to save settings")
            except ValueError:
                messagebox.showerror("Invalid Input", "Port must be a number")

        # Buttons
        btn_frame = ttk.Frame(dialog, padding="20")
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Test Connection", command=test_conn, bootstyle="info-outline").pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Save", command=save, bootstyle="success").pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, bootstyle="secondary").pack(side=tk.RIGHT, padx=5)

    def show_settings_dialog(self):
        """Show dialog to configure printer settings"""
        import settings_manager
        
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Printer Settings")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Initial load of settings if not loaded
        if not hasattr(self, 'settings'):
            self.settings = settings_manager.load_settings()

        # Current settings
        current = self.settings
        
        # Form frame
        form = ttk.Frame(dialog, padding="20")
        form.pack(fill=tk.BOTH, expand=True)
        
        # Label Dimensions
        ttk.Label(form, text="Label Dimensions (mm)", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        ttk.Label(form, text="Width (mm):").grid(row=1, column=0, sticky='w', pady=5)
        width_var = tk.DoubleVar(value=current.get('label_width_mm', 60.0))
        ttk.Entry(form, textvariable=width_var, width=10).grid(row=1, column=1, sticky='w', pady=5)
        
        ttk.Label(form, text="Height (mm):").grid(row=2, column=0, sticky='w', pady=5)
        height_var = tk.DoubleVar(value=current.get('label_height_mm', 40.0))
        ttk.Entry(form, textvariable=height_var, width=10).grid(row=2, column=1, sticky='w', pady=5)
        
        # Print Offsets
        ttk.Label(form, text="Print Offsets (mm)", font=('Arial', 10, 'bold')).grid(
            row=3, column=0, columnspan=2, sticky='w', pady=(20, 10))
            
        ttk.Label(form, text="X Offset (Left/Right):").grid(row=4, column=0, sticky='w', pady=5)
        offset_x_var = tk.DoubleVar(value=current.get('offset_x_mm', 0.0))
        ttk.Entry(form, textvariable=offset_x_var, width=10).grid(row=4, column=1, sticky='w', pady=5)
        
        ttk.Label(form, text="Y Offset (Up/Down):").grid(row=5, column=0, sticky='w', pady=5)
        offset_y_var = tk.DoubleVar(value=current.get('offset_y_mm', 0.0))
        ttk.Entry(form, textvariable=offset_y_var, width=10).grid(row=5, column=1, sticky='w', pady=5)
        
        def save():
            try:
                # Update settings dictionary
                new_settings = self.settings.copy()
                new_settings['label_width_mm'] = width_var.get()
                new_settings['label_height_mm'] = height_var.get()
                new_settings['offset_x_mm'] = offset_x_var.get()
                new_settings['offset_y_mm'] = offset_y_var.get()
                
                # Save to file
                if settings_manager.save_settings(new_settings):
                    self.settings = new_settings
                    self.add_status("Settings saved. Please regenerate barcodes.")
                    
                    # Update generator with new settings
                    self.barcode_gen = BarcodeGenerator(new_settings)
                    
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to save settings file")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numbers")
        
        # Buttons
        btn_frame = ttk.Frame(dialog, padding="20")
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Save Settings", command=save).pack(side=tk.RIGHT, padx=5)

    def print_barcode(self):
        """Print ALL generated barcodes using TSPL (Native Command)"""
        if not self.students_data:
            messagebox.showwarning("No Data", "Please generate barcodes first.")
            return

        if not messagebox.askyesno("Confirm Print", f"Are you sure you want to print {len(self.students_data)} labels?"):
            return

        # Disable button during printing
        self.print_btn.config(state='disabled')
        self.add_status("Generating TSPL commands and sending to printer...")
            
        def run_print():
            try:
                # Use Native TSPL Printing
                success = self.printer.print_tspl_data(self.students_data)
                
                if success:
                    self.root.after(0, lambda: self.add_status("✅ Print job sent successfully!", "success"))
                    self.root.after(0, lambda: messagebox.showinfo("Success", "Batch print job sent to printer."))
                    self.root.after(0, self.mark_all_printed)
                else:
                    self.root.after(0, lambda: self.add_status("❌ Print job failed.", "error"))
                    self.root.after(0, lambda: messagebox.showerror("Error", "Failed to send print job."))
            
            except Exception as e:
                self.root.after(0, lambda: self.add_status(f"Print error: {e}", "error"))
                log_event(f"Print thread error: {e}", 'error')
            finally:
                self.root.after(0, lambda: self.print_btn.config(state='normal'))
        
        threading.Thread(target=run_print, daemon=True).start()

    def mark_all_printed(self):
        """Mark all students as printed in the UI"""
        for i in range(len(self.students_data)):
            self.print_status[i] = 'success'
            self.update_student_status(i)
    
    def show_print_summary(self, success: int, failed: int, total: int):
        """Show print job summary"""
        summary = f"Print Job Sent!\n\n"
        summary += f"Total: {total}\n"
        
        if failed == 0:
            summary += "Job sent to printer successfully."
            messagebox.showinfo("Print Sent", summary)
            self.add_status(f"✓ Batch job for {total} barcode(s) sent successfully!")
        else:
            summary += "Failed to send print job."
            messagebox.showwarning("Print Error", summary)
            self.add_status(f"Print failed to send")
    
    def update_student_status(self, index: int, status: str):
        """Update student print status in listbox"""
        if index >= len(self.students_data):
            return
        
        student = self.students_data[index]
        student_id = student.get('StudentID', 'Unknown')
        seat_no = student.get('SeatNo', '?')
        
        # Update status
        self.print_status[index] = status
        
        # Choose icon based on status
        if status == 'success':
            icon = '✓'  # Green check
        elif status == 'failed':
            icon = '✗'  # Red X
        else:
            icon = '⚠'  # Yellow caution (pending)
        
        barcode_val = student.get('Barcode', student_id)
        
        # Update listbox item
        hall = student.get('VenueName', 'Hall ?')
        display = f"{icon} {barcode_val} - Seat {seat_no} - {hall}"
        self.student_listbox.delete(index)
        self.student_listbox.insert(index, display)
        
        # Keep selection if any
        # self.student_listbox.selection_set(index)

    def show_scan_dialog(self):
        """Show continuous scan dialog"""
        self.scan_popup = tk.Toplevel(self.root)
        self.scan_popup.title("Scan Barcode")
        self.scan_popup.geometry("600x500")
        
        # Center popup
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 300
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 250
        self.scan_popup.geometry(f"+{x}+{y}")
        
        # Header
        header = ttk.Frame(self.scan_popup, bootstyle="danger", padding=15)
        header.pack(fill=X)
        ttk.Label(header, text="🔍 Ready to Scan", font=('Segoe UI', 14, 'bold'), 
                 bootstyle="inverse-danger").pack()
        
        # Input Area
        input_frame = ttk.Frame(self.scan_popup, padding=20)
        input_frame.pack(fill=X)
        
        ttk.Label(input_frame, text="Scan Barcode Here:", font=('Segoe UI', 10)).pack(anchor=W)
        self.scan_entry = ttk.Entry(input_frame, font=('Consolas', 14))
        self.scan_entry.pack(fill=X, pady=(5, 0))
        self.scan_entry.focus_set()
        
        # Bind Enter key
        self.scan_entry.bind('<Return>', self.process_scan)
        
        # Result Area
        self.result_frame = ttk.Frame(self.scan_popup, padding=20)
        self.result_frame.pack(fill=BOTH, expand=True)
        
        # Initial Placeholder
        self.placeholder_lbl = ttk.Label(
            self.result_frame, 
            text="Waiting for scan...", 
            font=('Segoe UI', 12), 
            foreground="gray"
        )
        self.placeholder_lbl.pack(pady=50)

    def process_scan(self, event):
        """Handle scan input"""
        barcode = self.scan_entry.get().strip()
        if not barcode:
            return
            
        self.scan_entry.delete(0, tk.END)
        # Refocus immediately
        self.scan_entry.focus_set()
        
        self.add_status(f"Scanning: {barcode}...")
        
        # Run lookup
        threading.Thread(target=lambda: self.lookup_barcode_continuous(barcode), daemon=True).start()

    def lookup_barcode_continuous(self, barcode):
        """Lookup and update the existing scan window"""
        try:
            result = self.db.get_student_by_barcode(barcode)
            self.root.after(0, lambda: self.update_scan_results(result, barcode))
        except Exception as e:
            self.root.after(0, lambda: self.add_status(f"Scan error: {e}", error=True))

    def update_scan_results(self, data, scanned_barcode):
        """Update the scan window content"""
        # Safety Check
        if not hasattr(self, 'scan_popup') or not self.scan_popup.winfo_exists():
            return
            
        # Clear previous results
        for widget in self.result_frame.winfo_children():
            widget.destroy()
            
        if not data:
            # Show Error
            ttk.Label(self.result_frame, text="❌ Student Not Found", 
                     font=('Segoe UI', 16, 'bold'), foreground="red").pack(pady=10)
            ttk.Label(self.result_frame, text=f"Barcode: {scanned_barcode}", 
                     font=('Consolas', 12)).pack()
            # Play error sound/visuals if needed
            return

        # Show Success Data
        ttk.Label(self.result_frame, text="✅ Student Verified", 
                 font=('Segoe UI', 16, 'bold'), foreground="green").pack(pady=(0, 20))
                 
        # Grid layout for details
        grid_frame = ttk.Frame(self.result_frame)
        grid_frame.pack(fill=X)
        
        details = [
            ("Student Name:", data.get('StudentName', 'Unknown')), # Assuming we might fetch name later, or just ID
            ("Student ID:", data.get('StudentID', 'N/A')),
            ("Level:", data.get('StudentLevel', 'N/A')),
            ("---", "---"),
            ("Exam Date:", str(data.get('ExamDate', 'N/A'))),
            ("Module:", data.get('ModuleCode', 'N/A')),
            ("Venue:", data.get('VenueName', 'N/A')),
            ("Seat Number:", str(data.get('SeatNo', 'N/A'))),
        ]
        
        for i, (label, value) in enumerate(details):
            if label == "---":
                ttk.Separator(grid_frame, orient=HORIZONTAL).grid(row=i, column=0, columnspan=2, sticky='ew', pady=10)
                continue
                
            # Labels
            ttk.Label(grid_frame, text=label, font=('Segoe UI', 11, 'bold'), foreground="#555").grid(row=i, column=0, sticky='w', pady=5, padx=20)
            
            # Values (Highlight critical info)
            if "Seat" in label or "Venue" in label:
                ttk.Label(grid_frame, text=value, font=('Segoe UI', 14, 'bold'), foreground="#d9534f").grid(row=i, column=1, sticky='w', pady=5)
            else:
                ttk.Label(grid_frame, text=value, font=('Segoe UI', 12)).grid(row=i, column=1, sticky='w', pady=5)

    


def main():
    """Main entry point"""
    root = ttk.Window(themename="cosmo")
    app = BarcodeprinterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
