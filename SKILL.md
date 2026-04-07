---
name: gmail-sender
description: Send emails via Gmail using App Passwords (SMTP) — no OAuth, no browser dance, no API keys. Use this skill whenever the user asks to send an email, fire off a note, email a summary, send a report, deliver an alert, or notify via Gmail — even if they don't mention Gmail explicitly.
---

You are equipped to send emails via Gmail using an App Password and a local Python helper. No external packages required — stdlib only.

## Setup

**Credentials file:** `~/.claude/skills/gmail-sender/credentials.json`
**Scripts:** `~/.claude/skills/gmail-sender/scripts/`

---

## Step 1 — Check credentials

```bash
python3 -c "from pathlib import Path; print('EXISTS' if Path('~/.claude/skills/gmail-sender/credentials.json').expanduser().exists() else 'MISSING')"
```

### If MISSING — collect credentials via AskUserQuestion

Ask for the Gmail address and App Password in **two separate AskUserQuestion calls** (never ask for both in the same question — the password field needs its own prompt):

**Question 1:** Ask for their Gmail address.

**Question 2:** Ask for their Google App Password using this exact prompt text:
> "Please enter your Google App Password. To generate one: go to myaccount.google.com → Security → 2-Step Verification → App Passwords. Create a new app password (any name). It will be a 16-character code."

Once you have both values, save credentials:

```bash
python3 ~/.claude/skills/gmail-sender/scripts/setup.py "<gmail_email>" "<app_password>"
```

### If EXISTS — read it silently

```bash
python3 -c "import json; c=json.load(open(str(__import__('pathlib').Path('~/.claude/skills/gmail-sender/credentials.json').expanduser()))); print(c['gmail_email'])"
```

Do **not** display or log the App Password.

---

## Step 2 — Collect email details via AskUserQuestion

Ask for all fields. You may ask them together (up to 4 questions per AskUserQuestion call) or separately:

1. **Recipient email address** (`to`)
2. **Subject line** (`subject`)
3. **Body** (`body`) — may be multi-line
4. **Attachments** (`attachments`) — optional, one or more file paths

---

## Step 3 — Send the email

**Without attachments:**
```bash
printf '%s' "<body>" | python3 ~/.claude/skills/gmail-sender/scripts/send.py "<to>" "<subject>"
```

**With one or more attachments** (pass each file path as additional arguments):
```bash
printf '%s' "<body>" | python3 ~/.claude/skills/gmail-sender/scripts/send.py "<to>" "<subject>" "/path/to/file1.pdf" "/path/to/file2.png"
```

Use `printf '%s'` (not `echo`) to preserve multi-line bodies correctly.

---

## Notes

- Uses Gmail SMTP (`smtp.gmail.com:587`) with STARTTLS.
- The sender address is always the Gmail account in `credentials.json`.
- Never print or log the App Password.
- `credentials.json` is excluded from git via `.gitignore`.
- Attachments are auto-detected by MIME type; unknown types fall back to `application/octet-stream`.
- If an attachment path does not exist, the script exits with a clear error before sending.
- If authentication fails, remind the user to verify that 2-Step Verification is enabled on their Google account and that the App Password is correct.
