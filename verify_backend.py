
import os
import sys
from app import app, db
from models import User

def verify_backend():
    print("Setting up test...")
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # Create test user
            user = User(
                email='verifier@example.com',
                first_name='Verifier',
                last_name='User',
                password_hash='placeholder'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            print("Logging in...")
            login_resp = client.post('/auth/login', data={
                'email': 'verifier@example.com',
                'password': 'password123'
            }, follow_redirects=True)
            
            if b'Logged in successfully' not in login_resp.data and login_resp.status_code != 200:
                print("Login failed!")
                return False

            print("Testing /dashboard/api/recommend-courses...")
            # Test with specific skills
            resp = client.post('/dashboard/api/recommend-courses', json={
                'skill_gaps': ['Python', 'Machine Learning']
            })
            
            if resp.status_code != 200:
                print(f"API call failed with status {resp.status_code}")
                print(resp.json)
                return False
                
            data = resp.json
            if not data.get('success'):
                print("API returned success=False")
                return False
                
            courses = data.get('courses', [])
            print(f"Received {len(courses)} courses.")
            
            if not courses:
                print("No courses returned!")
                return False
                
            # Verify structure
            first_course = courses[0]
            required_keys = ['title', 'platform', 'rating', 'price', 'price_value']
            missing = [k for k in required_keys if k not in first_course]
            
            if missing:
                print(f"Missing keys in course object: {missing}")
                return False
                
            print("\nVerification Successful! Sample Course:")
            print(f"Title: {first_course['title']}")
            print(f"Price: {first_course['price']} (Value: {first_course['price_value']})")
            print(f"Rating: {first_course['rating']}")
            return True

if __name__ == "__main__":
    try:
        if verify_backend():
            print("\n✅ Backend verification passed!")
        else:
            print("\n❌ Backend verification failed!")
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
