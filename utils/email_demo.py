
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_verification_email(mentor_name, company_name, verification_link):
    """
    Simulates sending a verification email.
    """
    
    # Configuration as per request
    # Configuration
    sender_email = os.environ.get('MAIL_USERNAME')
    # In a real scenario, this would be the company_email passed in arguments.
    # For this demo/testing, we force it to the requested email.
    target_email = "ibrahimwani095@gmail.com"

    if not sender_email:
        print("ERROR: MAIL_USERNAME environment variable not set")
        return False
    
    subject = f"Verify Employment for {mentor_name}"
    
    body = f"""
    From: {sender_email}
    To: {target_email}
    Subject: {subject}
    
    <h2>Employment Verification Request</h2>
    <p>Hello,</p>
    <p>A user named <strong>{mentor_name}</strong> has applied to be a mentor on Pragati Platform, claiming to work at <strong>{company_name}</strong>.</p>
    <p>Please verify their employment by clicking the button below:</p>
    <a href="{verification_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Employment</a>
    <p>Or click this link: {verification_link}</p>
    """
    
    print("-" * 50)
    print(f"--- MOCK EMAIL SENT ---")
    print(f"FROM: {sender_email}")
    print(f"TO:   {target_email}")
    print(f"Link: {verification_link}")
    print("-" * 50)
    
    # REAL SMTP IMPLEMENTATION
    mail_password = os.environ.get('MAIL_PASSWORD', '').replace(' ', '')
    
    if not mail_password:
        print("WARNING: MAIL_PASSWORD not set. Email logged only (not sent).")
        return True

    try:
        print(f"DEBUG: Attempting SMTP connection to smtp.gmail.com:587 as {sender_email}...")
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = target_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print(f"DEBUG: Attempting login with password length {len(mail_password)}...")
        server.login(sender_email, mail_password)
        print("DEBUG: Login successful.")
        
        server.send_message(msg)
        server.quit()
        print(f"SUCCESS: Email sent to {target_email} via SMTP.")
    except smtplib.SMTPAuthenticationError:
        print("ERROR: Authentication Failed. Please check:")
        print("1. Is 2-Step Verification ON?")
        print("2. Are you using an App Password (not login password)?")
        return False
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

    return True
