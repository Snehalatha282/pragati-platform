from app import app, db
from models import User

with app.app_context():
    admin = User.query.filter_by(email="admin@pragati.com").first()
    if admin:
        print(f"Admin User Found: OK")
        print(f"Email: {admin.email}")
        print(f"Role: {admin.role}")
        if admin.role != 'admin':
            print("FIXING: User exists but role is not 'admin'. Updating...")
            admin.role = 'admin'
            db.session.commit()
            print("Role updated to 'admin'.")
    else:
        print("Admin User NOT Found. Creating...")
        admin = User(
            email="admin@pragati.com",
            first_name="Admin",
            last_name="User",
            role="admin"
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Admin user created with password 'admin123'.")
