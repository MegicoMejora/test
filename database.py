# database.py
import os
import mysql.connector
from urllib.parse import urlparse
from dotenv import load_dotenv
import tempfile

load_dotenv()

def parse_cleardb_url(url):
    # parse URL like mysql://user:pass@host:port/dbname?...
    parsed = urlparse(url)
    user = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port or 3306
    db = parsed.path.lstrip('/')
    return host, user, password, db, port

def _write_ca_content_to_file(ca_content):
    """Write inline CA PEM content to a temp file and return the path."""
    if not ca_content:
        return None
    fd, path = tempfile.mkstemp(prefix="db_ca_", suffix=".pem")
    with os.fdopen(fd, "w") as f:
        # support pasted \n sequences as well as real newlines
        f.write(ca_content.replace('\\n', '\n'))
    return path

def get_connection():
    # prefer CLEARDB/DB_URL if set (for compatibility)
    db_url = os.environ.get("CLEARDB_DATABASE_URL") or os.environ.get("DB_URL")
    if db_url:
        host, user, password, database, port = parse_cleardb_url(db_url)
    else:
        host = os.environ.get("DB_HOST", "localhost")
        user = os.environ.get("DB_USER", "root")
        password = os.environ.get("DB_PASS", "")
        database = os.environ.get("DB_NAME", "online_banking")
        port = int(os.environ.get("DB_PORT", 3306))

    # SSL handling: prefer an on-disk path, otherwise inline content
    ssl_ca_path = os.environ.get("DB_SSL_CA_PATH")  # path on filesystem (local dev)
    ssl_ca_content = os.environ.get("DB_SSL_CA_CONTENT")  # full PEM text (use on cloud)
    if not ssl_ca_path and ssl_ca_content:
        ssl_ca_path = _write_ca_content_to_file(ssl_ca_content)

    # Decide whether to attempt CREATE DATABASE:
    # - Only when connecting to localhost (local dev), or when DB_ALLOW_CREATE is "true".
    allow_create = os.environ.get("DB_ALLOW_CREATE", "false").lower() == "true"
    if host in ("localhost", "127.0.0.1") or allow_create:
        try:
            conn = mysql.connector.connect(host=host, user=user, password=password, port=port)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}`")
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            # If CREATE DATABASE fails on a managed DB, we continue and let the later connect raise the real error.
            # Print a helpful message for debugging (you can remove or log this in production).
            print(f"[database.py] warning: could not ensure database exists: {e}")

    # Build connection args
    connect_args = dict(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
        autocommit=False
    )

    if ssl_ca_path:
        connect_args["ssl_ca"] = ssl_ca_path
        # optional: enforce certificate verification
        connect_args["ssl_verify_cert"] = True

    return mysql.connector.connect(**connect_args)

