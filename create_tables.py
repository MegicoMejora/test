# create_tables.py
from dotenv import load_dotenv
load_dotenv()            # ensure environment variables are available

from database import get_connection
import mysql.connector

SQL_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS Users (
        UserID INT AUTO_INCREMENT PRIMARY KEY,
        Name VARCHAR(100) NOT NULL,
        Password VARCHAR(255) NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS Accounts (
        AccountID INT AUTO_INCREMENT PRIMARY KEY,
        UserID INT,
        Balance INT DEFAULT 0,
        FOREIGN KEY (UserID) REFERENCES Users(UserID)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS Transactions (
        TransactionID INT AUTO_INCREMENT PRIMARY KEY,
        AccountID INT,
        Amount INT,
        Type ENUM('Deposit','Withdrawal'),
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID)
    );
    """
]

def run():
    print("[create_tables] connecting to database...")
    try:
        conn = get_connection()
    except mysql.connector.Error as e:
        print(f"[create_tables] ERROR connecting to database: {e}")
        print("  - Check your DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME and SSL settings.")
        print("  - If using a managed DB (Aiven/PlanetScale/etc.), ensure the service is reachable and credentials are correct.")
        return

    try:
        cursor = conn.cursor()
        for sql in SQL_STATEMENTS:
            try:
                cursor.execute(sql)
                print("[create_tables] OK:", sql.splitlines()[0].strip())
            except mysql.connector.Error as ex:
                # show helpful message but continue to next statement
                print(f"[create_tables] WARNING: failed to execute statement: {ex}")
                print("  - If this is a managed DB, DDL may be restricted on the production branch.")
                print("  - You may need to run this on a development branch, or use the provider's console/SQL editor.")
        conn.commit()
        print("[create_tables] All statements executed (where allowed).")
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

if __name__ == "__main__":
    run()

