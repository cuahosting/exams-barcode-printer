# Quick Start Guide - Barcode Printer Application

## ✅ Setup Complete!

Your barcode printer application is fully configured and ready to use!

### Configuration Summary

- **Database**: cosmopolitanedu2 (localhost)
- **Printer**: Xprinter XP-365B
- **Semesters Available**: 13
- **Status**: ✅ All systems operational

### How to Run

```bash
cd C:\Users\NEW USER\Project\cosmopolitanedu\printer
python main.py
```

### Quick Workflow

1. **Login** with an authorized email:
   - zainab.attahiru@cosmopolitan.edu.ng
   - hayat.suleiman@cosmopolitan.edu.ng

2. **Select Semester** from the dropdown (e.g., "2026C")

3. **Select Module** from the available modules for that semester

4. **Click "Generate Barcode"** to create the barcode card
   - Shows first student's barcode with StudentID and Seat Number
   - Preview appears in right panel

5. **Click "Print Barcode"** to send to Xprinter XP-365B

### What the Application Does

- Connects to MySQL database `cosmopolitanedu2`
- Fetches semesters from `timetable_semester`
- Loads modules from `exam_timetable_hall` based on semester
- Retrieves student barcodes from `exam_barcode` (joined with exam hall data)
- Generates Code128 barcodes for exam cards
- Prints to XPrinter XP-365B thermal printer

### Database Structure Used

- **timetable_semester**: Semester selection (SemesterName, SemesterCode)
- **exam_timetable_hall**: Module codes per semester (ModuleCode, SemesterCode)
- **exam_barcode**: Student barcode data (Barcode, StudentID, SeatNo, ExamHallID)
- **getmodulename() function**: Returns module name from module code

### Current Behavior

- Generates barcode for **first student** in the module
- Shows Student ID and Seat Number on the card
- Card includes: Module Code, Barcode, Module Name, Semester/Student info

### Files Created

| File | Purpose |
|------|---------|
| `main.py` | GUI application |
| `config.py` | Database & printer settings (configured) |
| `database.py` | MySQL operations |
| `barcode_generator.py` | Barcode & card generation |
| `printer.py` | XPrinter interface |
| `utils.py` | Utilities & logging |
| `test_config.py` | Configuration test script |
| `requirements.txt` | Python dependencies (installed) |

### Testing

Run configuration test:
```bash
python test_config.py
```

Expected output:
- [OK] All modules imported successfully
- [OK] Connected to database: cosmopolitanedu2
- [OK] Found 13 semester(s)
- [OK] Target printer 'Xprinter XP-365B' is available

### Troubleshooting

**No modules found for semester**:
- Semester may not have exam timetable data yet
- Check `exam_timetable_hall` table has records for that SemesterCode

**No barcodes found**:
- Module may not have student barcode data yet
- Check `exam_barcode` table is populated and linked to `exam_timetable_hall`

**Printer not responding**:
- Ensure printer is powered on
- Check USB connection
- Verify printer shows as "Ready" in Windows

### Logs

Application logs are saved to: `barcode_printer.log`

Check logs for detailed error messages and all operations.

### Next Steps

The application currently prints the first student's barcode. If you need to:
- Print all student barcodes sequentially
- Select specific students
- Batch print multiple cards

Let me know and I can add those features!

---

**Ready to use!** Run `python main.py` to start printing barcodes. 🎉
