
from utils.email_demo import send_verification_email
import io
import sys

def test_email_output():
    # Capture stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    # Run function
    send_verification_email("Test User", "Test Corp", "http://test-link")
    
    # Restore stdout
    sys.stdout = sys.__stdout__
    
    output = captured_output.getvalue()
    
    # Verify contents
    expected_sender = "lincolodi095@gamil.com"
    expected_recipient = "ibrahimwani095@gmail.com"
    
    print("Checking Email Output...")
    
    if expected_sender in output:
        print(f"PASS: Sender '{expected_sender}' found.")
    else:
        print(f"FAIL: Sender '{expected_sender}' NOT found.")
        print("Output:", output)
        return False
        
    if expected_recipient in output:
        print(f"PASS: Recipient '{expected_recipient}' found.")
    else:
        print(f"FAIL: Recipient '{expected_recipient}' NOT found.")
        print("Output:", output)
        return False
        
    return True

if __name__ == "__main__":
    if test_email_output():
        print("Email Verification Passed!")
    else:
        print("Email Verification Failed!")
