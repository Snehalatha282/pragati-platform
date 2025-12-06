from app import app
from models import User

with app.app_context():
    users = User.query.all()
    print("-" * 50)
    print(f"{'ID':<5} {'Email':<30} {'Role':<10} {'Password Hash (Prefix)'}")
    print("-" * 50)
    for u in users:
        print(f"{u.id:<5} {u.email:<30} {u.role:<10} {u.password_hash[:10]}...")
    print("-" * 50)
