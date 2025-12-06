
import smtplib
import os
import sys

# Read variables
sender = "whitedevil752006@gmail.com"
password = os.environ.get('MAIL_PASSWORD')

print(f"--- Email Debugger ---")
print(f"Sender: {sender}")

if not password:
    print("ERROR: MAIL_PASSWORD environment variable is NOT set.")
    print("Usage: $env:MAIL_PASSWORD='your-app-password'; python debug_email.py")
    sys.exit(1)

print(f"Password Check: Length is {len(password)} characters.")
if len(password) < 16:
    print("WARNING: Password looks too short to be an App Password (usually 16 chars).")

print("\nAttempting to connect to Gmail SMTP...")

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    print("\n✅ SUCCESS! Authentication working.")
    print("The credentials are correct. You can now run the main app.")
    server.quit()
except smtplib.SMTPAuthenticationError:
    print("\n❌ FAILED: Authentication Refused.")
    print("-" * 40)
    print("POSSIBLE CAUSES:")
    print("1. You used your Login Password -> You MUST use an 'App Password'.")
    print("   Go to: https://myaccount.google.com/apppasswords")
    print("2. 2-Step Verification is OFF -> It must be ON to use App Passwords.")
    print("-" * 40)
except Exception as e:
    print(f"\n❌ FAILED: Connection Error: {e}")
