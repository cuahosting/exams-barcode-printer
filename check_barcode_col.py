from database import DatabaseManager

def check_barcode_cols():
    db = DatabaseManager()
    cols = db.execute_query("SHOW COLUMNS FROM exam_barcode")
    print("Columns in exam_barcode:")
    for c in cols:
        print(c['Field'])

if __name__ == "__main__":
    check_barcode_cols()
