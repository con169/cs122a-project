from db_connector import connect_to_db

def test_connection():
    conn = connect_to_db()
    if conn:
        print("✅ Database connection successful!")
        conn.close()
    else:
        print("❌ Database connection failed!")

if __name__ == "__main__":
    test_connection()
