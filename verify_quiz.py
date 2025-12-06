
import os
import json
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def verify_quiz_api():
    """Verify that the quiz API returns valid questions"""
    
    # Create a test client
    with app.test_client() as client:
        with app.app_context():
            # Cleanup previous test user if exists
            user = User.query.filter_by(email='verifier@example.com').first()
            if user:
                db.session.delete(user)
                db.session.commit()
            
            # Create fresh test user
            user = User(
                email='verifier@example.com',
                password_hash=generate_password_hash('password123'),
                first_name='Verifier',
                last_name='User',
                skills='Python, React'
            )
            db.session.add(user)
            db.session.commit()

            # Login
            login_resp = client.post('/auth/login', data={
                'email': 'verifier@example.com',
                'password': 'password123'
            }, follow_redirects=True)
            
            if login_resp.status_code != 200:
                print(f"Login failed: {login_resp.status_code}")
                return False

            # Test Quiz API
            print("Testing /dashboard/api/generate-quiz...")
            try:
                resp = client.post('/dashboard/api/generate-quiz', 
                                 json={'type': 'technical'},
                                 content_type='application/json')
                
                if resp.status_code == 200:
                    data = resp.get_json()
                    if data.get('success') and 'quiz' in data and 'questions' in data['quiz']:
                        questions = data['quiz']['questions']
                        print(f"Success! Received {len(questions)} questions.")
                        print(f"Sample Question: {questions[0]['question']}")
                        return True
                    else:
                        print(f"Invalid response structure: {data.keys()}")
                        return False
                else:
                    print(f"API Error: {resp.status_code} - {resp.data}")
                    return False
            except Exception as e:
                print(f"Request failed: {e}")
                return False

if __name__ == "__main__":
    if verify_quiz_api():
        print("Backend Verification Passed!")
    else:
        print("Backend Verification Failed!")
