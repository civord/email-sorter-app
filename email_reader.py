from email import policy
from email.parser import BytesParser
import imaplib, email
import database

database.create_table()

target_email = "fullpcgames3@gmail.com"
app_password = "bklw mlir rdyn xrkn"

# Connect to Gmail's IMAP service
mail = imaplib.IMAP4_SSL(host="imap.gmail.com")

# Login
mail.login(target_email, app_password)

# Select the working inbox
mail.select(mailbox="INBOX")

# Search for unread emails
status, messages = mail.search(None, "(UNSEEN SINCE 10-May-2025)")

email_ids = [eid for eid in messages[0].decode().split(" ") if eid]

# Fetch the emails
for email_id in email_ids:
    status, data = mail.fetch(email_id, "(RFC822)")
    # Get the raw email
    raw_email_data = data[0][1]
    # Convert it
    clean_email = BytesParser(policy=policy.default).parsebytes(raw_email_data)
    # Store the content that we need
    messageID = clean_email["Message-ID"]
    subject = clean_email["Subject"]
    sender = clean_email["From"]
    email_date = clean_email["Date"]
    body_part = clean_email.get_body(preferencelist=('plain',))
    if body_part:
        body = body_part.get_content()
    else:
        body = "(No plain text found)"

    if not database.check_for_duplicates(messageID):
        database.insert_email(messageID, subject, sender, email_date, body)
    # Print email info
    print("="*50)
    print(f"From: {sender}")
    print(f"Subject: {subject}")
    print("Body:")
    print(body)
    print("="*50)


mail.logout()
