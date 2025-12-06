from flask import Blueprint, render_template, jsonify, request, current_app, url_for
from flask_login import login_required, current_user
from models import db, UserCourse, JobApplication, Assessment
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

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
    try:
        # Handle JSON data or Form data
        if request.is_json:
            data = request.json
        else:
            data = request.form
            
        # Update text fields
        if 'firstName' in data:
            current_user.first_name = data['firstName']
        if 'lastName' in data:
            current_user.last_name = data['lastName']
        if 'phone' in data:
            current_user.phone = data['phone']
        if 'location' in data:
            current_user.location = data['location']
        if 'previousRole' in data:
            current_user.previous_role = data['previousRole']
        if 'desiredRole' in data:
            current_user.desired_role = data['desiredRole']
        if 'careerBreak' in data:
            current_user.career_break_years = int(data['careerBreak']) if data['careerBreak'] else 0
        if 'bio' in data:
            current_user.bio = data['bio']
            
        # Handle skills - expected as comma-separated string or list
        if 'skills' in data:
            skills = data['skills']
            if isinstance(skills, list):
                current_user.skills = ",".join(skills)
            else:
                current_user.skills = skills
        
        # Handle Profile Picture Upload
        if 'profilePicture' in request.files:
            file = request.files['profilePicture']
            if file and file.filename != '':
                filename = secure_filename(f"user_{current_user.id}_{int(datetime.now().timestamp())}_{file.filename}")
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_pics')
                
                # Ensure directory exists
                os.makedirs(upload_folder, exist_ok=True)
                
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                
                # Save relative path to DB
                current_user.profile_picture = f"uploads/profile_pics/{filename}"
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

# routes/dashboard.py (add these imports and routes)
from utils.gemini_assessment import GeminiAssessment
import json

@dashboard_bp.route('/api/assess-skills', methods=['POST'])
@login_required
def assess_skills():
    """API endpoint for skill assessment using Gemini"""
    try:
        data = request.json
        assessment_type = data.get('type', 'technical')
        
        # Prepare user data for assessment
        user_data = {
            'previous_role': current_user.previous_role or 'Not specified',
            'desired_role': current_user.desired_role or 'Not specified',
            'career_break_years': current_user.career_break_years or 0,
            'skills': current_user.skills or '',
            'location': current_user.location or ''
        }
        
        # Try Gemini API if key exists
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if gemini_api_key:
            try:
                assessor = GeminiAssessment()
                result = assessor.assess_skills(user_data, assessment_type)
            except Exception as e:
                # Fallback to mock if Gemini fails
                assessor = GeminiAssessment()
                result = assessor.mock_assessment(user_data)
                result['warning'] = 'Using mock data: ' + str(e)
        else:
            # Use mock data if no API key
            assessor = GeminiAssessment()
            result = assessor.mock_assessment(user_data)
            result['info'] = 'Using mock data. Set GEMINI_API_KEY for real assessments.'
        
        # Save assessment to database
        assessment = Assessment(
            user_id=current_user.id,
            assessment_type=assessment_type,
            result_data=json.dumps(result),
            completed_at=datetime.utcnow()
        )
        db.session.add(assessment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'assessment': result,
            'assessment_id': assessment.id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/generate-learning-path', methods=['POST'])
@login_required
def generate_learning_path():
    """Generate personalized learning path"""
    try:
        data = request.json
        skill_gaps = data.get('skill_gaps', [])
        user_level = data.get('level', 'beginner')
        
        assessor = GeminiAssessment()
        
        # Try Gemini or use mock
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if gemini_api_key:
            try:
                learning_path = assessor.generate_learning_path(skill_gaps, user_level)
            except:
                learning_path = assessor._default_learning_path(skill_gaps, user_level)
        else:
            learning_path = assessor._default_learning_path(skill_gaps, user_level)
        
        return jsonify({
            'success': True,
            'learning_path': learning_path
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/assessment-history', methods=['GET'])
@login_required
def assessment_history():
    """Get user's past assessments"""
    try:
        assessments = Assessment.query.filter_by(
            user_id=current_user.id
        ).order_by(Assessment.completed_at.desc()).limit(10).all()
        
        history = []
        for a in assessments:
            history.append({
                'id': a.id,
                'type': a.assessment_type,
                'score': int(a.score),
                'date': a.completed_at.isoformat()
            })
            
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/submit-quiz', methods=['POST'])
@login_required
def submit_quiz():
    """Submit quiz results and save to database"""
    try:
        data = request.json
        domain = data.get('domain', 'technical')
        score = data.get('score', 0)
        total_questions = data.get('total', 10)
        
        # Calculate percentage
        percentage = (score / total_questions) * 100 if total_questions > 0 else 0
        
        # Create assessment record
        assessment = Assessment(
            user_id=current_user.id,
            assessment_type=domain,
            score=percentage,
            result_data=json.dumps({
                'raw_score': score,
                'total_questions': total_questions,
                'domain': domain,
                'answers': data.get('answers', [])
            }),
            completed_at=datetime.utcnow()
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'assessment_id': assessment.id,
            'message': 'Quiz results saved successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/recommend-courses', methods=['POST'])
@login_required
def recommend_courses():
    """Generate course recommendations based on skill gaps and proficiency"""
    try:
        data = request.json
        skill_gaps = data.get('skill_gaps', [])
        proficiency_level = data.get('level', 'Intermediate') # Beginner, Intermediate, Advanced
        
        # If no explicit skill gaps provided, try to find from latest assessment
        if not skill_gaps:
             latest_assessment = Assessment.query.filter_by(
                user_id=current_user.id
            ).order_by(Assessment.completed_at.desc()).first()
             
             if latest_assessment:
                 try:
                     result = json.loads(latest_assessment.result_data)
                     # If it was a quiz, use the domain as the skill
                     if 'domain' in result:
                         skill_gaps = [result['domain']]
                     else:
                         skill_gaps = result.get('skill_gaps', [])
                 except:
                     pass
        
        # Default skills if still empty
        if not skill_gaps:
            skill_gaps = ['General Python', 'Web Development']

        assessor = GeminiAssessment()
        courses = assessor.get_course_recommendations(skill_gaps, level=proficiency_level)
        
        return jsonify({
            'success': True,
            'courses': courses
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/generate-quiz', methods=['POST'])
@login_required
def generate_quiz():
    """Generate a quiz based on user skills"""
    try:
        data = request.json
        assessment_type = data.get('type', 'technical')
        domain = data.get('domain', '')
        
        # Get user skills or use default
        if domain:
            skills_to_assess = domain
        else:
            skills_to_assess = current_user.skills or "General Python, Web Development"
        
        assessor = GeminiAssessment()
        
        # Use simple caching or just call every time (Gemini is fast enough)
        result = assessor.generate_quiz(skills_to_assess)
        
        return jsonify({
            'success': True,
            'quiz': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500