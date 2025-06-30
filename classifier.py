import database
import json

with open("config.json", "r") as file:
        config = json.load(file)

def classify_email(all_emails, config):
    """
    Classifies emails into categories and assigns labels based on configuration rules.

    Args:
        all_emails (list): A list of email dictionaries to be classified.
        config (dict): Dictionary of classification rules and labels.

    Returns:
        list: The list of emails with updated 'category' and 'labels' fields.
    """
    for email in all_emails:
        # Normalize fields
        sender = " ".join(email["sender"]) if isinstance(email["sender"], list) else email["sender"]
        subject = " ".join(email["subject"]) if isinstance(email["subject"], list) else email["subject"]
        body = " ".join(email["body"]) if isinstance(email["body"], list) else email["body"]

        # Classify the email
        for category, rules in config["categories"].items():
            if any(keyword in sender for keyword in rules["senders"]):
                email["category"] = category
                break
            elif any(keyword in subject for keyword in rules["subject_keywords"]):
                email["category"] = category
                break
            elif any(keyword in body for keyword in rules["body_keywords"]):
                email["category"] = category
                break

        # Assign labels
        combined_text = f"{subject} {body}"
        for label, keywords in config["labels"].items():
            if any(keyword in combined_text for keyword in keywords):
                email.setdefault("labels", [])
                if label not in email["labels"]:
                    email["labels"].append(label)

        print(f"Classifying email ID {email['id']}")
        print("Subject:", email["subject"])
        print("Body:", email["body"])
        print("Matched Category:", email.get("category"))
        print("Matched Labels:", email.get("labels", []))
    return all_emails


if __name__ == "__main__":
    all_emails = database.get_data_from_table()
    classified_emails = classify_email(all_emails, config)
