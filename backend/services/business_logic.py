from models.data_models import UserModel, TopicModel, QuestionModel, QuizAttemptModel, ProgressModel
from utils.auth import PasswordHandler, InputValidator, JWTHandler
from ml_engine.recommendation import RecommendationEngine, AdaptiveQuizEngine, InsightGenerator
from datetime import datetime
from bson import ObjectId
import statistics

class AuthService:
    """Authentication service"""
    
    @staticmethod
    def register(email, username, password):
        """
        Register new user
        Returns: (success, message, user_id)
        """
        # Validate inputs
        if not InputValidator.validate_email(email):
            return False, "Invalid email format", None
        
        if not InputValidator.validate_username(username):
            return False, "Username must be 3-20 chars, alphanumeric only", None
        
        valid, msg = InputValidator.validate_password(password)
        if not valid:
            return False, msg, None
        
        # Check if user exists
        if UserModel.exists(email):
            return False, "Email already registered", None
        
        # Hash password and create user
        password_hash = PasswordHandler.hash_password(password)
        user_id = UserModel.create_user(email, username, password_hash)
        
        return True, "Registration successful", user_id
    
    @staticmethod
    def login(email, password):
        """
        Login user
        Returns: (success, message, token, user_data)
        """
        user = UserModel.get_user_by_email(email)
        if not user:
            return False, "Invalid credentials", None, None
        
        if not PasswordHandler.verify_password(password, user['password_hash']):
            return False, "Invalid credentials", None, None
        
        # Generate JWT token
        token = JWTHandler.create_token(str(user['_id']))
        
        user_data = {
            'user_id': str(user['_id']),
            'email': user['email'],
            'username': user['username'],
            'total_points': user.get('total_points', 0),
            'current_level': user.get('current_level', 'Beginner')
        }
        
        return True, "Login successful", token, user_data
    
    @staticmethod
    def get_user_profile(user_id):
        """Get user profile"""
        user = UserModel.get_user_by_id(user_id)
        if not user:
            return None
        
        return {
            'user_id': str(user['_id']),
            'email': user['email'],
            'username': user['username'],
            'total_points': user.get('total_points', 0),
            'current_level': user.get('current_level', 'Beginner'),
            'topics_completed': user.get('topics_completed', []),
            'created_at': user.get('created_at').isoformat() if user.get('created_at') else None
        }

from config.database import get_db   # ✅ ADD THIS IMPORT

class TopicService:

    @staticmethod
    def get_all_topics():
        db = get_db()   # ✅ correct way
        topics = db["topics"].find().sort("order", 1)

        return [
            {
                "topic_id": str(t["_id"]),
                "name": t.get("name"),
                "description": t.get("description", ""),
                "difficulty": t.get("difficulty", "Beginner"),
                "category": t.get("category", "General")
            }
            for t in topics
        ]
    
    @staticmethod
    def get_topic_details(topic_id):
        """Get detailed topic information"""
        topic = TopicModel.get_topic(topic_id)
        if not topic:
            return None
        
        return {
            'topic_id': str(topic['_id']),
            'name': topic['name'],
            'description': topic['description'],
            'difficulty': topic['difficulty'],
            'category': topic['category'],
            'content': topic['content']
        }
    
    @staticmethod
    def get_questions_for_topic(topic_id, difficulty=None, limit=5):
        """Get questions for quiz"""
        questions = QuestionModel.get_questions_by_topic(topic_id, difficulty, limit)
        return [
            {
                'question_id': str(q['_id']),
                'text': q['text'],
                'options': q['options'],
                'difficulty': q['difficulty']
            }
            for q in questions
        ]


