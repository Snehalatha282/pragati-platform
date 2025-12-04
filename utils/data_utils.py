# utils/data_utils.py
import json
from datetime import datetime, timedelta
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_user_progress(user_id, db_session):
    """
    Calculate user's overall progress percentage
    """
    # This is a simplified example
    progress_components = {
        'profile_completion': 25,
        'skill_assessment': 25,
        'course_enrollment': 25,
        'mentor_connection': 15,
        'job_application': 10
    }
    
    total_progress = 0
    # Calculate actual progress based on user data
    # This would query the database in a real implementation
    
    return min(total_progress, 100)

def recommend_jobs(user_skills, job_listings, top_n=5):
    """
    Recommend jobs based on user skills
    """
    if not user_skills or not job_listings:
        return []
    
    # Create TF-IDF vectors for skills
    vectorizer = TfidfVectorizer()
    
    # Combine user skills into a single string
    user_skills_text = ' '.join(user_skills)
    
    # Create documents: user skills + job requirements
    documents = [user_skills_text] + [job['requirements'] for job in job_listings]
    
    # Fit and transform
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Calculate similarity between user skills and each job
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    # Get top N recommendations
    top_indices = cosine_similarities.argsort()[-top_n:][::-1]
    recommendations = [job_listings[i] for i in top_indices]
    
    return recommendations

def analyze_skill_gaps(user_skills, target_role_skills):
    """
    Analyze skill gaps for a target role
    """
    user_skill_set = set(user_skills)
    target_skill_set = set(target_role_skills)
    
    # Missing skills
    missing_skills = list(target_skill_set - user_skill_set)
    
    # Existing skills
    existing_skills = list(user_skill_set.intersection(target_skill_set))
    
    # Additional skills (bonus)
    additional_skills = list(user_skill_set - target_skill_set)
    
    return {
        'missing_skills': missing_skills,
        'existing_skills': existing_skills,
        'additional_skills': additional_skills,
        'coverage_percentage': len(existing_skills) / len(target_skill_set) * 100 if target_skill_set else 0
    }

def generate_weekly_report(user_data):
    """
    Generate weekly progress report
    """
    report = {
        'week_start': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
        'week_end': datetime.now().strftime('%Y-%m-%d'),
        'courses_completed': 0,
        'hours_studied': 0,
        'job_applications': 0,
        'mentor_sessions': 0,
        'skill_improvements': [],
        'next_week_goals': []
    }
    
    # Populate report based on user_data
    # This would query actual user activities from database
    
    return report

def format_statistics(data):
    """
    Format statistics for display
    """
    if isinstance(data, dict):
        return {k: format_statistics(v) for k, v in data.items()}
    elif isinstance(data, (int, float)):
        if data >= 1000:
            return f"{data/1000:.1f}K"
        return str(data)
    else:
        return data

def export_user_data(user_id, db_session):
    """
    Export all user data for GDPR compliance
    """
    # This would query all user-related data from the database
    export_data = {
        'profile': {},
        'activities': [],
        'courses': [],
        'applications': [],
        'connections': []
    }
    
    return json.dumps(export_data, indent=2, default=str)