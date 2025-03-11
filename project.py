import mysql.connector
import os
import sys
import logging
#from dotenv import load_dotenv

# Try loading dotenv only if it's available (for local testing)
try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    pass  # No error, just skip loading .env if it's missing

# Configure logging
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
            database=os.getenv('MYSQL_DATABASE'),
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
    """
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()

    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("SET GLOBAL local_infile = 1;")
        logging.info("Disabled foreign key checks.")

        # Drop all tables
        tables = ["movies", "producers", "releases", "reviews", "series", "sessions", "users", "videos", "viewers"]
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")
            logging.info(f"Dropped table {table}")

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        logging.info("Re-enabled foreign key checks.")

        # Read schema.sql and execute the commands
        with open("schema.sql", "r") as ddl_file:
            schema_sql = ddl_file.read()
            for statement in schema_sql.split(";"):
                if statement.strip():
                    cursor.execute(statement)
            logging.info("Recreated tables from schema.sql.")

    except mysql.connector.Error as e:
        logging.error(f"Error resetting database: {e}")

    finally:
        conn.commit()
        cursor.close()
        conn.close()



def import_csv_with_load_data(folder):
    """
    Uses LOAD DATA LOCAL INFILE to quickly import CSV files in the correct order.
    """
    conn = get_connection()
    if not conn:
        logging.error("Unable to establish a connection. Aborting import.")
        return

    cursor = conn.cursor()

    # Import tables in the correct order
    tables = ["users", "producers", "viewers", "releases", "movies", "series", "videos", "sessions", "reviews"]

    for table in tables:
        file_path = os.path.join(folder, f"{table}.csv")
        abs_file_path = os.path.abspath(file_path).replace('\\', '/')

        if not os.path.exists(abs_file_path):
            logging.warning(f"File {file_path} not found. Skipping.")
            continue

        try:
            sql = f"""
            LOAD DATA LOCAL INFILE '{abs_file_path}'
            INTO TABLE {table}
            FIELDS TERMINATED BY ',' 
            LINES TERMINATED BY '\\n'
            IGNORE 1 ROWS;
            """
            logging.info(f"Importing {table}.csv into table {table}...")
            cursor.execute(sql)
            conn.commit()
            logging.info(f"Successfully imported {table}.csv")
        except mysql.connector.Error as e:
            logging.error(f"Error importing {table}.csv: {e}")

    cursor.close()
    conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 project.py <function> [arguments]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "import":
        if len(sys.argv) < 3:
            print("Usage: python3 project.py import <folderName>")
            sys.exit(1)
        folder_name = sys.argv[2]
        reset_database()  # Delete and recreate tables
        import_csv_with_load_data(folder_name)
        print("Success")

    # More commands like insertViewer, addGenre, etc., will go here
