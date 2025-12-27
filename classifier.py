import database
import json
import re
from collections import defaultdict

with open("config.json", "r") as file:
        config = json.load(file)

with open("config_priority.json", "r") as file:
        config_priority = json.load(file)

def whole_word_in(text, word):
    return bool(re.search(r'\b' + re.escape(word) + r'\b', text, flags=re.IGNORECASE))

def extract_domain_from_sender(sender_text):
    """Extract domain from email address. Handles formats like 'name <email@domain.com>' and 'email@domain.com'"""
    # Extract email address from angle brackets if present
    match = re.search(r'<(.+?)>', sender_text)
    if match:
        email = match.group(1)
    else:
        email = sender_text
    
    # Extract domain part after @
    domain_match = re.search(r'@(.+)$', email)
    if domain_match:
        return domain_match.group(1).lower()
    return email.lower()

def looks_like_personal(sender):
     return ("gmail.com" in sender or "hotmail.com" in sender or "outlook.com" in sender or "yahoo.com" in sender) \
     and not any(char.isdigit() for char in sender.split("@")[0])

def is_marketing_domain(domain):
    known_news = [
        # Big tech ecosystems
        "facebookmail.com", "instagram.com", "meta.com",
        "tiktok.com", "googlemail.com", "youtube.com",
        "m.youtube.com", "notifications.google.com",

        # Shopping / E-commerce / Deals
        "aliexpress.com", "amazon.", "ebay.", "booking.com",
        "shein.com", "zalando.", "allegro.pl",

        # Entertainment / Streaming / Music / Games
        "spotify.com", "netflix.com", "crunchyroll.com",
        "steamcommunity.com", "steampowered.com",
        "epicgames.com", "riotgames.com",

        # Hardware & manufacturers
        "samsung.com", "apple.com", "huawei.com", "xiaomi.com",

        # SaaS / Tools / Productivity apps
        "notion.so", "slack.com", "discord.com",
        "mailchimp.com", "sendgrid.net", "messaging.microsoft.com",
        "newsletter.", "email.", "mailer.", "promo.", "news.",

        # Travel
        "ryanair.com", "wizzair.com", "lufthansa.com",
        "tripadvisor.com",

        # Food services
        "mcdonalds", "burgerking", "kfc.",
        
        # Clothing brands
        "nike.com", "adidas.com", "hm.com",
        "pullandbear.com", "bershka.com",

        # Apps & mobile services
        "telegram.org", "snapchat.com"
    ]
    domain = domain.lower()
    return any(d in domain for d in known_news)

def is_transactional_email(subject, body):
    patterns = ["order", "receipt", "invoice", "verification", "code", "reset", "login", "security"]
    text = subject + " " + body
    return any(p in text for p in patterns)

def assign_category(email, config):
    # Normalize fields
    sender = (email["sender"] or "").lower()
    subject = (email["subject"] or "").lower()
    body = (email["body"] or "").lower()
    sender_domain = extract_domain_from_sender(sender)
    best = {"category": None, "score": 0.0, "matches": {}}
    threshold_value = config.get("thresholds", {}).get("category_assign", 4.0)

    for category, rules in config.get("categories", {}).items():
        score = 0.0
        matches = defaultdict(list)
        w = rules.get("weights", {})
        sender_w = w.get("sender", 3)
        subject_w = w.get("subject", 2)
        body_w = w.get("body", 1)

        ## Check sender patterns
        for s in rules.get("sender_patterns", []):
             s = s.lower()
             if s.startswith("@"):
                  # Domain matching: check if the domain contains the pattern (e.g., "@samsung.com" matches "m1.email.samsung.com")
                  if s[1:] in sender_domain or sender_domain.endswith(s[1:]):
                       score += sender_w
                       matches["senders"].append(("domain", s))
             else:
                if whole_word_in(sender, s):
                     score += sender_w
                     matches["senders"].append(("sender_keywords", s))

        # Check keywords in subject and body
        for keyword in rules.get("keywords", []):
             if keyword in subject:
                  score += subject_w
                  matches["subjects"].append(keyword)
             if keyword in body:
                  score += body_w
                  matches["body"].append(keyword)
        
        # Check body indicators
        for phrase in rules.get("body_indicators", []):
             if phrase in body:
                  score += body_w
                  matches["body"].append(phrase)

        if score > best["score"]:
             best = {"category": category,
                     "score": score,
                     "matches": dict(matches)}
     # Check for fallbacks
    if best["score"] < threshold_value:
         if looks_like_personal(sender):
              best["category"] = "personal"
              return best
         elif is_marketing_domain(sender_domain):
              best["category"] = "marketing"
              return best
         elif is_transactional_email(subject, body):
              best["category"] = "alerts"
              return best
         elif best["score"] > 0:
              return best
         best["category"] = None
         return best
    return best


def assign_priority(email, config):
     # Normalize fields
     sender = (email["sender"] or "").lower()
     subject = (email["subject"] or "").lower()
     body = (email["body"] or "").lower()
     sender_domain = extract_domain_from_sender(sender)
     best = {"priority": None, "score": 0.0, "matches": []}
     treshold_value = config.get("tresholds", {}).get("priority_assign", 3.0)

     for priorites, rules in config.get("priorities", {}).items():
          score = 0.0
          matches = defaultdict(list)
          w = rules.get("weights", {})
          sender_w = w.get("sender", 3)
          subject_w = w.get("subject", 2)
          body_w = w.get("body", 1)

          for s in rules.get("sender_patterns", []):
               s = s.lower()
               if s.startswith("@"):
                    if s[1:] in sender_domain or sender_domain.endswith(s[1:]):
                         score += sender_w
                         matches["senders"].append(("domain", s))
               else:
                    if whole_word_in(sender, s):
                         score += sender_w
                         matches["senders"].append(("sender_keywords", s))
          
          for keyword in rules.get("subject_keywords", []):
               if keyword in subject:
                    score += subject_w
                    matches["subject"].append(keyword)
               if keyword in body:
                    score += body_w
                    matches["body"].append(keyword)

          for keyword in rules.get("body_indicators", []):
               if keyword in body:
                    score += body_w
                    matches["body"].append(keyword)
               if keyword in subject:
                    score += subject_w
                    matches["body"].append(keyword)
          
          if score > best["score"]:
               best = {"priority": priorites, "score": score, "matches": dict(matches)}

     if best["score"] >= treshold_value:
          return best
     
     return {"priority": "normal", "score": best["score"], "matches": best["matches"]}
            

if __name__ == "__main__":
    all_emails = database.get_data_from_table()
