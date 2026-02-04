#!/bin/bash

# Navigate to the project directory
# Replace /path/to/your/project with the actual path
# cd /path/to/your/project

# Load environment variables if needed
# export SENDGRID_API_KEY='your_api_key'

# Execute the sync script
# Using the absolute path to python and the script is recommended for cron
/usr/bin/python3 NewsletterLaunch/email_bridge.py --provider mock >> NewsletterLaunch/cron_sync.log 2>&1