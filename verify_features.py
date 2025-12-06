
import requests
import json
import os

BASE_URL = "http://127.0.0.1:5000"

def login(email, password):
    session = requests.Session()
    response = session.post(f"{BASE_URL}/auth/login", data={
        "email": email,
        "password": password
    })
    if response.status_code == 200 and "dashboard" in response.url:
        print("[PASS] Login successful")
        return session
    else:
        print(f"[FAIL] Login failed: {response.status_code}")
        return None

def test_quiz_generation(session):
    print("\n--- Testing Quiz Generation ---")
    domain = "Python"
    response = session.post(f"{BASE_URL}/dashboard/api/generate-quiz", json={
        "type": "technical",
        "domain": domain
    })
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            questions = data.get("quiz", {}).get("questions", [])
            print(f"[PASS] Quiz generated with {len(questions)} questions")
            if len(questions) >= 10:
                print("[PASS] Question count meets requirement (>=10)")
            else:
                print(f"[WARN] Question count {len(questions)} is less than 10")
            
            # Check structure of first question
            if questions:
                q = questions[0]
                if all(k in q for k in ["question", "options", "correct_answer"]):
                    print("[PASS] Question structure looks correct")
                else:
                    print("[FAIL] Invalid question structure")
        else:
            print(f"[FAIL] API returned success=False: {data}")
    else:
        print(f"[FAIL] API request failed: {response.status_code}")

def test_profile_update(session):
    print("\n--- Testing Profile Update ---")
    
    # Create a dummy image file
    with open("test_avatar.jpg", "wb") as f:
        f.write(os.urandom(1024))
    
    files = {
        'profilePicture': ('test_avatar.jpg', open('test_avatar.jpg', 'rb'), 'image/jpeg')
    }
    
    data = {
        'firstName': 'Test',
        'lastName': 'User',
        'bio': 'Updated bio via verification script',
        'skills': 'Python,Flask,Testing'
    }
    
    response = session.post(f"{BASE_URL}/dashboard/update-profile", data=data, files=files)
    
    # Cleanup
    files['profilePicture'][1].close()
    if os.path.exists("test_avatar.jpg"):
        os.remove("test_avatar.jpg")
        
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print("[PASS] Profile updated successfully")
        else:
            print(f"[FAIL] Profile update failed: {result}")
    else:
        print(f"[FAIL] HTTP Error: {response.status_code}")

if __name__ == "__main__":
    # Use distinct test credentials
    import time
    timestamp = int(time.time())
    email = f"test_{timestamp}@example.com"
    password = "password123"
    
    
    # Register first
    print(f"Registering user {email}...")
    requests.post(f"{BASE_URL}/auth/register", data={
        "email": email,
        "password": password,
        "confirm_password": password,
        "first_name": "Test",
        "last_name": "User",
        "phone": "555-0199"
    })
    
    session = login(email, password)
    if session:
        test_quiz_generation(session)
        test_profile_update(session)
