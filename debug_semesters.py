from database import DatabaseManager

def debug_semesters():
    print("Initializing DB...")
    try:
        db = DatabaseManager()
        print("Connected. Fetching semesters...")
        semesters = db.get_semesters()
        print(f"Semesters found: {len(semesters)}")
        for s in semesters:
            print(s)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    debug_semesters()
