from database import DatabaseManager

def check_columns():
    db = DatabaseManager()
    # Check exam_timetable_hall columns
    cols = db.execute_query("SHOW COLUMNS FROM exam_timetable_hall")
    print("Columns in exam_timetable_hall:")
    for c in cols:
        print(c['Field'])

if __name__ == "__main__":
    check_columns()
