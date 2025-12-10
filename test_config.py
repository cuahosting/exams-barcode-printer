"""
Quick test script to verify database and printer configuration
Run this before using the main application
"""
import sys

print("=" * 60)
print("Barcode Printer Application - Configuration Test")
print("=" * 60)

# Test 1: Import modules
print("\n[1/4] Testing module imports...")
try:
    import config
    from database import DatabaseManager
    from printer import PrinterManager
    from barcode_generator import BarcodeGenerator
    print("[OK] All modules imported successfully")
except Exception as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)

# Test 2: Database connection
print("\n[2/4] Testing database connection...")
try:
    db = DatabaseManager()
    if db.test_connection():
        print(f"[OK] Connected to database: {config.DB_CONFIG['database']}")
        print(f"  Host: {config.DB_CONFIG['host']}")
        print(f"  User: {config.DB_CONFIG['user']}")
    else:
        print("[FAIL] Database connection failed")
        sys.exit(1)
except Exception as e:
    print(f"[FAIL] Database error: {e}")
    sys.exit(1)

# Test 3: Database tables and data
print("\n[3/4] Testing database tables...")
try:
    # Test semesters
    semesters = db.get_semesters()
    print(f"[OK] Found {len(semesters)} semester(s) in timetable_semester")
    
    if semesters:
        sem = semesters[0]
        print(f"  Sample semester: {sem.get('SemesterName')} (Code: {sem.get('SemesterCode')})")
        
        # Test modules for first semester
        modules = db.get_modules_by_semester(sem.get('SemesterCode'))
        print(f"[OK] Found {len(modules)} module(s) for semester {sem.get('SemesterCode')}")
        
        if modules:
            mod_code = modules[0].get('ModuleCode')
            print(f"  Sample module code: {mod_code}")
            
            # Test getmodulename function
            mod_name = db.get_module_name(mod_code)
            if mod_name:
                print(f"[OK] getmodulename() function works: '{mod_name}'")
            else:
                print(f"[WARN] getmodulename() returned no name for {mod_code}")
            
            # Test barcode data
            barcode_list = db.get_barcode_data(mod_code, sem.get('SemesterCode'))
            if barcode_list:
                print(f"[OK] Found {len(barcode_list)} barcode record(s) for module {mod_code}")
                barcode_val = barcode_list[0].get('Barcode')
                if barcode_val:
                    print(f"  Sample barcode value: {barcode_val}")
                    print(f"  Student ID: {barcode_list[0].get('StudentID')}")
                    print(f"  Seat No: {barcode_list[0].get('SeatNo')}")
                else:
                    print(f"[WARN] Barcode field is empty")
            else:
                print(f"[WARN] No barcode data found for module {mod_code}")
    else:
        print("[WARN] No semesters found in database")
        
except Exception as e:
    print(f"[FAIL] Database query error: {e}")

# Test 4: Printer detection
print("\n[4/4] Testing printer configuration...")
try:
    pm = PrinterManager()
    printers = pm.get_available_printers()
    
    print(f"[OK] Found {len(printers)} printer(s) in Windows:")
    for p in printers:
        print(f"  - {p}")
    
    if pm.is_printer_available():
        print(f"[OK] Target printer '{pm.printer_name}' is available")
    else:
        print(f"[WARN] Target printer '{config.PRINTER_CONFIG['printer_name']}' not found")
        print(f"  Update PRINTER_CONFIG['printer_name'] in config.py")
        
except Exception as e:
    print(f"[FAIL] Printer error: {e}")

# Summary
print("\n" + "=" * 60)
print("Configuration Test Complete")
print("=" * 60)
print("\nIf all tests passed, you can run the application with:")
print("  python main.py")
print("\nAuthorized users:")
for user in config.AUTHORIZED_USERS:
    print(f"  - {user}")
print()
