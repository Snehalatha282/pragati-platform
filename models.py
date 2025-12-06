from flask_login import UserMixin
from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime




class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')
    career_break_years = db.Column(db.Integer)
    previous_role = db.Column(db.String(100))
    desired_role = db.Column(db.String(100))
    skills = db.Column(db.Text)
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Mentor Fields
    company = db.Column(db.String(100))
    job_title = db.Column(db.String(100))
    experience_years = db.Column(db.Integer)
    is_verified_mentor = db.Column(db.Boolean, default=False)

    # Relationships
    assessments = db.relationship('Assessment', backref='user', lazy=True)
    mentor_connections = db.relationship('MentorConnection', 
                                         foreign_keys='MentorConnection.mentee_id',
                                         backref='mentee', lazy=True)
    job_applications = db.relationship('JobApplication', backref='applicant', lazy=True)
    courses = db.relationship('UserCourse', backref='user', lazy=True)

    # Password helpers
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Placeholder dashboard methods
    def get_progress_percentage(self):
        return 0

    def get_recommended_jobs(self):
        return []

    def get_skill_gaps(self):
        return []


class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assessment_type = db.Column(db.String(50))
    score = db.Column(db.Float)
    result_data = db.Column(db.Text)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    difficulty = db.Column(db.String(20))
    duration_hours = db.Column(db.Integer)
    skills_covered = db.Column(db.Text)
    video_url = db.Column(db.String(300))
    resources = db.Column(db.Text)
    is_free = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserCourse(db.Model):
    __tablename__ = 'user_courses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    progress = db.Column(db.Float, default=0.0)
    completed = db.Column(db.Boolean, default=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)


class MentorConnection(db.Model):
    __tablename__ = 'mentor_connections'

    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mentee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_interaction = db.Column(db.DateTime)


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100))
    job_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    skills_required = db.Column(db.Text)
    salary_range = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    posted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

    applications = db.relationship('JobApplication', backref='job', lazy=True)


class JobApplication(db.Model):
    __tablename__ = 'job_applications'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='applied')
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    resume_url = db.Column(db.String(300))
    cover_letter = db.Column(db.Text)


class CommunityPost(db.Model):
    __tablename__ = 'community_posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    category = db.Column(db.String(50))
    likes = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
