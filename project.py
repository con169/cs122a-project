import mysql.connector
import os
import sys
import csv
import logging

#from dotenv import load_dotenv

# Try loading dotenv only if it's available (for local testing)
try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    pass  # No error, just skip loading .env if it's missing

# Configure logging (logging goes to stderr by default)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_connection():
    """
    Establish a MySQL connection with local_infile enabled.
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database='cs122a',
            allow_local_infile=True  # Needed for LOAD DATA LOCAL INFILE
        )
        logging.info("Connected to MySQL DB successfully")
        return conn
    except mysql.connector.Error as e:
        logging.error(f"Error connecting to MySQL DB: {e}")
        return None

def reset_database():
    """
    Deletes all tables and recreates them using schema.sql.
    Returns True if successful; False otherwise.
    """
    conn = get_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    try:
        cursor.execute("USE cs122a;")

        # Drop tables in order (child tables first)
        tables = ["reviews", "sessions", "videos", "series", "movies", "releases", "producers", "viewers", "users"]
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")
            logging.info(f"Dropped table {table}")

        # Read and execute schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        if not os.path.exists(schema_path):
            logging.error(f"Error: schema.sql file not found at {schema_path}!")
            return False

        with open(schema_path, "r") as ddl_file:
            schema_sql = ddl_file.read()
            for statement in schema_sql.split(";"):
                if statement.strip():
                    cursor.execute(statement)
            logging.info("Recreated tables from schema.sql.")

    except mysql.connector.Error as e:
        logging.error(f"Error resetting database: {e}")
        return False
    finally:
        conn.commit()
        cursor.close()
        conn.close()

    return True

def import_csv_with_insert(folder):
    """
    Reads CSV files from the given folder and inserts data using INSERT INTO.
    Returns True if successful; False otherwise.
    """
    conn = get_connection()
    if not conn:
        logging.error("Unable to establish a connection. Aborting import.")
        return False

    cursor = conn.cursor()
    # Import tables in the correct order
    tables = ["users", "producers", "viewers", "releases", "movies", "series", "videos", "sessions", "reviews"]

    for table in tables:
        file_path = os.path.join(folder, f"{table}.csv")
        if not os.path.exists(file_path):
            logging.warning(f"File {file_path} not found. Skipping.")
            continue

        try:
            logging.info(f"Importing {table}.csv into table {table}...")
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                columns = next(reader)  # Read header row
                if not columns:
                    continue
                placeholders = ', '.join(['%s'] * len(columns))
                insert_query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                for row in reader:
                    cursor.execute(insert_query, row)
            conn.commit()
            logging.info(f"Successfully imported {table}.csv")
        except mysql.connector.Error as e:
            logging.error(f"Error importing {table}.csv: {e}")
            return False

    cursor.close()
    conn.close()
    return True

def verify_data():
    """
    Verifies that key tables have at least one row.
    Returns True if users, producers, and releases each have >0 rows; False otherwise.
    """
    conn = get_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM users;")
        users_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM producers;")
        producers_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM releases;")
        releases_count = cursor.fetchone()[0]
        return users_count > 0 and producers_count > 0 and releases_count > 0
    except mysql.connector.Error as e:
        logging.error(f"Error verifying data: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    # Expect: python3 project.py import test_data
    if len(sys.argv) < 2:
        sys.stdout.write("Fail")
        sys.exit(1)

    command = sys.argv[1]

    if command == "import":
        if len(sys.argv) < 3:
            sys.stdout.write("Fail")
            sys.exit(1)
        folder_name = sys.argv[2]
        success = reset_database() and import_csv_with_insert(folder_name) and verify_data()
        if success:
            sys.stdout.write("Success")
            sys.exit(0)
        else:
            sys.stdout.write("Fail")
            sys.exit(1)
