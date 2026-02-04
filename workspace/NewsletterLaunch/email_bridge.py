import csv
import os
import sys
import argparse
import logging
import json
import time
import random
from abc import ABC, abstractmethod

# Path Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "subscribers.csv")
STATE_FILE = os.path.join(BASE_DIR, "sync_state.json")
LOG_FILE = os.path.join(BASE_DIR, "email_bridge.log")

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

# Simple Rate Limiter
class RateLimiter:
    def __init__(self, requests_per_minute=600, base_delay=0.01):
        self.requests_per_minute = requests_per_minute
        self.base_delay = base_delay
        self.last_call_time = 0

    def wait(self):
        current_time = time.time()
        elapsed = current_time - self.last_call_time
        min_delay = 60.0 / self.requests_per_minute
        wait_time = max(min_delay, self.base_delay) + random.uniform(0.01, 0.05)
        if elapsed < wait_time:
            sleep_duration = wait_time - elapsed
            time.sleep(sleep_duration)
        self.last_call_time = time.time()

limiter = RateLimiter()

def load_sync_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return set(json.load(f))
        except Exception as e:
            logger.error(f"Error loading sync state: {e}")
    return set()

def save_sync_state(synced_emails):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(list(synced_emails), f)
    except Exception as e:
        logger.error(f"Error saving sync state: {e}")

class EmailProvider(ABC):
    @abstractmethod
    def sync_subscribers(self, subscribers, dry_run=False):
        pass

    @abstractmethod
    def send_newsletter(self, subscribers, subject, content, dry_run=False):
        pass

class SendGridProvider(EmailProvider):
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = None
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            self.client = SendGridAPIClient(self.api_key)
            self.mail_class = Mail
        except ImportError:
            logger.warning("SendGrid library not found. Install it with 'pip install sendgrid'.")

    def sync_subscribers(self, subscribers, dry_run=False):
        if dry_run:
            logger.info(f"[DRY RUN] Would sync {len(subscribers)} subscribers to SendGrid.")
            return True

        if not self.client:
            logger.error("SendGrid client not initialized. Cannot sync.")
            return False
from_email = os.getenv("FROM_EMAIL", "newsletter@theaiauditor.com")
        for s in subscribers:
            message = self.mail_class(
                from_email=from_email,
        data = {
            "contacts": [
                {"email": s['email'], "first_name": s.get('name', '')} for s in subscribers
            ]
        }

        try:
            limiter.wait()
            response = self.client.client.marketing.contacts.put(request_body=data)
            if 200 <= response.status_code < 300:
                logger.info("Successfully synced subscribers to SendGrid.")
                return True
            else:
                logger.error(f"Failed to sync to SendGrid. Status code: {response.status_code}, Body: {response.body}")
                return False
        except Exception as e:
            logger.error(f"Error syncing to SendGrid: {e}")
            return False

    def send_newsletter(self, subscribers, subject, content, dry_run=False):
        if dry_run:
            logger.info(f"[DRY RUN] Would send newsletter to {len(subscribers)} subscribers via SendGrid.")
            return True
        
        if not self.client:
            logger.error("SendGrid client not initialized. Cannot send.")
            return False

        success_count = 0
        for s in subscribers:
            message = self.mail_class(
                from_email='newsletter@theaiauditor.com',
                to_emails=s['email'],
                subject=subject,
                plain_text_content=content
            )
            try:
                limiter.wait()
                response = self.client.send(message)
                if 200 <= response.status_code < 300:
                    success_count += 1
                    logger.info(f"Sent to {s['email']}")
                else:
                    logger.error(f"Failed to send to {s['email']}. Status: {response.status_code}")
            except Exception as e:
                logger.error(f"Error sending to {s['email']}: {e}")
        
        logger.info(f"Newsletter dispatch complete. Success: {success_count}/{len(subscribers)}")
        return success_count > 0

class SESProvider(EmailProvider):
    def __init__(self, region_name):
        self.region_name = region_name
        self.client = None
        try:
            import boto3
            self.client = boto3.client('sesv2', region_name=self.region_name)
        except ImportError:
            logger.warning("Boto3 library not found. Install it with 'pip install boto3'.")

    def sync_subscribers(self, subscribers, dry_run=False):
        if dry_run:
            logger.info(f"[DRY RUN] Would sync {len(subscribers)} subscribers to SES Contact List.")
            return True

        if not self.client:
            logger.error("SES client not initialized. Cannot sync.")
            return False

        success_count = 0
        contact_list_name = os.getenv("SES_CONTACT_LIST", "NewsletterSubscribers")

        for s in subscribers:
            try:
                limiter.wait()
                self.client.create_contact(
                    ContactListName=contact_list_name,
                    EmailAddress=s['email'],
                    AttributesData=json.dumps({"Name": s.get('name', '')})
                )
                success_count += 1
                logger.info(f"Created contact {s['email']}")
            except Exception as e:
                if "AlreadyExistsException" in str(e):
                    try:
                        self.client.update_contact(
                            ContactListName=contact_list_name,
                            EmailAddress=s['email'],
                            AttributesData=json.dumps({"Name": s.get('name', '')})
                        )
                        success_count += 1
                        logger.info(f"Updated contact {s['email']}")
                    except Exception as ue:
                        logger.error(f"Failed to update contact {s['email']}: {ue}")
                else:
                    logger.error(f"Failed to create contact {s['email']}: {e}")
        
        return success_count == len(subscribers)

    def send_newsletter(self, subscribers, subject, content, dry_run=False):
        if dry_run:
            logger.info(f"[DRY RUN] Would send newsletter to {len(subscribers)} subscribers via SES.")
            return True

        if not self.client:
            logger.error("SES client not initialized. Cannot send.")
            return False

        success_count = 0
        for s in subscribers:
            try:
from_email = os.getenv("FROM_EMAIL", "newsletter@theaiauditor.com")
        for s in subscribers:
            try:
                limiter.wait()
                self.client.send_email(
                    FromEmailAddress=from_email,
                        'Simple': {
                            'Subject': {'Data': subject},
                            'Body': {'Text': {'Data': content}}
                        }
                    }
                )
                success_count += 1
                logger.info(f"Sent to {s['email']}")
            except Exception as e:
                logger.error(f"Error sending to {s['email']}: {e}")
        
        return success_count > 0

