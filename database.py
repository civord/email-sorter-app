import sqlite3
import classifier
import json
import re
from bs4 import BeautifulSoup


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
                    body TEXT,
                   category TEXT,
                   priority TEXT,
                   category_score REAL,
                   category_matches TEXT,
                   priority_score REAL,
                   priority_matches TEXT,
                   status TEXT DEFAULT "UNREAD"
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

def get_data_from_table():
    conn = get_connection()
    cursor = conn.cursor()
    rows = cursor.execute("SELECT id, sender, subject, body, category, priority FROM emails").fetchall()
    conn.close()

    all_emails = []

    for email_id, sender, subject, body, category, priority in rows:

        # Normalize everything consistently
        sender_clean = (sender or "").strip().lower()
        subject_clean = (subject or "").strip().lower()

        # Better body cleanup
        body_clean = (body or "")
        body_clean = body_clean.replace("\n", " ")
        body_clean = re.sub(r"\s+", " ", body_clean).strip().lower()

        email_info = {
            "id": email_id,
            "sender": sender_clean,
            "subject": subject_clean,
            "body": body_clean,
            "current_category": category,
            "current_priority": priority
        }

        all_emails.append(email_info)

    return all_emails

def update_email_category_and_priority(classified_emails):
    # Load classification config
    with open("config.json", "r") as file:
        config = json.load(file)

    conn = get_connection()
    cursor = conn.cursor()

    for email in classified_emails:
        new_category = email.get("category", None)
        cat_score = email.get("category_score", 0)
        cat_matches = email.get("category_matches", None)
        new_priority = email.get("priority", None)
        prio_score = email.get("priority_score", 0)
        prio_matches = email.get("priority_matches", None)
        if new_category != email.get("current_category"):
            cursor.execute('''UPDATE emails SET category=?, category_score=?, category_matches=?  WHERE id=?''', (new_category, cat_score, json.dumps(cat_matches), email["id"]))
            print(f"Updated category for email ID {email['id']} to {new_category}")
        if new_priority:
            if new_priority != email.get("current_priority"):
                cursor.execute('''UPDATE emails SET priority=?, priority_score=?, priority_matches=? WHERE id=?''', (new_priority, prio_score, json.dumps(prio_matches), email["id"]))  
                print(f"Updated priority for email ID {email['id']} to {new_priority}")      
        else:
            cursor.execute('''UPDATE emails SET priority=NULL WHERE id=?''', (email["id"],))

    conn.commit()
    conn.close()
    print("Classification complete. Updated categories and labels.")

def get_raw_email_table():
    conn = get_connection()
    cursor = conn.cursor()
    raw_emails = cursor.execute("SELECT id, sender, subject, category, priority, status FROM emails").fetchall()
    conn.close()
    return raw_emails

def get_email(email_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
             SELECT sender, subject, body, date
             FROM emails
             WHERE id=?
              """, (email_id,))
    row = cursor.fetchone()
    conn.close()

    return row

def update_email_status(id, email_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE emails SET status=? WHERE id=?", (email_status, id))
    conn.commit()
    conn.close()