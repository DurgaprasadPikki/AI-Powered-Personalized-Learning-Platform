from bson import ObjectId
from datetime import datetime
from config.database import get_db

class UserModel:
    """User data model"""
    
    COLLECTION = 'users'
    
    @staticmethod
    def create_user(email, username, password_hash):
        """Create new user"""
        db = get_db()
        user_data = {
            'email': email,
            'username': username,
            'password_hash': password_hash,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'total_points': 0,
            'topics_completed': [],
            'current_level': 'Beginner'
        }
        result = db[UserModel.COLLECTION].insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        db = get_db()
        return db[UserModel.COLLECTION].find_one({'email': email})
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        db = get_db()
        try:
            return db[UserModel.COLLECTION].find_one({'_id': ObjectId(user_id)})
        except:
            return None
    
    @staticmethod
    def update_user(user_id, update_data):
        """Update user"""
        db = get_db()
        update_data['updated_at'] = datetime.utcnow()
        result = db[UserModel.COLLECTION].update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def exists(email):
        """Check if user exists"""
        db = get_db()
        return db[UserModel.COLLECTION].find_one({'email': email}) is not None


class TopicModel:
    """Topic data model"""
    
    COLLECTION = 'topics'
    
    @staticmethod
    def create_topic(name, description, category, difficulty, content, order):
        """Create new topic"""
        db = get_db()
        topic_data = {
            'name': name,
            'description': description,
            'category': category,
            'difficulty': difficulty,
            'content': content,
            'order': order,
            'created_at': datetime.utcnow(),
            'prerequisites': []
        }
        result = db[TopicModel.COLLECTION].insert_one(topic_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_topic(topic_id):
        """Get topic by ID"""
        db = get_db()
        try:
            return db[TopicModel.COLLECTION].find_one({'_id': ObjectId(topic_id)})
        except:
            return None
    
    @staticmethod
    def get_topics_by_difficulty(difficulty):
        """Get all topics of specific difficulty"""
        db = get_db()
        return list(db[TopicModel.COLLECTION].find(
            {'difficulty': difficulty}
        ).sort('order', 1))
    
    @staticmethod
    def get_all_topics():
        """Get all topics"""
        db = get_db()
        return list(db[TopicModel.COLLECTION].find().sort('order', 1))


class QuestionModel:
    """Question data model"""
    
    COLLECTION = 'questions'
    
    @staticmethod
    def create_question(topic_id, text, options, correct_answer, difficulty, explanation):
        """Create new question"""
        db = get_db()
        question_data = {
            'topic_id': ObjectId(topic_id),
            'text': text,
            'options': options,
            'correct_answer': correct_answer,
            'difficulty': difficulty,
            'explanation': explanation,
            'created_at': datetime.utcnow()
        }
        result = db[QuestionModel.COLLECTION].insert_one(question_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_question(question_id):
        """Get question by ID"""
        db = get_db()
        try:
            return db[QuestionModel.COLLECTION].find_one({'_id': ObjectId(question_id)})
        except:
            return None
    
    @staticmethod
    def get_questions_by_topic(topic_id, difficulty=None, limit=10):
        """Get questions for a topic"""
        db = get_db()
        query = {'topic_id': ObjectId(topic_id)}
        if difficulty:
            query['difficulty'] = difficulty
        return list(db[QuestionModel.COLLECTION].find(query).limit(limit))


class QuizAttemptModel:
    """Quiz attempt/result data model"""
    
    COLLECTION = 'quiz_attempts'
    
    @staticmethod
    def record_attempt(user_id, question_id, topic_id, selected_answer, is_correct, time_spent):
        """Record a quiz attempt"""
        db = get_db()
        attempt_data = {
            'user_id': ObjectId(user_id),
            'question_id': ObjectId(question_id),
            'topic_id': ObjectId(topic_id),
            'selected_answer': selected_answer,
            'is_correct': is_correct,
            'time_spent': time_spent,
            'timestamp': datetime.utcnow()
        }
        result = db[QuizAttemptModel.COLLECTION].insert_one(attempt_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_user_attempts(user_id, topic_id=None):
        """Get user's quiz attempts"""
        db = get_db()
        query = {'user_id': ObjectId(user_id)}
        if topic_id:
            query['topic_id'] = ObjectId(topic_id)
        return list(db[QuizAttemptModel.COLLECTION].find(query).sort('timestamp', -1))
    
    @staticmethod
    def get_recent_attempts(user_id, limit=20):
        """Get user's recent attempts"""
        db = get_db()
        return list(db[QuizAttemptModel.COLLECTION].find(
            {'user_id': ObjectId(user_id)}
        ).sort('timestamp', -1).limit(limit))


class ProgressModel:
    """User progress tracking model"""
    
    COLLECTION = 'user_progress'
    
    @staticmethod
    def update_progress(user_id, topic_id, accuracy, avg_time, questions_answered):
        """Update or create user progress for a topic"""
        db = get_db()
        result = db[ProgressModel.COLLECTION].update_one(
            {'user_id': ObjectId(user_id), 'topic_id': ObjectId(topic_id)},
            {'$set': {
                'accuracy': accuracy,
                'avg_time': avg_time,
                'questions_answered': questions_answered,
                'updated_at': datetime.utcnow()
            }},
            upsert=True
        )
        return result.upserted_id or True
    
    @staticmethod
    def get_user_progress(user_id):
        """Get user's progress across all topics"""
        db = get_db()
        return list(db[ProgressModel.COLLECTION].find(
            {'user_id': ObjectId(user_id)}
        ))
    
    @staticmethod
    def get_topic_progress(user_id, topic_id):
        """Get user's progress for specific topic"""
        db = get_db()
        return db[ProgressModel.COLLECTION].find_one({
            'user_id': ObjectId(user_id),
            'topic_id': ObjectId(topic_id)
        })


class RecommendationModel:
    """Recommendation model"""
    
    COLLECTION = 'recommendations'
    
    @staticmethod
    def save_recommendation(user_id, recommended_topics):
        """Save recommendation for user"""
        db = get_db()
        result = db[RecommendationModel.COLLECTION].update_one(
            {'user_id': ObjectId(user_id)},
            {'$set': {
                'recommended_topics': recommended_topics,
                'generated_at': datetime.utcnow()
            }},
            upsert=True
        )
        return result.upserted_id or True
    
    @staticmethod
    def get_recommendation(user_id):
        """Get user's latest recommendation"""
        db = get_db()
        return db[RecommendationModel.COLLECTION].find_one(
            {'user_id': ObjectId(user_id)}
        )
