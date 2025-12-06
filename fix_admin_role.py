from app import app, db
from models import User

with app.app_context():
    admin = User.query.filter_by(email="admin@pragati.com").first()
    if admin:
        print(f"Found user: {admin.email} with Role: {admin.role}")
        admin.role = 'admin'
        db.session.commit()
        print("SUCCESS: Updated role to 'admin'")
    else:
        print("ERROR: User not found!")
