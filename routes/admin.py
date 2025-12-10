# routes/admin.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import User, Job, UserCourse, MentorConnection, JobApplication, CommunityPost

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    # Helper to check admin role
    if current_user.role != 'admin':
        return render_template('404.html'), 404
        
    # Valid stats fetching
    total_users = User.query.count()
    active_jobs = Job.query.filter_by(is_active=True).count()
    course_enrollments = UserCourse.query.count()
    mentor_matches = MentorConnection.query.filter_by(status='accepted').count()
    
    # Extra stats for charts
    job_applications = JobApplication.query.count()
    community_posts = CommunityPost.query.count()

    stats = {
        'total_users': total_users,
        'active_jobs': active_jobs,
        'course_enrollments': course_enrollments,
        'mentor_matches': mentor_matches,
        'job_applications': job_applications,
        'community_posts': community_posts
    }
    
    return render_template('admin/dashboard.html', stats=stats)
