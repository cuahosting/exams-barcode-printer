from database import DatabaseManager

def check_venue_cols():
    db = DatabaseManager()
    cols = db.execute_query("SHOW COLUMNS FROM timetable_venue")
    print("Columns in timetable_venue:")
    for c in cols:
        print(c['Field'])

if __name__ == "__main__":
    check_venue_cols()
