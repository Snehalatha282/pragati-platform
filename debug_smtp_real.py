
import smtplib
import os

sender = "whitedevil752006@gmail.com"
password = "orgz aqdp txay zcdo".replace(" ", "")

print(f"Testing SMTP for {sender}...")
print(f"Password used: {password}")

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.set_debuglevel(1)
    server.starttls()
    server.login(sender, password)
    print("\nSUCCESS: Login worked!")
    server.quit()
except Exception as e:
    print(f"\nFAILURE: {e}")
