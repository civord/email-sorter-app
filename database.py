import sqlite3

## Creates a connection to the database
def get_connection():
    conn = sqlite3.connect("emails.db")
    return conn

## Create a table inside the database
def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    messageID TEXT UNIQUE,
                    subject TEXT,
                    sender TEXT,
                    date TEXT,
                    body TEXT
                   )''')
    conn.commit()
    conn.close()

## Insert an email into the table
def insert_email(messageID, subject, sender, date, body):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO emails (messageID, subject, sender, date, body) 
                  VALUES (?, ?, ?, ?, ?)''', (messageID, subject, sender, date, body))
    conn.commit()
    conn.close()

def check_for_duplicates(messageID):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM emails WHERE messageID=?", (messageID,))
    result = cursor.fetchone()
    conn.close()
    return result is not None