class QuizService:
    """Quiz management and scoring service"""
    
    @staticmethod
    def submit_answer(user_id, question_id, selected_answer, time_spent_seconds):
        """
        Submit quiz answer and record result
        Returns: (correct, explanation, points_earned)
        """
        question = QuestionModel.get_question(question_id)
        if not question:
            return False, "Question not found", 0
        
        is_correct = selected_answer == question['correct_answer']
        points = 10 if is_correct else 0
        
        # Record attempt
        QuizAttemptModel.record_attempt(
            user_id,
            question_id,
            str(question['topic_id']),
            selected_answer,
            is_correct,
            time_spent_seconds
        )
        
        # Update user points
        user = UserModel.get_user_by_id(user_id)
        if user:
            new_points = user.get('total_points', 0) + points
            UserModel.update_user(user_id, {'total_points': new_points})
        
        explanation = question.get('explanation', '')
        
        return is_correct, explanation, points
    
    @staticmethod
    def get_topic_statistics(user_id, topic_id):
        """Get user's statistics for a topic"""
        attempts = QuizAttemptModel.get_user_attempts(user_id, topic_id)
        
        if not attempts:
            return {
                'accuracy': 0,
                'avg_time': 0,
                'questions_answered': 0,
                'correct_answers': 0
            }
        
        correct_count = sum(1 for a in attempts if a['is_correct'])
        total_count = len(attempts)
        avg_time = statistics.mean([a['time_spent'] for a in attempts]) if attempts else 0
        
        stats = {
            'accuracy': round(correct_count / total_count * 100, 1) if total_count > 0 else 0,
            'avg_time': round(avg_time, 2),
            'questions_answered': total_count,
            'correct_answers': correct_count
        }
        
        # Update progress in database
        ProgressModel.update_progress(
            user_id,
            topic_id,
            stats['accuracy'] / 100,
            stats['avg_time'],
            total_count
        )
        
        return stats
    
    @staticmethod
    def get_next_question(user_id, topic_id):
        """
        Get next question with adaptive difficulty
        """
        stats = QuizService.get_topic_statistics(user_id, topic_id)
        current_accuracy = stats['accuracy'] / 100
        avg_time = stats['avg_time']
        
        # Adjust difficulty
        next_difficulty, _ = AdaptiveQuizEngine.adjust_difficulty(
            user_id,
            topic_id,
            current_accuracy,
            avg_time
        )
        
        # Get question
        questions = TopicService.get_questions_for_topic(topic_id, next_difficulty, limit=1)
        
        return {
            'question': questions[0] if questions else None,
            'current_difficulty': next_difficulty,
            'stats': stats
        }


class ProgressService:
    """Progress tracking service"""
    
    @staticmethod
    def get_user_dashboard(user_id):
        """Get dashboard data for user"""
        user = UserModel.get_user_by_id(user_id)
        if not user:
            return None
        
        # Get progress across all topics
        progress_data = ProgressModel.get_user_progress(user_id)
        
        # Calculate statistics
        total_topics = len(progress_data)
        avg_accuracy = round(
            statistics.mean([p['accuracy'] * 100 for p in progress_data]),
            1
        ) if progress_data else 0
        
        total_time = sum(p.get('avg_time', 0) * p.get('questions_answered', 0) for p in progress_data)
        total_questions = sum(p.get('questions_answered', 0) for p in progress_data)
        
        # Get insights
        insights = InsightGenerator.generate_insights(user_id)
        
        return {
            'user': {
                'username': user['username'],
                'total_points': user.get('total_points', 0),
                'current_level': user.get('current_level', 'Beginner')
            },
            'statistics': {
                'topics_studied': total_topics,
                'average_accuracy': avg_accuracy,
                'total_time_spent': round(total_time / 60, 1),  # Convert to minutes
                'total_questions_answered': total_questions
            },
            'insights': insights,
            'progress_by_topic': [
                {
                    'topic_id': str(p['topic_id']),
                    'accuracy': round(p['accuracy'] * 100, 1),
                    'questions_answered': p.get('questions_answered', 0)
                }
                for p in progress_data
            ]
        }


class RecommendationService:
    """Recommendation service"""
    
    @staticmethod
    def get_recommendations(user_id):
        """Get personalized topic recommendations"""
        engine = RecommendationEngine()
        recommendations = engine.get_recommendations(user_id, top_n=3)
        
        return {
            'recommendations': recommendations,
            'generated_at': datetime.utcnow().isoformat()
        }
