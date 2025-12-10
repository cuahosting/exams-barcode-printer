# Configuration Guide for Barcode Printer Application

This guide will help you configure the application for your specific environment.

## Step 1: Database Configuration

Open `config.py` and update the `DB_CONFIG` section:

### Finding Your Database Details

1. **Host**: Your MySQL server address
   - If MySQL is on the same computer: `localhost` or `127.0.0.1`
   - If on another server: IP address or hostname

2. **Database**: The name of your database containing the exam tables

3. **User & Password**: Your MySQL credentials with read access to:
   - `timetable_semester`
   - `exam_timetable_hall`
   - `exam_barcode`
   - `getmodulename()` function

### Example Configuration

```python
DB_CONFIG = {
    'host': 'localhost',          # or your server IP
    'database': 'cosmopolitan_db', # your database name
    'user': 'exam_user',          # your MySQL username
    'password': 'secure_password', # your MySQL password
    'port': 3306,
    'raise_on_warnings': True,
    'autocommit': False
}
```

## Step 2: Printer Configuration

### Finding Your Printer Name

1. Open **Windows Settings** (Win + I)
2. Navigate to **Devices** > **Printers & scanners**
3. Find your XPrinter XP-365B in the list
4. Copy the **exact name** as it appears

### Common Printer Names

- `XP-365B`
- `XPrinter XP-365B`
- `USB Thermal Printer`

### Update config.py

```python
PRINTER_CONFIG = {
    'printer_name': 'XP-365B',  # EXACT name from Windows
    'card_width_mm': 85.6,      # Credit card width
    'card_height_mm': 54.0,     # Credit card height
    'dpi': 300,                 # Print resolution
}
```

### Custom Card Sizes

If you're using custom-sized cards, measure and update:

```python
PRINTER_CONFIG = {
    'printer_name': 'XP-365B',
    'card_width_mm': 100.0,     # Your width in mm
    'card_height_mm': 60.0,     # Your height in mm
    'dpi': 300,
}
```

## Step 3: Verify Database Structure

### Required Tables

Ensure your database has these tables with the correct columns:

#### 1. timetable_semester
```sql
-- Should have these columns (column names may vary):
-- id (INT, PRIMARY KEY)
-- name or semester_name (VARCHAR)
-- Other columns as needed

SELECT * FROM timetable_semester LIMIT 1;
```

#### 2. exam_timetable_hall
```sql
-- Should have these columns:
-- semester_id (INT, references timetable_semester.id)
-- module_code (VARCHAR)
-- Other columns as needed

SELECT * FROM exam_timetable_hall LIMIT 1;
```

#### 3. exam_barcode
```sql
-- Should have these columns:
-- module_code (VARCHAR)
-- Barcode or barcode (VARCHAR/TEXT) - the actual barcode value
-- Other columns as needed

SELECT * FROM exam_barcode LIMIT 1;
```

### MySQL Function: getmodulename

Check if the function exists:

```sql
SHOW CREATE FUNCTION getmodulename;
```

If it doesn't exist, you need to create it. Example:

```sql
DELIMITER //

CREATE FUNCTION getmodulename(code VARCHAR(50))
RETURNS VARCHAR(255)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE module_name VARCHAR(255);
    
    -- Adjust this query based on your actual table structure
    SELECT name INTO module_name 
    FROM modules 
    WHERE module_code = code 
    LIMIT 1;
    
    RETURN module_name;
END //

DELIMITER ;
```

**Note**: Adjust the query inside the function based on where module names are stored in your database.

## Step 4: Test Connection

Before running the full application, test your database connection:

```bash
cd C:\Users\NEW USER\Project\cosmopolitanedu\printer
python
```

In Python:

```python
from database import DatabaseManager

# Test connection
db = DatabaseManager()
if db.test_connection():
    print("✓ Database connected successfully!")
    
    # Test queries
    semesters = db.get_semesters()
    print(f"✓ Found {len(semesters)} semesters")
    
    if semesters:
        sem_id = semesters[0]['id']
        modules = db.get_modules_by_semester(sem_id)
        print(f"✓ Found {modules} modules for first semester")
else:
    print("✗ Database connection failed")
```

## Step 5: Test Printer

Test if printer is detected:

```python
from printer import PrinterManager

pm = PrinterManager()

# List available printers
printers = pm.get_available_printers()
print("Available printers:")
for p in printers:
    print(f"  - {p}")

# Check if XPrinter is available
if pm.is_printer_available():
    print(f"✓ Printer '{pm.printer_name}' is ready")
else:
    print("✗ Printer not found")
```

## Common Configuration Issues

### Issue: "Database connection failed"

**Possible causes:**
- MySQL server not running
- Incorrect credentials
- Firewall blocking connection
- Database doesn't exist

**Solutions:**
1. Start MySQL service: `net start MySQL80` (or your version)
2. Verify credentials in MySQL Workbench
3. Check firewall settings
4. Ensure database exists: `SHOW DATABASES;`

### Issue: "Printer not found"

**Possible causes:**
- Printer not installed in Windows
- Wrong printer name
- Printer offline
- Driver issues

**Solutions:**
1. Install XPrinter driver from manufacturer
2. Print test page from Windows to verify
3. Copy exact name from Windows Settings
4. Ensure printer is set to "Online" status

### Issue: "getmodulename function not found"

**Possible causes:**
- Function doesn't exist
- Function in different database
- User lacks EXECUTE permission

**Solutions:**
1. Create the function (see Step 3)
2. Ensure you're connecting to the right database
3. Grant permissions: `GRANT EXECUTE ON FUNCTION getmodulename TO 'user'@'host';`

### Issue: "No semesters found"

**Possible causes:**
- Empty table
- Connection to wrong database
- Table structure mismatch

**Solutions:**
1. Verify data exists: `SELECT COUNT(*) FROM timetable_semester;`
2. Check database name in config.py
3. Verify table columns match expected structure

## Environment-Specific Notes

### For Development/Testing

You can use a test database:

```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'cosmopolitan_test',  # Test database
    'user': 'test_user',
    'password': 'test_pass',
    'port': 3306,
}
```

### For Production

Use secure credentials and consider:
- Using environment variables for passwords
- Restricting database user permissions (SELECT only)
- Enabling SSL for database connections

### Multiple Printers

If you have multiple thermal printers, you can create different config profiles:

```python
# config_xp365.py
PRINTER_CONFIG = {
    'printer_name': 'XP-365B',
    ...
}

# config_xp470.py
PRINTER_CONFIG = {
    'printer_name': 'XP-470B',
    ...
}
```

## Next Steps

After configuration:

1. ✓ Install dependencies: `pip install -r requirements.txt`
2. ✓ Update `config.py`
3. ✓ Test database connection
4. ✓ Test printer detection
5. ✓ Run application: `python main.py`
6. ✓ Login with authorized email
7. ✓ Generate and print test barcode

## Getting Help

If you encounter issues:

1. Check `barcode_printer.log` for error messages
2. Verify all configuration steps above
3. Test database queries manually in MySQL Workbench
4. Ensure printer works from other applications
5. Contact system administrators for database/printer support
