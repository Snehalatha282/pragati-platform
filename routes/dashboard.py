# routes/dashboard.py
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import db, UserCourse, JobApplication, Assessment
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def home():
    # Get user statistics
    enrolled_courses = UserCourse.query.filter_by(user_id=current_user.id).count()
    completed_courses = UserCourse.query.filter_by(user_id=current_user.id, completed=True).count()
    job_applications = JobApplication.query.filter_by(user_id=current_user.id).count()
    assessments = Assessment.query.filter_by(user_id=current_user.id).count()
    
    # Recent activity
    recent_courses = UserCourse.query.filter_by(user_id=current_user.id)\
        .order_by(UserCourse.enrolled_at.desc()).limit(3).all()
    
    # Recommended jobs (simplified)
    recommended_jobs = []  # Add job matching logic here
    
    # Progress data for charts
    progress_data = {
        'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        'data': [30, 45, 60, 80]
    }
    
    return render_template('dashboard/home.html',
                         enrolled_courses=enrolled_courses,
                         completed_courses=completed_courses,
                         job_applications=job_applications,
                         assessments=assessments,
                         recent_courses=recent_courses,
                         recommended_jobs=recommended_jobs,
                         progress_data=progress_data)

@dashboard_bp.route('/skills')
@login_required
def skills():
    # Get user's skill assessments and courses
    assessments = Assessment.query.filter_by(user_id=current_user.id).all()
    user_courses = UserCourse.query.filter_by(user_id=current_user.id).all()
    
    # Sample skill categories (replace with actual data)
    skill_categories = [
        {'name': 'Technical Skills', 'level': 65, 'color': '#8a2be2'},
        {'name': 'Soft Skills', 'level': 80, 'color': '#ec4899'},
        {'name': 'Industry Knowledge', 'level': 45, 'color': '#06b6d4'},
        {'name': 'Digital Literacy', 'level': 70, 'color': '#10b981'}
    ]
    
    return render_template('dashboard/skills.html',
                         assessments=assessments,
                         user_courses=user_courses,
                         skill_categories=skill_categories)

@dashboard_bp.route('/community')
@login_required
def community():
    # Community posts and discussions
    return render_template('dashboard/community.html')

@dashboard_bp.route('/profile')
@login_required
def profile():
    return render_template('dashboard/profile.html', user=current_user)

@dashboard_bp.route('/settings')
@login_required
def settings():
    return render_template('dashboard/settings.html')

@dashboard_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    data = request.json
    # Update user profile logic here
    return jsonify({'success': True, 'message': 'Profile updated successfully'})

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')