# create_tables.py
from database import get_connection
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# SQL statements to create tables
sql_statements = [
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
    conn = get_connection()  # database.py now ensures DB exists
    cursor = conn.cursor()
    for s in sql_statements:
        cursor.execute(s)
    conn.commit()
    cursor.close()
    conn.close()
    print("Database and tables created/verified successfully.")

if __name__ == "__main__":
    run()
