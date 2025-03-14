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
#logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_connection():
    """
    Establish a MySQL connection with local_infile enabled.
    """
    try:
        conn = mysql.connector.connect(user='test', password='password', database='cs122a',
            allow_local_infile=True  # Needed for LOAD DATA LOCAL INFILE
        )
        #logging.info("Connected to MySQL DB successfully")
        return conn
    except mysql.connector.Error as e:
        #logging.error(f"Error connecting to MySQL DB: {e}")
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
            #logging.info(f"Dropped table {table}")

        # Read and execute schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        if not os.path.exists(schema_path):
            #logging.error(f"Error: schema.sql file not found at {schema_path}!")
            return False

        with open(schema_path, "r") as ddl_file:
            schema_sql = ddl_file.read()
            for statement in schema_sql.split(";"):
                if statement.strip():
                    cursor.execute(statement)
            #logging.info("Recreated tables from schema.sql.")

    except mysql.connector.Error as e:
        #logging.error(f"Error resetting database: {e}")
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
        #logging.error("Unable to establish a connection. Aborting import.")
        return False

    cursor = conn.cursor()
    # Import tables in the correct order
    tables = ["users", "producers", "viewers", "releases", "movies", "series", "videos", "sessions", "reviews"]

    for table in tables:
        file_path = os.path.join(folder, f"{table}.csv")
        if not os.path.exists(file_path):
            #logging.warning(f"File {file_path} not found. Skipping.")
            continue

        try:
            #logging.info(f"Importing {table}.csv into table {table}...")
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
            #logging.info(f"Successfully imported {table}.csv")
        except mysql.connector.Error as e:
            #logging.error(f"Error importing {table}.csv: {e}")
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
        #logging.error(f"Error verifying data: {e}")
         print("False")
    finally:
        cursor.close()
        conn.close()

def insertViewer(data):
    # Order:
    # [uid, email, nickname, street, city, state, zip, genres, joined_date, first, last, subscription]

    conn = get_connection()
    cursor = conn.cursor()
    uid, email, nickname, street, city, state, zip_code, genres, joined_date, first, last, subscription = data
    try:
        # Check if uid already exists
        cursor.execute(f"SELECT COUNT(*) FROM users WHERE uid ='{uid}'")
        if cursor.fetchone()[0] > 0:
            print("Fail")
            return


        # First need to insert into User table, then we will insert into viewer table.

        user_sql_code = (
            f"INSERT INTO users (uid, email, joined_date, nickname, street, city, state, zip, genres) "
            f"VALUES ({uid}, '{email}', '{joined_date}', '{nickname}', '{street}', '{city}', '{state}', '{zip_code}', '{genres}');"
        )
        cursor.execute(user_sql_code)


        # now to insert into viewer the extra information
        viewer_sql_code = (
            f"INSERT INTO viewers (uid, first_name, last_name, subscription) "
            f"VALUES ({uid}, '{first}', '{last}', '{subscription}');"
        )
        cursor.execute(viewer_sql_code)

        conn.commit()
        print("Success")

    except Exception as e:
        print("Fail", e)
    finally:
        cursor.close()
        conn.close()


def addGenre(data):
    uid, genre = data

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Get the current genres for the user
        cursor.execute("SELECT genres FROM users WHERE uid = %s;", (uid,))
        result = cursor.fetchone()
        if not result:
            print("Fail")
            return

        current_genres = result[0]
        if not current_genres or current_genres.strip() == "":
            new_genres = genre  # Use the original formatting
        else:
            # Create a lowercase list for comparison
            genres_list_lower = [g.strip().lower() for g in current_genres.split(';')]
            if genre.lower() in genres_list_lower:
                new_genres = current_genres  # No change if genre already exists
            else:
                new_genres = current_genres + ';' + genre  # Append original input

        cursor.execute("UPDATE users SET genres = %s WHERE uid = %s;", (new_genres, uid))
        conn.commit()
        # Print the updated genres string instead of "Success"
        #sys.stdout.write("Success")
        #sys.exit(0)
        
    except Exception as e:
        print("Fail", e)
    finally:
        cursor.close()
        conn.close()
        return True


def insertMovie(data):
    conn = get_connection()
    cursor = conn.cursor()
    rid,website_url = data

    try:
        sql_code = (
            f"INSERT INTO movies (rid, website_url) "
            f"VALUES ('{rid}','{website_url}');"
        )
        cursor.execute(sql_code)
        conn.commit()
        print("Success")

    except Exception as e:
        print("Fail", e)
    finally:
        cursor.close()
        conn.close()

def deleteViewer(data):
    conn = get_connection()
    cursor = conn.cursor()
    uid = data

    try:
        sql_code = (
            f"DELETE FROM viewers "
            f"WHERE uid = '{uid}';"
        )
        cursor.execute(sql_code)
        conn.commit()
        print("Success")

    except Exception as e:
        print("Fail", e)
    finally:
        cursor.close()
        conn.close()

