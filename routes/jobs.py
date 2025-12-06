# routes/jobs.py
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Job, JobApplication, User
from datetime import datetime

jobs_bp = Blueprint('jobs', __name__, url_prefix='/jobs')

@jobs_bp.route('/')
@login_required
def job_listings():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Filters
    job_type = request.args.get('type', '')
    location = request.args.get('location', '')
    search = request.args.get('search', '')
    
    # Build query
    query = Job.query.filter_by(is_active=True)
    
    if job_type:
        query = query.filter(Job.job_type == job_type)
    if location:
        query = query.filter(Job.location.contains(location))
    if search:
        query = query.filter(
            Job.title.contains(search) | 
            Job.company.contains(search) |
            Job.description.contains(search)
        )
    
    # Pagination
    jobs = query.order_by(Job.posted_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # User's applications
    user_applications = JobApplication.query.filter_by(
        user_id=current_user.id
    ).all()
    applied_job_ids = [app.job_id for app in user_applications]
    
    # Job types for filter
    job_types = db.session.query(Job.job_type).distinct().all()
    job_types = [j[0] for j in job_types if j[0]]
    
    return render_template('jobs/listings.html',
                         jobs=jobs,
                         applied_job_ids=applied_job_ids,
                         job_types=job_types,
                         current_filters={
                             'type': job_type,
                             'location': location,
                             'search': search
                         })

@jobs_bp.route('/<int:job_id>')
@login_required
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Check if user has applied
    has_applied = JobApplication.query.filter_by(
        user_id=current_user.id,
        job_id=job_id
    ).first() is not None
    
    # Similar jobs
    similar_jobs = Job.query.filter(
        Job.id != job_id,
        Job.is_active == True
    ).limit(3).all()
    
    return render_template('jobs/detail.html',
                         job=job,
                         has_applied=has_applied,
                         similar_jobs=similar_jobs)

@jobs_bp.route('/<int:job_id>/apply', methods=['POST'])
@login_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Check if already applied
    existing_application = JobApplication.query.filter_by(
        user_id=current_user.id,
        job_id=job_id
    ).first()
    
    if existing_application:
        flash('You have already applied for this job.', 'warning')
        return redirect(url_for('jobs.job_detail', job_id=job_id))
    
    # Create application
    application = JobApplication(
        job_id=job_id,
        user_id=current_user.id,
        cover_letter=request.form.get('cover_letter', ''),
        applied_at=datetime.utcnow()
    )
    
    # Handle resume upload
    if 'resume' in request.files:
        resume = request.files['resume']
        if resume.filename:
            # Save resume logic here
            application.resume_url = f"uploads/resumes/{current_user.id}_{resume.filename}"
    
    db.session.add(application)
    db.session.commit()
    
    flash('Application submitted successfully!', 'success')
    return redirect(url_for('jobs.job_detail', job_id=job_id))

@jobs_bp.route('/applications')
@login_required
def my_applications():
    applications = JobApplication.query.filter_by(
        user_id=current_user.id
    ).order_by(JobApplication.applied_at.desc()).all()
    
    return render_template('jobs/applications.html',
                         applications=applications)

@jobs_bp.route('/save/<int:job_id>', methods=['POST'])
@login_required
def save_job(job_id):
    # Implementation for saving jobs
    return jsonify({'success': True})

@jobs_bp.route('/api/recommended')
@login_required
def recommended_jobs():
    # Simple recommendation logic
    jobs = Job.query.filter_by(is_active=True).limit(5).all()
    
    return jsonify([{
        'id': job.id,
        'title': job.title,
        'company': job.company,
        'location': job.location,
        'job_type': job.job_type
    } for job in jobs])

# In routes/jobs.py - Missing route
@jobs_bp.route('/applications/<int:application_id>/status', methods=['POST'])
@login_required
def update_application_status(application_id):
    # Missing handler for updating application status
    pass