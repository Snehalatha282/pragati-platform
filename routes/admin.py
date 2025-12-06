from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import User, MentorConnection, db
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin Dashboard View"""
    # Stats
    total_users = User.query.count()
    total_mentors = User.query.filter_by(role='mentor', is_verified_mentor=True).count()
    pending_mentors = User.query.filter_by(role='mentor', is_verified_mentor=False).count()
    
    # Lists
    users = User.query.order_by(User.created_at.desc()).limit(50).all()
    pending_verification = User.query.filter_by(role='mentor', is_verified_mentor=False).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_mentors=total_mentors,
                         pending_mentors=pending_mentors,
                         users=users,
                         pending_verification=pending_verification)

@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot delete yourself!', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    try:
        # Manual cleanup if cascade isn't perfect (safe bet)
        # Note: SQLAlchemy usually handles this if relationships are set to cascade
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.email} deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')
        
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/approve-mentor/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def approve_mentor(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'mentor':
        flash('User is not a mentor applicant.', 'warning')
        return redirect(url_for('admin.dashboard'))
        
    user.is_verified_mentor = True
    db.session.commit()
    flash(f'Mentor {user.first_name} verified successfully.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/reject-mentor/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def reject_mentor(user_id):
    user = User.query.get_or_404(user_id)
    # Revert to normal user
    user.role = 'user'
    user.is_verified_mentor = False
    db.session.commit()
    flash(f'Mentor application for {user.first_name} rejected.', 'info')
    return redirect(url_for('admin.dashboard'))
