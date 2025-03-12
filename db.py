# db.py

import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASS')
db_name = os.environ.get('DB_NAME')
db_connection_name = os.environ.get('INSTANCE_CONNECTION_NAME')

def open_connection():
    conn = None
    unix_socket_path = f'/cloudsql/{db_connection_name}' if db_connection_name else None

    if unix_socket_path and os.path.exists(unix_socket_path):
        try:
            conn = pymysql.connect(
                user=db_user,
                password=db_password,
                unix_socket=unix_socket_path,
                db=db_name,
                cursorclass=pymysql.cursors.DictCursor
            )
        except pymysql.MySQLError as e:
            print("Error connecting to Cloud SQL via Unix socket:", e)
    else:
        print("Unix socket not found. Ensure Cloud SQL is correctly configured on Cloud Run.")
        try:
            conn = pymysql.connect(
                host='127.0.0.1',
                user=db_user,
                password=db_password,
                db=db_name,
                cursorclass=pymysql.cursors.DictCursor
            )
        except pymysql.MySQLError as e:
            print("Error connecting to MySQL on 127.0.0.1:", e)
    return conn

def get_messages():
    conn = open_connection()
    if conn is None:
        return {"error": "Unable to connect to the database."}
    
    try:
        with conn.cursor() as cursor:
            result = cursor.execute('SELECT * FROM messages;')
            messages = cursor.fetchall()
            if result > 0:
                return messages
            else:
                return []  # Return an empty list if there are no messages.
    except Exception as e:
        print("Error fetching messages:", e)
        return {"error": "Error fetching messages."}
    finally:
        conn.close()
