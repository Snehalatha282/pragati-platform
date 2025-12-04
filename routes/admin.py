# routes/admin.py
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, User, Job, Course, MentorConnection, CommunityPost

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def require_admin():
    if not current_user.is_authenticated or current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))

@admin_bp.route('/')
@login_required
def dashboard():
    # Get statistics for admin dashboard
    total_users = User.query.count()
    total_jobs = Job.query.filter_by(is_active=True).count()
    total_courses = Course.query.count()
    active_mentorships = MentorConnection.query.filter_by(status='accepted').count()
    
    # Recent activities
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_jobs = Job.query.order_by(Job.posted_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_jobs=total_jobs,
                         total_courses=total_courses,
                         active_mentorships=active_mentorships,
                         recent_users=recent_users,
                         recent_jobs=recent_jobs)

@admin_bp.route('/users')
@login_required
def users():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    action = 'activated' if user.is_active else 'deactivated'
    flash(f'User {action} successfully.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/jobs')
@login_required
def jobs():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    jobs = Job.query.order_by(Job.posted_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/jobs.html', jobs=jobs)

@admin_bp.route('/jobs/<int:job_id>/toggle', methods=['POST'])
@login_required
def toggle_job(job_id):
    job = Job.query.get_or_404(job_id)
    job.is_active = not job.is_active
    db.session.commit()
    
    action = 'activated' if job.is_active else 'deactivated'
    flash(f'Job {action} successfully.', 'success')
    return redirect(url_for('admin.jobs'))

@admin_bp.route('/courses')
@login_required
def courses():
    courses = Course.query.all()
    return render_template('admin/courses.html', courses=courses)

@admin_bp.route('/courses/add', methods=['POST'])
@login_required
def add_course():
    # Add new course logic
    flash('Course added successfully.', 'success')
    return redirect(url_for('admin.courses'))

@admin_bp.route('/mentors')
@login_required
def mentors():
    mentors = User.query.filter_by(role='mentor').all()
    return render_template('admin/mentors.html', mentors=mentors)

@admin_bp.route('/community')
@login_required
def community():
    posts = CommunityPost.query.order_by(CommunityPost.created_at.desc()).all()
    return render_template('admin/community.html', posts=posts)

@admin_bp.route('/community/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    
    flash('Post deleted successfully.', 'success')
    return redirect(url_for('admin.community'))

@admin_bp.route('/settings')
@login_required
def settings():
    return render_template('admin/settings.html')

@admin_bp.route('/analytics')
@login_required
def analytics():
    # Analytics data
    return render_template('admin/analytics.html')