import os
import subprocess
import sys

def run_deploy():
    config_path = "NewsletterLaunch/issue_02_deployment.env"
    bridge_script = "NewsletterLaunch/email_bridge.py"
    
    # Load environment variables from .env file
    env_vars = os.environ.copy()
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    else:
        print(f"Error: Config file {config_path} not found.")
        return

    provider = env_vars.get("EMAIL_PROVIDER", "mock")
    issue_file = env_vars.get("ISSUE_FILE")
    subject = env_vars.get("ISSUE_SUBJECT")
    
    is_production = "--production" in sys.argv
    dry_run = [] if is_production else ["--dry-run"]
    
    if is_production:
        print("!!! PRODUCTION DISPATCH MODE ENABLED !!!")
    else:
        print("Running in DRY RUN mode. Use --production for real dispatch.")

    # Step 1: Sync
    print(f"Step 1: Synchronizing latest subscribers to {provider}...")
    sync_cmd = [sys.executable, bridge_script, "sync", "--provider", provider] + dry_run
    subprocess.run(sync_cmd, env=env_vars, check=True)

    # Step 2: Dispatch
    print(f"Step 2: Dispatching Issue #2...")
    dispatch_cmd = [
        sys.executable, bridge_script, "dispatch",
        "--provider", provider,
        "--issue", issue_file,
        "--subject", subject
    ] + dry_run
    subprocess.run(dispatch_cmd, env=env_vars, check=True)
    
    print("Issue #2 deployment process complete.")

if __name__ == "__main__":
    run_deploy()