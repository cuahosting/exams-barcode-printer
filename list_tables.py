from database import DatabaseManager

def check_tables():
    db = DatabaseManager()
    tables = db.execute_query("SHOW TABLES")
    print("Venue Tables:")
    for t in tables:
        name = list(t.values())[0]
        if 'venue' in name.lower() or 'hall' in name.lower():
            print(name)

if __name__ == "__main__":
    check_tables()
