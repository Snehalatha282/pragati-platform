
import requests
import sqlite3
import time

BASE_URL = 'http://127.0.0.1:5000'
EMAIL = 'gated_mentor@example.com'
PASSWORD = 'password123'
FIRST_NAME = 'Gated'
LAST_NAME = 'Mentor'

def verify_gating():
    session = requests.Session()
    
    # 1. Register
    print(f"Registering {EMAIL}...")
    session.post(f'{BASE_URL}/auth/register', data={
        'email': EMAIL,
        'password': PASSWORD,
        'confirm_password': PASSWORD,
        'first_name': FIRST_NAME,
        'last_name': LAST_NAME
    })
    
    # Login
    session.post(f'{BASE_URL}/auth/login', data={
        'email': EMAIL,
        'password': PASSWORD
    })
    
    # 2. Apply
    print("Applying for mentorship...")
    apply_resp = session.post(f'{BASE_URL}/mentorship/become-mentor', data={
        'company': 'Gate Corp',
        'job_title': 'Gatekeeper',
        'experience_years': '10',
        'skills': 'Security',
        'bio': 'None shall pass.'
    })
    
    if apply_resp.status_code != 200:
        print(f"Application failed: {apply_resp.status_code}")
        return False

    db_path = 'instance/pragati.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT is_verified_mentor FROM users WHERE email = ?", (EMAIL,))
    row = cursor.fetchone()
    print(f"DEBUG: is_verified_mentor in DB is: {row}")
    conn.close()

    # 3. Check List (Should NOT be here)
    print("Checking Mentor List (Expect: Not Found)...")
    list_resp = session.get(f'{BASE_URL}/mentorship/')
    if '<h3>Gated Mentor</h3>' in list_resp.text:
        print("FAIL: Unverified mentor is visible!")
        return False
    else:
        print("PASS: Unverified mentor is hidden.")

    # 4. Manual DB Verification
    print("Manually verifying via DB...")
    db_path = 'instance/pragati.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_verified_mentor = 1 WHERE email = ?", (EMAIL,))
    conn.commit()
    conn.close()
    
    # 5. Check List (Should BE here)
    print("Checking Mentor List (Expect: Found)...")
    list_resp_2 = session.get(f'{BASE_URL}/mentorship/')
    if '<h3>Gated Mentor</h3>' in list_resp_2.text:
        print("PASS: Verified mentor is visible.")
        return True
    else:
        print("FAIL: Verified mentor is still hidden!")
        # Debug
        # print(list_resp_2.text) 
        return False

if __name__ == '__main__':
    if verify_gating():
        print("Gating Logic Verified!")
    else:
        print("Gating Logic Failed!")
