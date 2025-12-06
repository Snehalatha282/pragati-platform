# database.py
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
# from models import db, User, Course, Job

def init_db():
    """Initialize database with sample data"""
    db.create_all()
    
    # # Create admin user if not exists
    # if not User.query.filter_by(email='admin@pragati.com').first():
    #     admin = User(
    #         email='admin@pragati.com',
    #         first_name='Admin',
    #         last_name='Pragati',
    #         role='admin'
    #     )
    #     admin.set_password('admin123')
    #     db.session.add(admin)
    #     db.session.commit()
    
    # # Add sample courses
    # if Course.query.count() == 0:
    #     courses = [
    #         Course(
    #             title='Python for Data Science',
    #             description='Learn Python programming for data analysis and visualization',
    #             category='Programming',
    #             difficulty='beginner',
    #             duration_hours=20,
    #             skills_covered='["Python", "Pandas", "NumPy", "Data Analysis"]',
    #             is_free=True
    #         ),
    #         Course(
    #             title='Web Development Fundamentals',
    #             description='Master HTML, CSS, and JavaScript for modern web development',
    #             category='Web Development',
    #             difficulty='beginner',
    #             duration_hours=30,
    #             skills_covered='["HTML", "CSS", "JavaScript", "Responsive Design"]',
    #             is_free=True
    #         ),
    #         Course(
    #             title='Digital Marketing Strategy',
    #             description='Learn to create effective digital marketing campaigns',
    #             category='Marketing',
    #             difficulty='intermediate',
    #             duration_hours=15,
    #             skills_covered='["SEO", "Social Media", "Content Marketing", "Analytics"]',
    #             is_free=True
    #         )
    #     ]
    #     db.session.bulk_save_objects(courses)
    #     db.session.commit()