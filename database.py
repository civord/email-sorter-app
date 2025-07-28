import sqlite3
import classifier
import json

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
                   priority TEXT
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
    data = cursor.execute("SELECT id, sender, subject, body, category, priority FROM emails").fetchall() 
    conn.close()

    all_emails = []

    for email_id, sender, subject, body, category, priority in data:
        sender_words = sender.lower().split() if sender else []
        subject_words = subject.lower().split() if subject else []

        # Clean up the body text by removing extra spaces and newlines
        body = body.replace("\n", " ").strip() if body else ""
        body_words = body.lower().split() if body else []
        # Create a dictionary for the email information     
        email_info = {
            "id": email_id,
            "sender": sender_words,
            "subject": subject_words,
            "body": body_words,
            "current_category": category,
            "current_priority": priority
        }
        all_emails.append(email_info)

    return all_emails


def update_email_category_and_priority():
    # Load classification config
    with open("config.json", "r") as file:
        config = json.load(file)

    conn = get_connection()
    cursor = conn.cursor()
    all_emails = get_data_from_table()

    # Pass config to classifier
    classified_emails = classifier.classify_email(all_emails, config)

    for email in classified_emails:
        new_category = email.get("category", None)
        if new_category != email.get("current_category"):
            cursor.execute('''UPDATE emails SET category=? WHERE id=?''', (new_category, email["id"]))
            print(f"Updated category for email ID {email['id']} to {new_category}")
        new_priority = ", ".join(email.get("labels", [])) if "labels" in email else None
        if new_priority:
            if new_priority != email.get("current_priority"):
                cursor.execute('''UPDATE emails SET priority=? WHERE id=?''', (new_priority, email["id"]))  
                print(f"Updated priority for email ID {email['id']} to {new_priority}")      
        else:
            cursor.execute('''UPDATE emails SET priority=NULL WHERE id=?''', (email["id"],))

    conn.commit()
    conn.close()
    print("Classification complete. Updated categories and labels.")

def get_raw_email_table():
    conn = get_connection()
    cursor = conn.cursor()
    raw_emails = cursor.execute("SELECT id, sender, subject, category, priority FROM emails").fetchall()
    return raw_emails