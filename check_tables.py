from database import DatabaseManager

def list_tables():
    db = DatabaseManager()
    tables = db.execute_query("SHOW TABLES")
    print("Tables found:", tables)

if __name__ == "__main__":
    list_tables()
