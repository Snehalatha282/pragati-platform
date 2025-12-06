
import requests
import requests
import sys

BASE_URL = 'http://127.0.0.1:5000'
EMAIL = 'mentor_candidate@example.com'
PASSWORD = 'password123'

def verify_mentorship_flow():
    session = requests.Session()
    
    # 1. Register (or Login if exists)
    print(f"Registering/Logging in as {EMAIL}...")
    session.post(f'{BASE_URL}/auth/register', data={
        'email': EMAIL,
        'password': PASSWORD,
        'confirm_password': PASSWORD,
        'first_name': 'Mentor',
        'last_name': 'Candidate'
    })
    
    login_resp = session.post(f'{BASE_URL}/auth/login', data={
        'email': EMAIL,
        'password': PASSWORD
    })
    
    if login_resp.status_code != 200:
        print("Login failed")
        return False

    # 2. Apply to be Mentor
    print("Submitting Mentor Application...")
    apply_resp = session.post(f'{BASE_URL}/mentorship/become-mentor', data={
        'company': 'Tech Corp',
        'job_title': 'Senior Dev',
        'experience_years': '5',
        'skills': 'Python, Leadership',
        'bio': 'I want to help.'
    }, allow_redirects=True)
    
    if apply_resp.status_code == 200:
        # Check for success message in HTML
        if 'Congratulations! You are now a mentor' in apply_resp.text:
            print("PASS: Application submitted successfully.")
            print("PASS: Success message found.")
        else:
            print("FAIL: Success message not found in response.")
            return False
            
        return True
    else:
        print(f"FAIL: Application submission failed with {apply_resp.status_code}")
        return False

if __name__ == '__main__':
    if verify_mentorship_flow():
        print("Mentorship Verification Passed!")
    else:
        print("Mentorship Verification Failed!")
