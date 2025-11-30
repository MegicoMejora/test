import os
import mysql.connector
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv() 

def parse_cleardb_url(url):
    # ClearDB format: mysql://user:pass@host/dbname?reconnect=true
    parsed = urlparse(url)
    user = parsed.username
    password = parsed.password
    host = parsed.hostname
    db = parsed.path.lstrip('/')
    return host, user, password, db

def get_connection():
    # Try ClearDB (HEROKU) first, then DB_URL, then individual vars, then localhost defaults
    db_url = os.environ.get("CLEARDB_DATABASE_URL") or os.environ.get("DB_URL")
    if db_url:
        host, user, password, database = parse_cleardb_url(db_url)
    else:
        host = os.environ.get("DB_HOST", "localhost")
        user = os.environ.get("DB_USER", "root")
        password = os.environ.get("DB_PASS", "")
        database = os.environ.get("DB_NAME", "online_banking")

    # Step 1: Connect without database to create it if missing
    conn = mysql.connector.connect(host=host, user=user, password=password)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    conn.commit()
    cursor.close()
    conn.close()

    # Step 2: Connect to the database
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        autocommit=False
    )
