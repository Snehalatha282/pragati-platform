
import requests
import sys

BASE_URL = 'http://127.0.0.1:5000'
EMAIL = 'verifier@example.com'
PASSWORD = 'password123'

def test_quiz():
    session = requests.Session()
    
    # Login
    print(f"Logging in as {EMAIL}...")
    login_resp = session.post(f'{BASE_URL}/auth/login', data={
        'email': EMAIL,
        'password': PASSWORD
    })
    
    # Check if login succeeded (either 200 OK or redirect to dashboard which returns 200)
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.status_code}")
        # It might be that the user doesn't exist if verify_backend.py didn't run or persist
        # But we can't easily creating user via external API if there is no register API that takes JSON
        # There is /auth/register but it treats form data.
        # Let's try to register first just in case
        print("Attempting registration...")
        reg_resp = session.post(f'{BASE_URL}/auth/register', data={
            'email': EMAIL,
            'password': PASSWORD,
            'confirm_password': PASSWORD,
            'first_name': 'Verifier',
            'last_name': 'External'
        })
        # After register, we might need to login again
        login_resp = session.post(f'{BASE_URL}/auth/login', data={
            'email': EMAIL,
            'password': PASSWORD
        })
    
    # Generate Quiz
    print("Requesting Quiz...")
    try:
        resp = session.post(f'{BASE_URL}/dashboard/api/generate-quiz', 
                          json={'type': 'technical'})
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                questions = data.get('quiz', {}).get('questions', [])
                print(f"PASS: Received {len(questions)} questions.")
                print(f"Sample: {questions[0]['question']}")
                return True
            else:
                print(f"FAIL: Success false in response: {data}")
                return False
        else:
            print(f"FAIL: API Error {resp.status_code}")
            print(resp.text)
            return False
            
    except Exception as e:
        print(f"FAIL: Exception {e}")
        return False

if __name__ == '__main__':
    if test_quiz():
        sys.exit(0)
    else:
        sys.exit(1)
