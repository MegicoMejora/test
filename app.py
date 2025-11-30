from flask import Flask, render_template, request, redirect, session
from database import get_connection
from models.account import Account
from models.transaction import DepositTransaction, WithdrawalTransaction
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv() 

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

@app.route('/')
def home():
    return redirect('/login')  # redirect users to the login page


# --- Registration Route ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (Name, Password) VALUES (%s, %s)", (name, password))
        conn.commit()
        user_id = cursor.lastrowid

        cursor.execute("INSERT INTO Accounts (UserID, Balance) VALUES (%s, %s)", (user_id, 0.0))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect('/login')
    return render_template('register.html')


# --- Login Route ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password'].encode('utf-8')

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE Name = %s", (name,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password, user['Password'].encode('utf-8')):
            session['user_id'] = user['UserID']
            session['name'] = user['Name']
            return redirect('/dashboard')
        else:
            return "Invalid login credentials."
    return render_template('login.html')


# --- Dashboard Route ---
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Accounts WHERE UserID = %s", (session['user_id'],))
    account = cursor.fetchone()

    return render_template('dashboard.html', name=session['name'], balance=account['Balance'])


# --- Deposit Route ---
@app.route('/deposit', methods=['POST'])
def deposit():
    amount = float(request.form['amount'])
    user_id = session['user_id']

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT AccountID, Balance FROM Accounts WHERE UserID = %s", (user_id,))
    account_id, balance = cursor.fetchone()

    acc = Account(account_id, user_id, balance)
    deposit_txn = DepositTransaction(account_id, amount)
    deposit_txn.execute(acc)

    cursor.execute("UPDATE Accounts SET Balance = %s WHERE AccountID = %s", (acc.get_balance(), account_id))
    cursor.execute("INSERT INTO Transactions (AccountID, Amount, Type) VALUES (%s, %s, 'Deposit')", (account_id, amount))
    conn.commit()
    conn.close()
    return redirect('/dashboard')


# --- Withdraw Route ---
@app.route('/withdraw', methods=['POST'])
def withdraw():
    amount = float(request.form['amount'])
    user_id = session['user_id']

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT AccountID, Balance FROM Accounts WHERE UserID = %s", (user_id,))
    account_id, balance = cursor.fetchone()

    acc = Account(account_id, user_id, balance)
    withdraw_txn = WithdrawalTransaction(account_id, amount)
    result = withdraw_txn.execute(acc)

    if result == "Withdrawal successful.":
        cursor.execute("UPDATE Accounts SET Balance = %s WHERE AccountID = %s", (acc.get_balance(), account_id))
        cursor.execute("INSERT INTO Transactions (AccountID, Amount, Type) VALUES (%s, %s, 'Withdrawal')", (account_id, amount))
        conn.commit()

    conn.close()
    return redirect('/dashboard')


# --- Transaction History ---
@app.route('/transactions')
def transactions():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT T.Type, T.Amount, T.Timestamp
        FROM Transactions T
        JOIN Accounts A ON T.AccountID = A.AccountID
        WHERE A.UserID = %s
        ORDER BY T.Timestamp DESC
    """, (session['user_id'],))
    transactions = cursor.fetchall()
    return render_template('transactions.html', transactions=transactions)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # bind to 0.0.0.0 so Heroku can route requests
    app.run(debug=True, host='0.0.0.0', port=port)