def insertSession(data):
    sid, uid, rid, ep_num, initiate_at, leave_at, quality, device = data

    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql_code = (
            f"INSERT INTO sessions (sid, uid, rid, ep_num, initiate_at, leave_at, quality, device) "
            f"VALUES ({sid}, {uid}, {rid}, {ep_num}, '{initiate_at}', '{leave_at}', '{quality}', '{device}');"
        )
        cursor.execute(sql_code)
        conn.commit()
        print("Success")
    except Exception as e:
        print("Fail", e)
    finally:
        cursor.close()
        conn.close()

def updateRelease(data):
    conn = get_connection()
    cursor = conn.cursor()

    rid, title = data
    try:
        sql_code = f"UPDATE releases SET title = '{title}' WHERE rid = {rid};"
        cursor.execute(sql_code)
        conn.commit()
        print("Success")
    except Exception as e:
        print("Fail", e)
    finally:
        cursor.close()
        conn.close()

def listReleases(data):
    conn = get_connection()
    cursor = conn.cursor()
    uid = data

    try:
        sql_code = (
            f"SELECT DISTINCT r.rid, r.genre, r.title "
            f"FROM releases r "
            f"JOIN reviews rev ON r.rid = rev.rid "
            f"WHERE rev.uid = {uid} "
            f"ORDER BY r.title ASC;"
        )
        cursor.execute(sql_code)
        rows = cursor.fetchall()

        for row in rows:
            print(",".join(str(x) for x in row))
    except Exception as e:
        print("Fail", e)
    finally:
        cursor.close()
        conn.close()

def popularRelease(data):
    conn = get_connection()
    cursor = conn.cursor()

    num = int(data[0])
    try:
        sql_code = (
            f"SELECT R.rid, R.title, COUNT(Rev.rvid) as reviewCount "
            f"FROM releases R "
            f"LEFT JOIN reviews Rev ON R.rid = Rev.rid "
            f"GROUP BY R.rid, R.title "
            f"ORDER by reviewCount DESC, R.rid DESC "
            f"LIMIT {num}; "
        )
        cursor.execute(sql_code)
        rows = cursor.fetchall()
        for row in rows:
            print(",".join(str(x) for x in row))
    except Exception as e:
        print("Fail", e)
    finally:
        cursor.close()
        conn.close()

def releaseTitle(sid):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql_code = (
            "SELECT r.rid, r.title AS release_title, r.genre, v.title AS video_title, v.ep_num, v.length "
            "FROM releases r "
            "JOIN videos v ON r.rid = v.rid "
            "JOIN sessions s ON v.rid = s.rid AND v.ep_num = s.ep_num "
            "WHERE s.sid = %s "
            "ORDER BY r.title ASC;"
        )
        cursor.execute(sql_code, (sid,))
        rows = cursor.fetchall()
        for row in rows:
            print(",".join(str(x) for x in row))
    except Exception as e:
        print("Fail", e)
    finally:
        cursor.close()
        conn.close()


def activeViewer(N, start, end):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql_code = (
            "SELECT v.uid, v.first_name, v.last_name "
            "FROM viewers v "
            "JOIN sessions s ON v.uid = s.uid "
            "WHERE s.initiate_at BETWEEN %s AND %s "
            "GROUP BY v.uid "
            "HAVING COUNT(s.sid) >= %s "
            "ORDER BY v.uid ASC;"
        )
        cursor.execute(sql_code, (start, end, N))
        rows = cursor.fetchall()
        for row in rows:
            print(",".join(str(x) for x in row))
    except Exception as e:
        print("Fail", e)
    finally:
        cursor.close()
        conn.close()

def videosViewed(rid):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql_code = (
            "SELECT v.rid, v.ep_num, v.title, v.length, "
            "(SELECT COUNT(DISTINCT s.uid) FROM sessions s WHERE s.rid = v.rid) AS viewers "
            "FROM videos v "
            "WHERE v.rid = %s "
            "ORDER BY v.rid DESC, v.ep_num ASC; "
        )
        cursor.execute(sql_code, (rid,))
        rows = cursor.fetchall()

        for row in rows:
            print(",".join(str(x) for x in row))

    except Exception as e:
        print("Fail", e)
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

    if command == "insertViewer":
        insertViewer(sys.argv[2:])

    elif command == "addGenre":
        addGenre(sys.argv[2:])

    elif command == "deleteViewer":
        deleteViewer(sys.argv[2])

    elif command == "insertMovie":
        insertMovie(sys.argv[2:])

    elif command == "insertSession":
        insertSession(sys.argv[2:])

    elif command == "updateRelease":
        updateRelease(sys.argv[2:])

    elif command == "listReleases":
         listReleases(sys.argv[2])

    elif command == "popularRelease":
        popularRelease(sys.argv[2:])

    elif command == "releaseTitle":
        releaseTitle(sys.argv[2])

    elif command == "activeViewer":
        activeViewer(sys.argv[2], sys.argv[3], sys.argv[4])

    elif command == "videosViewed":
        videosViewed(sys.argv[2])