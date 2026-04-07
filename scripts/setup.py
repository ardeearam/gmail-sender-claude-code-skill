#!/usr/bin/env python3
"""
setup.py -- Saves Gmail credentials (email + App Password) to credentials.json.

Usage:
    python3 setup.py <gmail_email> <app_password>

The App Password must be a 16-character Google App Password (spaces optional).
Generate one at: https://myaccount.google.com/apppasswords
"""

import json
import stat
import sys
from pathlib import Path

CREDS_FILE = Path(__file__).parent.parent / "credentials.json"


def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: setup.py <gmail_email> <app_password>")

    email = sys.argv[1].strip()
    app_password = sys.argv[2].strip().replace(" ", "")

    if not email or not app_password:
        sys.exit("ERROR: Both email and app_password are required.")

    creds = {
        "gmail_email": email,
        "gmail_app_password": app_password,
    }

    CREDS_FILE.write_text(json.dumps(creds, indent=2) + "\n")
    CREDS_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)

    print(f"Credentials saved to: {CREDS_FILE}")
    print("File permissions set to 600 (owner read/write only).")


if __name__ == "__main__":
    main()
