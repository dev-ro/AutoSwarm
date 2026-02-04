# Subscriber Synchronization Automation

This document outlines how to automate the daily execution of the `email_bridge.py` script to ensure your subscriber list is synchronized with your email provider.

## Option 1: GitHub Actions (Recommended)

A GitHub Actions workflow has been configured in `.github/workflows/daily_sync.yml`. This is the easiest way to automate the sync if your code is hosted on GitHub.

### Setup:
1.  Go to your GitHub repository **Settings** > **Secrets and variables** > **Actions**.
2.  Add the following **Secrets**:
    *   `SENDGRID_API_KEY`: Your SendGrid API Key (if using SendGrid).
    *   `AWS_ACCESS_KEY_ID` & `AWS_SECRET_ACCESS_KEY`: AWS credentials (if using SES).
    *   `SES_CONTACT_LIST`: The name of your SES contact list.
3.  Add the following **Variables**:
    *   `EMAIL_PROVIDER`: Set to `sendgrid`, `ses`, or `mock`. Default is `mock`.

### Schedule:
The workflow is set to run daily at 00:00 UTC. You can also trigger it manually from the **Actions** tab.

---

## Option 2: Scheduled Cron Job

If you are running the project on a Linux server, you can use a cron job.

### Setup:
1.  Ensure you have the necessary environment variables set in your shell or within the cron job definition.
2.  Make the helper script executable:
    ```bash
    chmod +x NewsletterLaunch/daily_sync.sh
    ```
3.  Open your crontab editor:
    ```bash
    crontab -e
    ```
4.  Add the following line to run the sync daily at midnight:
    ```cron
    0 0 * * * /path/to/NewsletterLaunch/daily_sync.sh
    ```

### Helper Script:
The `NewsletterLaunch/daily_sync.sh` script is provided as a template. Make sure to update the paths and environment variables inside the script to match your server configuration.