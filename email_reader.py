from email import policy
from email.parser import BytesParser
import imaplib
import database
import socket

database.create_table()

target_email = "fullpcgames3@gmail.com"
app_password = "bklw mlir rdyn xrkn"

# Set timeout to prevent hanging
socket.setdefaulttimeout(30)

try:
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(target_email, app_password)
    mail.select("INBOX")

    # 1. Get last UID
    last_uid = database.get_last_uid() or 0
    print(f"Starting from UID: {last_uid}")

    # 2. Search for emails with UID greater than last_uid
    status, messages = mail.uid("search", None, f"(UID {last_uid + 1}:*)")

    uids = messages[0].split()
    print(f"Found {len(uids)} new emails to process")

    max_uid = last_uid
    processed_count = 0
    error_count = 0
    batch_size = 50  # Save progress every 50 emails

    for i, uid in enumerate(uids):
        try:
            status, data = mail.uid("fetch", uid, "(RFC822)")
            if status != 'OK' or not data[0]:
                print(f"Warning: Failed to fetch UID {uid}")
                error_count += 1
                max_uid = max(max_uid, int(uid))
                continue

            raw_email_data = data[0][1]

            clean_email = BytesParser(policy=policy.default).parsebytes(raw_email_data)

            message_id = clean_email["Message-ID"]
            subject = clean_email["Subject"]
            sender = clean_email["From"]
            email_date = clean_email["Date"]

            body_part = clean_email.get_body(preferencelist=("plain",))
            body = body_part.get_content() if body_part else "(No plain text found)"

            if not database.check_for_duplicates(message_id):
                database.insert_email(message_id, subject, sender, email_date, body)
                processed_count += 1

            max_uid = max(max_uid, int(uid))

        except Exception as e:
            print(f"Error processing UID {uid}: {e}")
            error_count += 1
            max_uid = max(max_uid, int(uid))
            continue

        # 3. Persist progress every batch_size emails to avoid losing all progress if interrupted
        if (i + 1) % batch_size == 0 and max_uid > last_uid:
            database.set_last_uid(max_uid)
            print(f"Batch checkpoint at {i + 1} emails: saved last_uid = {max_uid}")

    # Final save
    if max_uid > last_uid:
        database.set_last_uid(max_uid)
        print(f"Final save: last_uid = {max_uid}")

    print(f"Processing complete: {processed_count} new emails added, {error_count} errors")

    mail.logout()

except imaplib.IMAP4.error as e:
    print(f"IMAP error: {e}")
    print("Check your email credentials (target_email and app_password)")
except Exception as e:
    print(f"Unexpected error: {e}")