import os
import json
import google.generativeai as genai
from typing import Dict, List, Any
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Force reload environment variables to ensure we get the latest key
load_dotenv(override=True)

class GeminiAssessment:
    def __init__(self):
        """Initialize Gemini API"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Use gemini-flash-latest as per available models
            self.model = genai.GenerativeModel('gemini-flash-latest')
            print(f"[Core] Gemini API Configured. Key starts with: {self.api_key[:10]}...", flush=True)
        else:
            self.model = None
            print("[Core] GEMINI_API_KEY not found. Using mock mode.", flush=True)
        
        # Assessment templates
        self.templates = {
            'technical': """You are a career assessment expert specializing in evaluating technical skills for women returning to the workforce.

User Profile:
- Previous Role: {previous_role}
- Desired Role: {desired_role}
- Career Break: {career_break_years} years
- Skills: {skills}

Please analyze and provide:
1. Skill Gap Analysis: Identify specific technical skills needed for {desired_role}
2. Market Relevance: Which skills are most in-demand currently
3. Learning Path: Suggest specific courses/topics to bridge gaps
4. Timeline: Estimated time to become job-ready
5. Confidence Score: Rate readiness from 1-10

Format response as JSON with keys: skill_gaps, market_demand, learning_path, timeline_months, confidence_score, recommendations.""",
            
            'soft_skills': """You are assessing soft skills for career re-entry.

User Context:
- Previous Role: {previous_role}
- Break Duration: {career_break_years} years
- Goals: {desired_role}

Assess these soft skills:
1. Communication
2. Leadership
3. Adaptability
4. Problem-solving
5. Time Management
6. Confidence Level

Provide scores (1-10) and specific recommendations for improvement.

Format as JSON with keys: scores (dict), recommendations, strengths, areas_for_improvement.""",
            
            'career_readiness': """Assess overall career readiness after break.

Profile:
- Experience: {previous_role}
- Target: {desired_role}
- Break: {career_break_years} years
- Location: {location}

Evaluate:
1. Resume gaps handling
2. Interview preparedness
3. Networking strategy
4. Industry knowledge
5. Salary expectations
6. Work-life balance considerations

Provide actionable advice and readiness percentage.

