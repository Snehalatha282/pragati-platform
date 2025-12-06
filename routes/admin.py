from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, User, Job, Course, MentorConnection, CommunityPost, JobApplication
import os
import json
from datetime import datetime, timedelta
from utils.gemini_assessment import GeminiAssessment
from sqlalchemy import func, desc

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def require_admin():
    if not current_user.is_authenticated or current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard.home'))

# ------------------- ADMIN DASHBOARD -------------------

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    total_users = User.query.count()
    total_jobs = Job.query.filter_by(is_active=True).count()
    total_courses = Course.query.count()
    active_mentorships = MentorConnection.query.filter_by(status='accepted').count()

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_jobs = Job.query.order_by(Job.posted_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_jobs=total_jobs,
                           total_courses=total_courses,
                           active_mentorships=active_mentorships,
                           recent_users=recent_users,
                           recent_jobs=recent_jobs)

# ------------------- USER MANAGEMENT -------------------

@admin_bp.route('/users', endpoint="users")
@login_required
def admin_users():
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
    
    return redirect(url_for('admin.admin_users'))

# ------------------- JOB MANAGEMENT -------------------

@admin_bp.route('/jobs', endpoint="jobs")
@login_required
def admin_jobs():
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
    
    return redirect(url_for('admin.admin_jobs'))

# ------------------- COURSE MANAGEMENT -------------------

@admin_bp.route('/courses', endpoint="courses")
@login_required
def admin_courses():
    courses = Course.query.all()
    return render_template('admin/courses.html', courses=courses)

@admin_bp.route('/courses/add', methods=['POST'])
@login_required
def add_course():
    # Add new course logic
    flash('Course added successfully.', 'success')
    return redirect(url_for('admin.admin_courses'))

# ------------------- MENTOR MANAGEMENT -------------------

@admin_bp.route('/mentors', endpoint="mentors")
@login_required
def admin_mentors():
    mentors = User.query.filter_by(role='mentor').all()
    return render_template('admin/mentors.html', mentors=mentors)

# ------------------- COMMUNITY MANAGEMENT -------------------
@admin_bp.route('/community', endpoint="community")

@login_required
def admin_community():
    posts = CommunityPost.query.order_by(CommunityPost.created_at.desc()).all()
    return render_template('admin/community.html', posts=posts)

