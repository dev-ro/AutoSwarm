import csv
import os
import sys
import argparse
import re
import logging
import fcntl
from datetime import datetime
from contextlib import contextmanager

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "subscribers.csv")
LOG_FILE = os.path.join(BASE_DIR, "subscriber_manager.log")

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

HEADERS = ["email", "name", "signup_date", "utm_source", "utm_medium", "utm_content"]

@contextmanager
def locked_file(filename, mode):
    """Context manager for file locking."""
    file = open(filename, mode, newline='')
    try:
        # Request an exclusive lock (blocking)
        if 'r' not in mode or '+' in mode:
            fcntl.flock(file.fileno(), fcntl.LOCK_EX)
        else:
            fcntl.flock(file.fileno(), fcntl.LOCK_SH)
        yield file
    finally:
        # Release the lock and close the file
        fcntl.flock(file.fileno(), fcntl.LOCK_UN)
        file.close()

def validate_email(email):
    """Basic email validation using regex."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(email_regex, email):
        return True
    return False

def initialize_db():
    if not os.path.exists(DB_FILE):
        try:
            os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
            with locked_file(DB_FILE, 'w') as file:
                writer = csv.writer(file)
                writer.writerow(HEADERS)
            logger.info(f"Initialized database at {DB_FILE}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            sys.exit(1)
    else:
        # Check if we need to update headers
        try:
            with locked_file(DB_FILE, 'r+') as file:
                reader = csv.reader(file)
                existing_headers = next(reader, None)
                if existing_headers != HEADERS:
                    logger.info("Updating database headers...")
                    rows = list(reader)
                    file.seek(0)
                    file.truncate()
                    writer = csv.writer(file)
                    writer.writerow(HEADERS)
                    for row in rows:
                        # Map old rows to new headers
                        # Old might have fewer columns
                        new_row = row + [""] * (len(HEADERS) - len(row))
                        writer.writerow(new_row)
        except Exception as e:
            logger.error(f"Error updating database headers: {e}")

def get_all_subscribers():
    subscribers = []
    if os.path.exists(DB_FILE):
        try:
            with locked_file(DB_FILE, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    subscribers.append(row)
        except Exception as e:
            logger.error(f"Error reading subscribers: {e}")
    return subscribers

def add_subscriber(email, name, utm_source="", utm_medium="", utm_content=""):
    initialize_db()
    
    if not validate_email(email):
        logger.error(f"Invalid email format: {email}")
        return False

    if not name.strip():
        logger.error("Name cannot be empty.")
        return False

    try:
        # Check if subscriber already exists
        with locked_file(DB_FILE, 'r+') as file:
            reader = list(csv.DictReader(file))
            if any(sub['email'] == email for sub in reader):
                logger.warning(f"Subscriber with email {email} already exists.")
                return False

            signup_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.seek(0, os.SEEK_END)
            writer = csv.writer(file)
            writer.writerow([email, name, signup_date, utm_source, utm_medium, utm_content])
            logger.info(f"Added subscriber: {name} ({email}) [source: {utm_source}]")
            return True
    except Exception as e:
        logger.error(f"Error adding subscriber: {e}")
        return False

def remove_subscriber(email):
    initialize_db()
    
    if not validate_email(email):
        logger.error(f"Invalid email format: {email}")
        return False

    try:
        with locked_file(DB_FILE, 'r+') as file:
            reader = list(csv.DictReader(file))
            initial_count = len(reader)
            updated_subscribers = [sub for sub in reader if sub['email'] != email]
            
            if len(updated_subscribers) == initial_count:
                logger.warning(f"Subscriber with email {email} not found.")
                return False

            # Overwrite the file with updated list
            file.seek(0)
            file.truncate()
            writer = csv.writer(file)
            writer.writerow(HEADERS)
            for sub in updated_subscribers:
                writer.writerow([sub.get(h, "") for h in HEADERS])
            
            logger.info(f"Removed subscriber: {email}")
            return True
    except Exception as e:
        logger.error(f"Error removing subscriber: {e}")
        return False

def list_subscribers():
    initialize_db()
    subscribers = get_all_subscribers()
    if not subscribers:
        logger.info("No subscribers found.")
        return

    print(f"\n{'Email':<30} | {'Name':<15} | {'Date':<20} | {'Source':<10} | {'Medium':<10} | {'Content'}")
    print("-" * 110)
    for sub in subscribers:
        print(f"{sub['email']:<30} | {sub['name']:<15} | {sub['signup_date']:<20} | {sub.get('utm_source', ''):<10} | {sub.get('utm_medium', ''):<10} | {sub.get('utm_content', '')}")
    print()

def main():
    parser = argparse.ArgumentParser(description="Subscriber Management System")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new subscriber")
    add_parser.add_argument("email", help="Email of the subscriber")
    add_parser.add_argument("name", help="Name of the subscriber")
    add_parser.add_argument("--source", dest="utm_source", default="", help="UTM source")
    add_parser.add_argument("--medium", dest="utm_medium", default="", help="UTM medium")
    add_parser.add_argument("--content", dest="utm_content", default="", help="UTM content")

    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a subscriber")
    remove_parser.add_argument("email", help="Email of the subscriber to remove")

    # List command
    subparsers.add_parser("list", help="List all subscribers")

    args = parser.parse_args()

    if args.command == "add":
        add_subscriber(args.email, args.name, args.utm_source, args.utm_medium, args.utm_content)
    elif args.command == "remove":
        remove_subscriber(args.email)
    elif args.command == "list":
        list_subscribers()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()