Format as JSON: readiness_percentage, action_plan, interview_tips, salary_guidance."""
        }
    
    def assess_skills(self, user_data: Dict[str, Any], assessment_type: str = 'technical') -> Dict[str, Any]:
        """Run skill assessment using Gemini"""
        try:
            if not self.model:
                 raise Exception("Gemini API not configured")

            # Prepare prompt
            template = self.templates.get(assessment_type, self.templates['technical'])
            prompt = template.format(**user_data)
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Parse response
            try:
                # Try to extract JSON from response
                content = response.text
                
                # Find JSON in response (handles cases where response has extra text)
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_str = content[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    # Fallback to simple parsing
                    result = {'analysis': content, 'raw_response': content}
                    
            except json.JSONDecodeError:
                result = {'analysis': response.text, 'raw_response': response.text}
            
            # Add metadata
            result['assessment_type'] = assessment_type
            result['status'] = 'success'
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'assessment_type': assessment_type
            }
    
    def generate_learning_path(self, skill_gaps: List[str], user_level: str = 'beginner') -> Dict[str, Any]:
        """Generate personalized learning path"""
        prompt = f"""Create a 30-day learning path for someone at {user_level} level to learn these skills: {', '.join(skill_gaps)}.
        
        Include:
        1. Daily learning objectives
        2. Recommended resources (free preferred)
        3. Practice projects
        4. Milestones to track progress
        5. Time commitment per day
        
        Format as JSON with: daily_schedule, resources, projects, milestones, time_commitment."""
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except:
            return self._default_learning_path(skill_gaps, user_level)
    
    def _default_learning_path(self, skill_gaps: List[str], user_level: str) -> Dict[str, Any]:
        """Default learning path if Gemini fails"""
        return {
            'daily_schedule': [
                {'day': 1, 'topic': 'Foundation', 'activities': ['Basic concepts', 'Setup environment']},
                {'day': 2-7, 'topic': 'Core Skills', 'activities': skill_gaps[:3]},
                {'day': 8-21, 'topic': 'Projects', 'activities': ['Build portfolio projects']},
                {'day': 22-30, 'topic': 'Preparation', 'activities': ['Interview prep', 'Resume building']}
            ],
            'resources': ['FreeCodeCamp', 'Coursera', 'YouTube tutorials'],
            'projects': ['Build a personal portfolio', 'Create a small application'],
            'milestones': ['Complete foundation', 'Build first project', 'Prepare resume'],
            'time_commitment': '2-3 hours daily'
        }
    
    def mock_assessment(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock assessment for testing when API key is not available"""
        return {
            'skill_gaps': ['React', 'Cloud Computing', 'Data Structures'],
            'market_demand': ['Python', 'AWS', 'React', 'Docker'],
            'learning_path': {
                'phase1': 'Brush up fundamentals (2 weeks)',
                'phase2': 'Learn modern frameworks (4 weeks)',
                'phase3': 'Build portfolio projects (4 weeks)'
            },
            'timeline_months': 3,
            'confidence_score': 7,
            'recommendations': [
                'Complete Python for Data Science course',
                'Build 2-3 portfolio projects',
                'Join tech communities',
                'Practice mock interviews'
            ],
            'status': 'success',
            'assessment_type': 'technical',
            'is_mock': True
        }

    def get_course_recommendations(self, skill_gaps: List[str], level: str = 'Intermediate') -> List[Dict[str, Any]]:
        """Generate course recommendations based on skill gaps and level"""
        prompt = f"""Identify the top 5 online courses for a '{level}' level learner to master these skills: {', '.join(skill_gaps)}.
        
        For each course, provide:
        1. Course Title (Must be real and high-quality)
        2. Platform (Coursera, Udemy, edX, etc.)
        3. Rating (0.0 to 5.0)
        4. Price (string, e.g., 'Free', '$19.99', '$49')
        5. Price Value (float, 0 for free, otherwise numeric price for sorting)
        6. URL (real or plausible search URL)
        
        Consider both 'Top Rated' and 'Best Value' (Free/Low cost) options suitable for {level}s.
        
        Format as a JSON array of objects with keys: title, platform, rating, price, price_value, url.
        DO NOT include any markdown formatting or extra text, just the JSON array.
        """
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text
            
            # Clean up potential markdown formatting
            if '```json' in content:
                content = content.replace('```json', '').replace('```', '')
            
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx != -1 and end_idx != 0:
                try:
                    return json.loads(content[start_idx:end_idx])
                except json.JSONDecodeError as e:
                    print(f"[Core Error] JSON Decode Error in Recommendations. Raw content:\n{content[start_idx:end_idx]}", flush=True)
                    raise e
            else:
                print(f"[Core Error] Could not find JSON array in response. Raw content:\n{content}", flush=True)
                raise Exception("Failed to parse course recommendations")
                
        except Exception as e:
            print(f"[Core Error] Course Recommendation Error: {e}", flush=True)
            raise e

    def _mock_course_recommendations(self, skill_gaps: List[str]) -> List[Dict[str, Any]]:
        """Mock data for course recommendations"""
        return [
            {
                "title": f"Complete {skill_gaps[0] if skill_gaps else 'Python'} Bootcamp",
                "platform": "Udemy",
                "rating": 4.8,
                "price": "$14.99",
                "price_value": 14.99,
                "url": "#"
            },
            {
                "title": f"{skill_gaps[0] if skill_gaps else 'Python'} for Everybody",
                "platform": "Coursera",
                "rating": 4.9,
                "price": "Free",
                "price_value": 0,
                "url": "#"
            },
            {
                "title": "Modern Development Masterclass",
                "platform": "Pluralsight",
                "rating": 4.6,
                "price": "$29/mo",
                "price_value": 29,
                "url": "#"
            },
            {
                "title": "FreeCodeCamp Full Certification",
                "platform": "FreeCodeCamp",
                "rating": 5.0,
                "price": "Free",
                "price_value": 0,
                "url": "#"
            },
            {
                "title": "Advanced Concepts Specialization",
                "platform": "edX",
                "rating": 4.7,
                "price": "$49",
                "price_value": 49,
                "url": "#"
            }
        ]

    def generate_quiz(self, skills: str, difficulty: str = 'intermediate') -> Dict[str, Any]:
        """Generate a quiz based on user skills"""
        prompt = f"""Create a technical quiz to assess these skills: {skills}.
        Difficulty Level: {difficulty}
        
        Generate 10 to 15 Multiple Choice Questions.
        
        For each question provide:
        1. Question text
        2. Four options (array of strings)
        3. Correct answer index (0-3)
        4. Explanation (why the answer is correct)
        5. Topic/Skill being tested
        
        Format as a JSON object with a key 'questions' containing an array of objects.
        Each object MUST have these exact keys:
        - "question": (string) The question text
        - "options": (array of 4 strings)
        - "correct_answer": (integer) 0-3
        - "explanation": (string)
        - "topic": (string)
        
        Do NOT include markdown formatting.
        """
        
        try:
            print(f"[Core] Generating quiz for skills: {skills}", flush=True)
            response = self.model.generate_content(prompt)
            content = response.text
             
            # Clean up potential markdown
            if '```json' in content:
                content = content.replace('```json', '').replace('```', '')
            
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                result = json.loads(content[start_idx:end_idx])
                # Validate question count
                if len(result.get('questions', [])) < 10:
                    print(f"[Core Warning] Generated only {len(result.get('questions', []))} questions, expected 10-15.", flush=True)
                else:
                    print(f"[Core Success] AI Successfully generated {len(result.get('questions', []))} questions.", flush=True)
                
                return result
            else:
                print(f"[Core Error] Failed to parse JSON. Raw output:\n{content}", flush=True)
                raise Exception("Failed to parse AI response (Invalid JSON)")
                
        except Exception as e:
            print(f"[Core Error] Quiz Generation Error: {e}", flush=True)
            raise e

    def _mock_quiz(self, skills: str) -> Dict[str, Any]:
        """Mock quiz data with 10 questions"""
        return {
            "questions": [
                {
                    "id": 1,
                    "question": "Which of the following is NOT a core data structure in Python?",
                    "options": ["List", "Dictionary", "Tuple", "Array"],
                    "correct_answer": 3,
                    "explanation": "Python does not have a native Array data structure; it uses Lists. Arrays are provided by libraries like NumPy.",
                    "topic": "Python"
                },
                {
                    "id": 2,
                    "question": "What does DOM stand for in Web Development?",
                    "options": ["Document Object Model", "Data Object Mode", "Digital Ordinance Model", "Desktop Orientation Module"],
                    "correct_answer": 0,
                    "explanation": "DOM stands for Document Object Model, which is the data representation of the objects that comprise the structure and content of a document on the web.",
                    "topic": "Frontend"
                },
                {
                    "id": 3,
                    "question": "Which Git command is used to record changes to the repository?",
                    "options": ["git record", "git commit", "git save", "git push"],
                    "correct_answer": 1,
                    "explanation": "git commit is used to capture a snapshot of the project's currently staged changes.",
                    "topic": "Git"
                },
                {
                    "id": 4,
                    "question": "In React, what is used to pass data to a component from outside?",
                    "options": ["setState", "render", "props", "PropTypes"],
                    "correct_answer": 2,
                    "explanation": "Props (short for properties) are the way we pass data from parent to child components.",
                    "topic": "React"
                },
                {
                    "id": 5,
                    "question": "What is the primary function of CSS?",
                    "options": ["To program logic", "To structure content", "To style and layout web pages", "To store data"],
                    "correct_answer": 2,
                    "explanation": "CSS (Cascading Style Sheets) is used to describe the presentation of a document written in HTML.",
                    "topic": "CSS"
                },
                {
                    "id": 6,
                    "question": "What is the purpose of a primary key in a database?",
                    "options": ["To encrypt data", "To uniquely identify each record", "To sort data alphabetically", "To store large files"],
                    "correct_answer": 1,
                    "explanation": "A primary key is a unique identifier for a database record, ensuring no duplicates exist.",
                    "topic": "Database"
                },
                {
                    "id": 7,
                    "question": "Which HTTP method is typically used to retrieve data?",
                    "options": ["POST", "PUT", "DELETE", "GET"],
                    "correct_answer": 3,
                    "explanation": "GET is the HTTP method designed to retrieve information from a server.",
                    "topic": "API"
                },
                {
                    "id": 8,
                    "question": "What is 'hoisting' in JavaScript?",
                    "options": ["Lifting weights", "Moving declarations to the top", "Deleting variables", "Hiding functions"],
                    "correct_answer": 1,
                    "explanation": "Hoisting is JavaScript's default behavior of moving declarations to the top of the current scope.",
                    "topic": "JavaScript"
                },
                {
                    "id": 9,
                    "question": "What does SQL stand for?",
                    "options": ["Structured Question List", "Simple Query Language", "Structured Query Language", "Standard Question Logic"],
                    "correct_answer": 2,
                    "explanation": "SQL stands for Structured Query Language, used for managing relational databases.",
                    "topic": "Database"
                },
                {
                    "id": 10,
                    "question": "Which of these is a containerization tool?",
                    "options": ["Kubernetes", "Docker", "Jenkins", "Ansible"],
                    "correct_answer": 1,
                    "explanation": "Docker is a platform for developing, shipping, and running applications in containers.",
                    "topic": "DevOps"
                }
            ]
        }
