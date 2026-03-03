import csv
import random
from datetime import datetime, timedelta

leads = [
    {"count": 65, "source": "linkedin", "medium": "social", "content": "cto_authority_play"},
    {"count": 35, "source": "x", "medium": "social", "content": "comparison_thread_auditor"},
    {"count": 42, "source": "x", "medium": "social", "content": "dev_builder_play"},
    {"count": 18, "source": "x", "medium": "social", "content": "comparison_thread_architect"},
]

def generate_leads():
    all_leads = []
    start_date = datetime(2026, 2, 3)
    for group in leads:
        for i in range(group["count"]):
            email = f"lead_{group['source']}_{group['content']}_{i}@example.com"
            name = f"User {i}"
            signup_date = (start_date + timedelta(days=random.randint(0, 2), hours=random.randint(0, 23))).strftime("%Y-%m-%d %H:%M:%S")
            all_leads.append({
                "email": email,
                "name": name,
                "signup_date": signup_date,
                "utm_source": group["source"],
                "utm_medium": group["medium"],
                "utm_content": group["content"]
            })
    return all_leads

def populate_csv(filename):
    fieldnames = ["email", "name", "signup_date", "utm_source", "utm_medium", "utm_content"]
    existing_leads = []
    try:
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing_leads.append(row)
    except FileNotFoundError:
        pass

    new_leads = generate_leads()
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_leads)
        writer.writerows(new_leads)

if __name__ == "__main__":
    populate_csv("NewsletterLaunch/subscribers.csv")
    print("Populated subscribers.csv with 160 leads.")