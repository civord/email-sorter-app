import database
import classifier
import json

with open("config.json", "r") as file:
        config = json.load(file)

with open("config_priority.json", "r") as file:
        config_priority = json.load(file)

def main():
    emails = database.get_data_from_table()
    classified_emails = []
    for email in emails:
        cat_result = classifier.assign_category(email, config)
        prio_result = classifier.assign_priority(email, config_priority)

        merged = {
            "id": email["id"],
            "category": cat_result.get("category"),
            "category_score": cat_result.get("score"),
            "category_matches": cat_result.get("matches"),
            "priority": prio_result.get("priority"),
            "priority_score": prio_result.get("score"),
            "priority_matches": prio_result.get("matches"),
            "current_category": email.get("current_category"),
            "current_priority": email.get("current_priority")
        }

        classified_emails.append(merged)
    database.update_email_category_and_priority(classified_emails)

if __name__ == "__main__":
    main()