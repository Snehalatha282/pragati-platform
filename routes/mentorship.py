# routes/mentorship.py
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, User, MentorConnection
from datetime import datetime

mentorship_bp = Blueprint('mentorship', __name__, url_prefix='/mentorship')

@mentorship_bp.route('/')
@login_required
def mentor_list():
    # Get available mentors (only verified ones)
    mentors = User.query.filter(
        User.role == 'mentor',
        User.is_active == True,
        User.is_verified_mentor == True
    ).all()
    
    # Get user's mentor connections
    connections = MentorConnection.query.filter_by(
        mentee_id=current_user.id
    ).all()
    
    # Get pending requests
    pending_requests = MentorConnection.query.filter_by(
        mentor_id=current_user.id,
        status='pending'
    ).all() if current_user.role == 'mentor' else []
    
    return render_template('mentorship/list.html',
                         mentors=mentors,
                         connections=connections,
                         pending_requests=pending_requests)

@mentorship_bp.route('/connect/<int:mentor_id>', methods=['POST'])
@login_required
def connect_mentor(mentor_id):
    mentor = User.query.get_or_404(mentor_id)
    
    # Check if already connected
    existing = MentorConnection.query.filter_by(
        mentor_id=mentor_id,
        mentee_id=current_user.id
    ).first()
    
    if existing:
        flash('You have already sent a connection request to this mentor.', 'warning')
        return redirect(url_for('mentorship.mentor_list'))
    
    # Create connection request
    connection = MentorConnection(
        mentor_id=mentor_id,
        mentee_id=current_user.id,
        status='pending',
        created_at=datetime.utcnow()
    )
    
    db.session.add(connection)
    db.session.commit()
    
    flash('Connection request sent successfully!', 'success')
    return redirect(url_for('mentorship.mentor_list'))

@mentorship_bp.route('/connections')
@login_required
def my_connections():
    connections = MentorConnection.query.filter(
        (MentorConnection.mentee_id == current_user.id) |
        (MentorConnection.mentor_id == current_user.id)
    ).all()
    
    return render_template('mentorship/connections.html',
                         connections=connections)

@mentorship_bp.route('/request/<int:request_id>/<action>', methods=['POST'])
@login_required
def handle_request(request_id, action):
    connection = MentorConnection.query.get_or_404(request_id)
    
    if connection.mentor_id != current_user.id:
        flash('Unauthorized action.', 'error')
        return redirect(url_for('mentorship.mentor_list'))
    
    if action == 'accept':
        connection.status = 'accepted'
        flash('Connection request accepted.', 'success')
    elif action == 'reject':
        connection.status = 'rejected'
        flash('Connection request rejected.', 'info')
    
    db.session.commit()
    return redirect(url_for('mentorship.mentor_list'))

@mentorship_bp.route('/become-mentor', methods=['GET', 'POST'])
@login_required
def become_mentor():
    # Check if already a mentor
    if current_user.role == 'mentor':
        if current_user.is_verified_mentor:
            flash('You are already a verified mentor.', 'info')
            return redirect(url_for('mentorship.mentor_list'))
        else:
            # Render the page but with a "Pending" state (handled in template or flash)
            flash('Your mentor application is pending verification from your company.', 'warning')
            return render_template('mentorship/become_mentor.html', is_pending=True)

    if request.method == 'POST':
        print("\n" + "="*50)
        print("--- REACHED BECOME MENTOR POST ---")
        print("="*50 + "\n")
        # Update user role to mentor
        current_user.role = 'mentor'
        current_user.bio = request.form.get('bio', '')
        current_user.skills = request.form.get('skills', '')
        
        # New Verification Fields
        current_user.company = request.form.get('company', '')
        current_user.job_title = request.form.get('job_title', '')
        
        try:
            current_user.experience_years = int(request.form.get('experience_years', 0))
        except ValueError:
            current_user.experience_years = 0
            
        current_user.is_verified_mentor = False # Pending verification
        
        db.session.commit()
        
        # Send Verification Email
        from utils.email_demo import send_verification_email
        import uuid
        
        # In a real app, store this token in DB/Redis with expiration
        token = str(uuid.uuid4())
        # Use verify_mentor_action route
        verification_link = url_for('mentorship.verify_mentor_action', user_id=current_user.id, token=token, _external=True)
        
        # Send email (Mock)
        send_verification_email(f"{current_user.first_name} {current_user.last_name}", current_user.company, verification_link)
        
        flash('Congratulations! You are now a mentor. A verification email has been sent to your company for review.', 'success')
        return redirect(url_for('mentorship.mentor_list'))
    
    return render_template('mentorship/become_mentor.html')

@mentorship_bp.route('/verify/<int:user_id>/<token>')
def verify_mentor_action(user_id, token):
    user = User.query.get_or_404(user_id)
    # In a real app, verify token validity
    user.is_verified_mentor = True
    db.session.commit()
    return "<h1>Employment Verified!</h1><p>The mentor profile has been authenticated. You can close this window.</p>"

@mentorship_bp.route('/session/<int:session_id>', methods=['GET', 'POST'])
@login_required
def mentorship_session(session_id):
    # Missing handler for mentorship sessions
    pass