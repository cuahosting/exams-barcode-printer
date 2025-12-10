from database import DatabaseManager

def check_date_cols():
    db = DatabaseManager()
    tables = ["exam_timetable", "exam_timetable_detail", "timetable_venue"]
    for t in tables:
        try:
            cols = db.execute_query(f"SHOW COLUMNS FROM {t}")
            print(f"\nColumns in {t}:")
            for c in cols:
                print(f"  {c['Field']} ({c['Type']})")
        except Exception as e:
            print(f"Error checking {t}: {e}")

if __name__ == "__main__":
    check_date_cols()
