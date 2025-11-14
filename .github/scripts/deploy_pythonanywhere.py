#!/usr/bin/env python3
"""
PythonAnywhere Deployment Script
Deploys the application using PythonAnywhere's API
"""
import os
import sys
import time
import requests


def get_env_var(name: str) -> str:
    """Get environment variable or exit with error"""
    value = os.environ.get(name)
    if not value:
        print(f"ERROR: Environment variable {name} is not set")
        print("Please configure GitHub secrets:")
        print("  - PYTHONANYWHERE_USERNAME")
        print("  - PYTHONANYWHERE_API_TOKEN")
        print("  - PYTHONANYWHERE_DOMAIN")
        sys.exit(1)
    return value


def main():
    """Main deployment function"""
    # Get credentials from environment
    username = get_env_var('PYTHONANYWHERE_USERNAME')
    token = get_env_var('PYTHONANYWHERE_API_TOKEN')
    domain = get_env_var('PYTHONANYWHERE_DOMAIN')

    api_base = f'https://www.pythonanywhere.com/api/v0/user/{username}'
    headers = {'Authorization': f'Token {token}'}

    print("=" * 60)
    print("DEPLOYING TO PYTHONANYWHERE")
    print("=" * 60)
    print(f"Username: {username}")
    print(f"Domain: {domain}")
    print()

    # Step 1: Check if web app exists
    print("[1/3] Checking web app configuration...")
    response = requests.get(
        f'{api_base}/webapps/{domain}/',
        headers=headers,
        timeout=30
    )

    if response.status_code != 200:
        print(f"ERROR: Cannot access web app at {domain}")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        print()
        print("Please ensure:")
        print("  1. The web app is created on PythonAnywhere")
        print("  2. Your API token has the correct permissions")
        print("  3. The domain name is correct (e.g., username.pythonanywhere.com)")
        sys.exit(1)

    print(f"SUCCESS: Web app found at {domain}")
    print()

    # Step 2: Git pull via SSH (requires setup on PythonAnywhere)
    print("[2/3] Pulling latest code from GitHub...")
    print("NOTE: This assumes git repository is already cloned on PythonAnywhere")
    print("      at ~/comp5313_gr3_projects")
    print()

    # We can't directly execute commands via the new API
    # Instead, we'll just reload the app which will use the code already there
    # The repo should be kept up to date manually or via a webhook
    print("IMPORTANT: Ensure code is pulled on PythonAnywhere")
    print("You can set up automatic git pull using:")
    print("  1. SSH key on PythonAnywhere linked to GitHub")
    print("  2. A scheduled task to pull periodically")
    print("  3. Manual pull before each deployment")
    print()

    # Step 3: Reload web app
    print("[3/3] Reloading web application...")
    response = requests.post(
        f'{api_base}/webapps/{domain}/reload/',
        headers=headers,
        timeout=30
    )

    if response.status_code == 200:
        print("SUCCESS: Web app reloaded successfully")
        print()
        print("=" * 60)
        print("DEPLOYMENT COMPLETE")
        print("=" * 60)
        print(f"Your app is live at: https://{domain}")
        print()
        print("Next steps:")
        print("  1. Visit the health endpoint: https://" + domain + "/health")
        print("  2. Test the chat endpoint")
        print("  3. Monitor logs on PythonAnywhere for any issues")
    else:
        print(f"ERROR: Failed to reload web app")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)


if __name__ == '__main__':
    main()

