#!/usr/bin/env python3
"""
send.py -- Send an email via Gmail using an App Password (stdlib only, no pip required).

Usage:
    python3 send.py <to> <subject> [attachment_path ...]
    (email body is read from stdin)

Examples:
    echo "Hello there!" | python3 send.py recipient@example.com "Greetings"
    printf 'See attached.' | python3 send.py recipient@example.com "Report" /tmp/report.pdf
    printf 'Two files.' | python3 send.py me@gmail.com "Files" ~/doc.pdf ~/photo.png
"""

import json
import mimetypes
import smtplib
import sys
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path

CREDS_FILE = Path(__file__).parent.parent / "credentials.json"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def load_credentials():
    if not CREDS_FILE.exists():
        sys.exit(
            f"ERROR: credentials.json not found at {CREDS_FILE}\n"
            f"Run setup first: python3 {Path(__file__).parent / 'setup.py'} <email> <app_password>"
        )
    with CREDS_FILE.open() as f:
        creds = json.load(f)
    for key in ("gmail_email", "gmail_app_password"):
        if not creds.get(key):
            sys.exit(f"ERROR: Missing '{key}' in credentials.json")
    return creds


def build_message(sender, to, subject, body, attachment_paths):
    if attachment_paths:
        msg = MIMEMultipart()
        msg.attach(MIMEText(body, "plain", "utf-8"))
        for path in attachment_paths:
            p = Path(path).expanduser().resolve()
            if not p.exists():
                sys.exit(f"ERROR: Attachment not found: {p}")
            mime_type, _ = mimetypes.guess_type(str(p))
            if mime_type:
                main_type, sub_type = mime_type.split("/", 1)
            else:
                main_type, sub_type = "application", "octet-stream"
            part = MIMEBase(main_type, sub_type)
            part.set_payload(p.read_bytes())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment", filename=p.name)
            msg.attach(part)
    else:
        msg = MIMEText(body, "plain", "utf-8")

    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    return msg


def send_email(sender, app_password, to, subject, body, attachment_paths):
    msg = build_message(sender, to, subject, body, attachment_paths)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(sender, app_password)
        smtp.sendmail(sender, [to], msg.as_string())


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    to = sys.argv[1].strip()
    subject = sys.argv[2].strip()
    attachment_paths = sys.argv[3:]
    body = sys.stdin.read()

    if not body.strip():
        sys.exit("ERROR: Email body is empty (nothing provided on stdin).")

    creds = load_credentials()
    sender = creds["gmail_email"]
    app_password = creds["gmail_app_password"]

    if attachment_paths:
        print(f"Sending email to {to} with {len(attachment_paths)} attachment(s)...")
    else:
        print(f"Sending email to {to}...")

    try:
        send_email(sender, app_password, to, subject, body, attachment_paths)
        print(f"Email sent successfully from {sender} to {to}.")
    except smtplib.SMTPAuthenticationError:
        sys.exit(
            "ERROR: Authentication failed. Verify your Gmail address and App Password.\n"
            "Make sure 2-Step Verification is enabled and the App Password is valid."
        )
    except smtplib.SMTPException as e:
        sys.exit(f"ERROR: SMTP error -- {e}")


if __name__ == "__main__":
    main()