class MockProvider(EmailProvider):
    def sync_subscribers(self, subscribers, dry_run=False):
        logger.info(f"MOCK: Syncing {len(subscribers)} subscribers...")
        for s in subscribers:
            logger.info(f"MOCK: Synced {s['email']}")
        return True

    def send_newsletter(self, subscribers, subject, content, dry_run=False):
        logger.info(f"MOCK: Starting newsletter dispatch: {subject}")
        delivered = 0
        bounced = 0
        total = len(subscribers)
        
        for i, s in enumerate(subscribers):
            # Simulate real-time progress
            limiter.wait()
            
            # Simulate a 5% bounce rate
            if random.random() < 0.05:
                bounced += 1
                logger.warning(f"[BOUNCE] Failed to deliver to {s['email']} (Reason: Mailbox Full/Invalid)")
            else:
                delivered += 1
                logger.info(f"[DELIVERED] {delivered}/{total} - Sent to {s['email']}")
            
            # Real-time report every 10%
            report_interval = max(1, total // 10)
            if (i + 1) % report_interval == 0 or (i + 1) == total:
                deliverability = (delivered / (i + 1)) * 100
                bounce_rate = (bounced / (i + 1)) * 100
                logger.info(f"--- PROGRESS REPORT: {i+1}/{total} ---")
                logger.info(f"Deliverability: {deliverability:.2f}% | Bounce Rate: {bounce_rate:.2f}%")
        
        logger.info("MOCK: Dispatch complete.")
        logger.info(f"Final Stats: Delivered: {delivered}, Bounced: {bounced}, Total: {total}")
        return True

def get_subscribers():
    subscribers = []
    if not os.path.exists(DB_FILE):
        logger.error(f"Database file {DB_FILE} not found.")
        return subscribers

    try:
        with open(DB_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                subscribers.append(row)
    except Exception as e:
        logger.error(f"Error reading subscribers: {e}")
    return subscribers

def main():
    parser = argparse.ArgumentParser(description="Newsletter Email Bridge & Dispatch")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Sync subscribers to provider")
    sync_parser.add_argument("--provider", choices=["sendgrid", "ses", "mock"], required=True)
    sync_parser.add_argument("--dry-run", action="store_true")
    sync_parser.add_argument("--force", action="store_true")

    # Dispatch command
    dispatch_parser = subparsers.add_parser("dispatch", help="Dispatch newsletter issue")
    dispatch_parser.add_argument("--provider", choices=["sendgrid", "ses", "mock"], required=True)
    dispatch_parser.add_argument("--issue", required=True, help="Path to issue markdown file")
    dispatch_parser.add_argument("--subject", required=True, help="Email subject line")
    dispatch_parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    subscribers = get_subscribers()
    if not subscribers:
        logger.info("No subscribers found in CSV.")
        return

    provider = None
    if args.provider == "sendgrid":
        api_key = os.getenv("SENDGRID_API_KEY")
        if not api_key and not args.dry_run:
            logger.error("SENDGRID_API_KEY environment variable not set.")
            sys.exit(1)
        provider = SendGridProvider(api_key)
    elif args.provider == "ses":
        region = os.getenv("AWS_REGION", "us-east-1")
        provider = SESProvider(region)
    elif args.provider == "mock":
        provider = MockProvider()

    if not provider:
        logger.error("Failed to initialize provider.")
        sys.exit(1)

    if args.command == "sync":
        synced_emails = load_sync_state()
        if args.force:
            to_sync = subscribers
        else:
            to_sync = [s for s in subscribers if s['email'] not in synced_emails]

        if not to_sync:
            logger.info("All subscribers are already synced. Use --force to sync anyway.")
            return

        success = provider.sync_subscribers(to_sync, dry_run=args.dry_run)
        if success and not args.dry_run:
            new_synced = synced_emails.union({s['email'] for s in to_sync})
            save_sync_state(new_synced)
            logger.info("Sync state updated.")

    elif args.command == "dispatch":
        if not os.path.exists(args.issue):
            logger.error(f"Issue file {args.issue} not found.")
            sys.exit(1)
        
        with open(args.issue, 'r') as f:
            content = f.read()
        
        logger.info(f"Starting dispatch of '{args.subject}' to {len(subscribers)} subscribers.")
        provider.send_newsletter(subscribers, args.subject, content, dry_run=args.dry_run)

if __name__ == "__main__":
    main()