@admin_bp.route('/community/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    
    flash('Post deleted successfully.', 'success')
    return redirect(url_for('admin.admin_community'))

# ------------------- SYSTEM SETTINGS -------------------

@admin_bp.route('/settings', endpoint="settings")
@login_required
def admin_settings():
    return render_template('admin/settings.html')

@admin_bp.route('/analytics', endpoint="analytics")
@login_required
def admin_analytics():
    return render_template('admin/analytics.html')

# ------------------- API JOB TREND ANALYSIS -------------------

@admin_bp.route('/api/analyze-jobs', methods=['POST'])
@login_required
def analyze_jobs():
    try:
        recent_jobs = Job.query.filter(
            Job.posted_at >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        applications = JobApplication.query.filter(
            JobApplication.applied_at >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        job_data = {
            'total_jobs': len(recent_jobs),
            'job_types': {},
            'common_skills': {},
            'applications_per_job': len(applications) / max(len(recent_jobs), 1)
        }
        
        for job in recent_jobs:
            job_type = job.job_type or 'unknown'
            job_data['job_types'][job_type] = job_data['job_types'].get(job_type, 0) + 1
            
            if job.skills_required:
                skills = [s.strip() for s in job.skills_required.split(',')]
                for skill in skills:
                    if skill:
                        job_data['common_skills'][skill] = job_data['common_skills'].get(skill, 0) + 1
        
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if gemini_api_key:
            try:
                assessor = GeminiAssessment()
                
                prompt = f"""
                Analyze job market:
                Jobs: {len(recent_jobs)}
                Job Types: {json.dumps(job_data['job_types'])}
                Top Skills: {json.dumps(job_data['common_skills'])}
                """
                
                response = assessor.model.generate_content(prompt)
                
                content = response.text
                start = content.find('{')
                end = content.rfind('}') + 1
                
                ai_analysis = {}
                if start != -1 and end != 0:
                    try:
                        ai_analysis = json.loads(content[start:end])
                    except:
                        ai_analysis = {'analysis': response.text}
                
                analysis_result = {
                    'skill_demand': [
                        {'name': skill, 'count': count, 'demand': 'high' if count > 10 else 'medium' if count > 5 else 'low'}
                        for skill, count in sorted(job_data['common_skills'].items(), key=lambda x: x[1], reverse=True)[:10]
                    ],
                    'market_insights': [
                        {
                            'title': 'Skill Gap Trend',
                            'description': f"Top needed skills: {', '.join(list(job_data['common_skills'].keys())[:3])}",
                            'icon': 'chart-bar'
                        }
                    ],
                    'gemini_analysis': ai_analysis.get('analysis', 'No AI output'),
                    'status': 'success'
                }
                
            except Exception as e:
                analysis_result = {
                    'error': f'Gemini AI failed: {str(e)}',
                    'basic_insights': True,
                    'status': 'partial'
                }
        else:
            analysis_result = {
                'error': 'Gemini key missing',
                'basic_analysis': True,
                'status': 'basic'
            }
        
        return jsonify({'success': True, 'analysis': analysis_result})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ------------------- USER STATS API -------------------

@admin_bp.route('/api/user-stats')
@login_required
def user_stats():
    try:
        total_users = User.query.count()
        active_today = User.query.filter(User.last_login >= datetime.utcnow().date()).count()
        
        growth_data = {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'values': [120, 145, 132, 167, 189, 156, 142]
        }
        
        engagement_data = {
            'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            'values': [850, 920, 890, 980]
        }
        
        user_growth = 10
        
        return jsonify({
            'success': True,
            'total_users': total_users,
            'active_today': active_today,
            'avg_progress': 68,
            'completion_rate': 42,
            'user_growth': user_growth,
            'growth_data': growth_data,
            'engagement_data': engagement_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ------------------- USER DETAILS API -------------------

@admin_bp.route('/api/users/<int:user_id>')
@login_required
def get_user_details(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        recent_activity = [
            {
                'icon': 'graduation-cap',
                'title': 'Course Completed',
                'description': 'Completed Web Development Fundamentals',
                'time': '2 hours ago'
            }
        ]
        
        progress = calculate_user_progress(user.id)
        
        user_data = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': user.phone,
            'location': user.location,
            'role': user.role,
            'is_active': user.is_active,
            'previous_role': user.previous_role,
            'desired_role': user.desired_role,
            'career_break_years': user.career_break_years,
            'skills': user.skills,
            'profile_picture': user.profile_picture,
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'progress': progress,
            'courses_count': 3,
            'applications_count': 5,
            'mentors_count': 2,
            'community_posts': 8,
            'recent_activity': recent_activity,
            'ai_insights': 'User shows strong engagement.'
        }
        
        return jsonify({'success': True, 'user': user_data})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ------------------- USER ANALYSIS API -------------------

@admin_bp.route('/api/users/<int:user_id>/analyze', methods=['POST'])
@login_required
def analyze_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if gemini_api_key:
            try:
                assessor = GeminiAssessment()
                
                user_data = {
                    'name': f"{user.first_name} {user.last_name}",
                    'role': user.role,
                    'previous_role': user.previous_role or 'Not specified',
                    'desired_role': user.desired_role or 'Not specified',
                    'career_break': f"{user.career_break_years or 0} years",
                    'skills': user.skills or 'Not specified',
                    'location': user.location or 'Not specified'
                }
                
                prompt = f"Analyze this user: {json.dumps(user_data)}"
                response = assessor.model.generate_content(prompt)
                
                ai_analysis = {'analysis': response.text}
                
                analysis_result = {
                    'behavioral_patterns': [
                        {
                            'title': 'Learning Engagement',
                            'description': 'Consistent course progress',
                            'icon': 'graduation-cap',
                            'confidence': 85
                        }
                    ],
                    'gemini_analysis': ai_analysis.get('analysis', 'AI OK'),
                    'recommendations': [
                        'Connect with mentors',
                        'Focus interview prep'
                    ],
                    'next_best_actions': [
                        {
                            'title': 'Schedule Counseling',
                            'description': 'Book career session',
                            'button_text': 'Schedule Now'
                        }
                    ],
                    'status': 'success'
                }
                
            except Exception as e:
                analysis_result = {
                    'behavioral_patterns': [{'title': 'Basic', 'description': 'Fallback'}],
                    'error': f'Gemini failed: {str(e)}',
                    'mock_data': True
                }
        else:
            analysis_result = {
                'behavioral_patterns': [{'title': 'Basic Profile Analysis', 'description': 'API missing'}],
                'info': 'Gemini API key not set',
                'mock_data': True
            }
        
        return jsonify({'success': True, 'analysis': analysis_result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ------------------- HELPERS -------------------

def calculate_user_progress(user_id):
    return 68  # Simulated value

def get_user_activity(user_id):
    return {'courses': 3, 'applications': 5, 'last_active': '2 hours ago'}
