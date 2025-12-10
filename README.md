# Barcode Printer Application

A Python desktop application for generating and printing exam barcodes for Cosmopolitan University.

## Features

- **User Authentication**: Secure login for authorized users
- **Semester Selection**: Choose from available semesters
- **Module Selection**: Select modules with automatic name lookup
- **Barcode Generation**: Create professional barcode cards
- **Print Support**: Direct printing to XPrinter XP-365B thermal printer
- **Preview**: View generated barcode before printing

## Requirements

- Python 3.8 or higher
- Windows OS (for printer support)
- MySQL database with required tables
- XPrinter XP-365B configured in Windows

## Installation

### 1. Install Python Dependencies

```bash
cd C:\Users\NEW USER\Project\cosmopolitanedu\printer
pip install -r requirements.txt
```

### 2. Configure Database

Edit `config.py` and update the database settings:

```python
DB_CONFIG = {
    'host': 'your_mysql_host',
    'database': 'your_database_name',
    'user': 'your_username',
    'password': 'your_password',
    'port': 3306,
}
```

### 3. Configure Printer

Update the printer name in `config.py`:

```python
PRINTER_CONFIG = {
    'printer_name': 'XP-365B',  # Exact name from Windows Settings
    'card_width_mm': 85.6,
    'card_height_mm': 54.0,
    'dpi': 300,
}
```

To find your printer name:
1. Open Windows Settings
2. Go to Devices > Printers & scanners
3. Copy the exact name of your XPrinter

## Database Requirements

The application expects the following MySQL structure:

### Tables

1. **timetable_semester**
   - Contains semester information
   - Must have an `id` column
   - Should have `name` or `semester_name` column

2. **exam_timetable_hall**
   - Contains module codes per semester
   - Must have `semester_id` and `module_code` columns

3. **exam_barcode**
   - Contains barcode data for each module
   - Must have `module_code` and `Barcode` (or `barcode`) columns

### MySQL Function

The application uses a MySQL function `getmodulename(module_code)` to retrieve module names. Ensure this function exists in your database.

Example:
```sql
CREATE FUNCTION getmodulename(code VARCHAR(50))
RETURNS VARCHAR(255)
DETERMINISTIC
BEGIN
    DECLARE module_name VARCHAR(255);
    SELECT name INTO module_name FROM modules WHERE module_code = code;
    RETURN module_name;
END;
```

## Usage

### Running the Application

```bash
python main.py
```

### Workflow

1. **Login**: Enter your authorized email address
   - zainab.attahiru@cosmopolitan.edu.ng
   - hayat.suleiman@cosmopolitan.edu.ng

2. **Select Semester**: Choose from the dropdown

3. **Select Module**: Choose a module (shows code and name)

4. **Generate Barcode**: Click "Generate Barcode" to create the card

5. **Preview**: Review the barcode card in the preview pane

6. **Print**: Click "Print Barcode" to send to XPrinter

## Card Layout

Each barcode card includes:
- Module code (top)
- Code128 barcode (center)
- Module name (below barcode)
- Semester information (bottom)

Card dimensions: 85.6mm x 54mm (credit card size)

## Troubleshooting

### Database Connection Error

- Check `config.py` database settings
- Ensure MySQL server is running
- Verify database credentials
- Check network connectivity

### Printer Not Found

- Verify printer is installed in Windows
- Check printer name matches exactly in `config.py`
- Ensure printer is powered on and connected
- Try printing a test page from Windows

### Barcode Not Generated

- Check that `exam_barcode` table has data for the selected module
- Verify the `Barcode` column is not empty
- Check application logs in `barcode_printer.log`

### Module Names Not Showing

- Ensure `getmodulename()` MySQL function exists
- Check function has correct permissions
- Verify module data exists in your database

## Logs

Application logs are saved to `barcode_printer.log` in the same directory.

## File Structure

```
printer/
├── main.py                 # Main GUI application
├── config.py              # Configuration settings
├── database.py            # Database operations
├── barcode_generator.py   # Barcode generation
├── printer.py             # Printer interface
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── barcode_printer.log   # Application logs (generated)
```

## Support

For issues or questions, contact:
- zainab.attahiru@cosmopolitan.edu.ng
- hayat.suleiman@cosmopolitan.edu.ng

## License

Internal use only - Cosmopolitan University
