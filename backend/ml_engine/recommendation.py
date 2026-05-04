import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import json
import os
from models.data_models import QuizAttemptModel, ProgressModel, TopicModel, UserModel
from bson import ObjectId

class FeatureExtractor:
    """Extract features from user performance data"""
    
    @staticmethod
    def extract_user_features(user_id, all_topics):
        """
        Extract features for a user to feed into ML model
        Returns feature vector for each topic
        """
        progress_data = ProgressModel.get_user_progress(user_id)
        recent_attempts = QuizAttemptModel.get_recent_attempts(user_id, limit=50)
        
        # Create feature matrix
        features_dict = {}
        
        for topic in all_topics:
            topic_id = str(topic['_id'])
            
            # Find progress for this topic
            topic_progress = next(
                (p for p in progress_data if str(p['topic_id']) == topic_id),
                None
            )
            
            # Find attempts for this topic
            topic_attempts = [a for a in recent_attempts if str(a['topic_id']) == topic_id]
            
            # Extract features
            accuracy = topic_progress['accuracy'] if topic_progress else 0.0
            avg_time = topic_progress['avg_time'] if topic_progress else 0.0
            questions_answered = topic_progress['questions_answered'] if topic_progress else 0
            
            # Recency score (more recent = higher score)
            recency_score = 0.0
            if topic_attempts:
                most_recent = topic_attempts[0]['timestamp']
                days_since = (datetime.utcnow() - most_recent).days
                recency_score = max(0, 1 - (days_since / 30))
            
            # Consistency score (based on standard deviation of recent scores)
            consistency_score = 1.0
            if len(topic_attempts) >= 3:
                recent_correct = [1 if a['is_correct'] else 0 for a in topic_attempts[:10]]
                if len(recent_correct) > 0:
                    consistency_score = 1 - (np.std(recent_correct) if len(recent_correct) > 1 else 0)
            
            # Time efficiency (lower time for high accuracy = high efficiency)
            time_efficiency = 0.0
            if accuracy > 0 and avg_time > 0:
                time_efficiency = min(1.0, accuracy / (avg_time / 10))
            
            features_dict[topic_id] = {
                'accuracy': accuracy,
                'avg_time': min(avg_time, 180) / 180,  # Normalize to 0-1
                'questions_answered': min(questions_answered, 50) / 50,
                'recency_score': recency_score,
                'consistency_score': consistency_score,
                'time_efficiency': time_efficiency,
                'attempted': 1 if topic_progress else 0,
                'difficulty': self._encode_difficulty(topic.get('difficulty', 'Beginner'))
            }
        
        return features_dict
    
    @staticmethod
    def _encode_difficulty(difficulty):
        """Encode difficulty level to numeric"""
        mapping = {'Beginner': 0, 'Intermediate': 1, 'Advanced': 2}
        return mapping.get(difficulty, 0)


class RecommendationEngine:
    """ML-based recommendation engine"""
    
    def __init__(self):
        self.model_path = os.path.join(
            os.path.dirname(__file__), 'models'
        )
        os.makedirs(self.model_path, exist_ok=True)
    
    def get_recommendations(self, user_id, top_n=3):
        """
        Generate top-N topic recommendations for user
        """
        all_topics = TopicModel.get_all_topics()
        user = UserModel.get_user_by_id(user_id)
        
        if not user or not all_topics:
            return []
        
        # Extract features
        extractor = FeatureExtractor()
        features_dict = extractor.extract_user_features(user_id, all_topics)
        
        # Score each topic using hybrid approach
        topic_scores = []
        
        for topic in all_topics:
            topic_id = str(topic['_id'])
            features = features_dict.get(topic_id, {})
            
            # Skip if already completed
            if topic_id in user.get('topics_completed', []):
                continue
            
            # Scoring algorithm
            score = self._calculate_recommendation_score(features, topic, user)
            
            topic_scores.append({
                'topic_id': topic_id,
                'topic_name': topic['name'],
                'difficulty': topic['difficulty'],
                'score': score,
                'reason': self._get_recommendation_reason(features, topic)
            })
        
        # Sort by score and return top N
        recommendations = sorted(topic_scores, key=lambda x: x['score'], reverse=True)[:top_n]
        
        return recommendations
    
    def _calculate_recommendation_score(self, features, topic, user):
        """
        Hybrid scoring function combining multiple signals
        """
        current_level = user.get('current_level', 'Beginner')
        
        # 1. Difficulty progression: recommend next level
        level_scores = {
            'Beginner': {'Beginner': 0.5, 'Intermediate': 1.0, 'Advanced': 0.2},
            'Intermediate': {'Beginner': 0.1, 'Intermediate': 0.7, 'Advanced': 1.0},
            'Advanced': {'Beginner': 0, 'Intermediate': 0.2, 'Advanced': 0.8}
        }
        
        topic_difficulty = topic.get('difficulty', 'Beginner')
        difficulty_score = level_scores.get(current_level, {}).get(topic_difficulty, 0.5)
        
        # 2. Content strength: recommend weak areas for practice
        accuracy = features.get('accuracy', 0)
        weakness_score = max(0, 1 - accuracy)  # Inverted: lower accuracy = higher score
        
        # 3. Engagement: recommend areas based on recency and consistency
        engagement_score = (
            features.get('recency_score', 0) * 0.3 +
            features.get('consistency_score', 0.5) * 0.3 +
            features.get('time_efficiency', 0) * 0.2
        )
        
        # 4. Attempt status: prefer less attempted topics
        attempt_factor = 1.0 if features.get('attempted', 0) == 0 else 0.7
        
        # Combined score
        final_score = (
            difficulty_score * 0.3 +
            weakness_score * 0.3 +
            engagement_score * 0.2 +
            attempt_factor * 0.2
        )
        
        return round(final_score, 3)
    
    def _get_recommendation_reason(self, features, topic):
        """Generate human-readable reason for recommendation"""
        accuracy = features.get('accuracy', 0)
        attempted = features.get('attempted', 0)
        
        if not attempted:
            return "Not yet attempted"
        elif accuracy < 0.5:
            return "Needs improvement"
        elif accuracy < 0.8:
            return "Keep practicing"
        else:
            return "Ready for next level"


class AdaptiveQuizEngine:
    """Adaptive difficulty adjustment for quiz"""
    
    DIFFICULTY_THRESHOLD = 0.75  # 75% accuracy threshold
    
    @staticmethod
    def adjust_difficulty(user_id, topic_id, current_accuracy, avg_time_seconds):
        """
        Adjust quiz difficulty based on performance
        Returns (next_difficulty, should_increase)
        """
        # Get current topic progress
        progress = ProgressModel.get_topic_progress(user_id, topic_id)
        current_difficulty = progress.get('current_difficulty', 'Beginner') if progress else 'Beginner'
        
        # Calculate performance score
        performance_score = current_accuracy
        
        # Adjust based on time: penalize if taking too long
        if avg_time_seconds > 60:
            performance_score *= 0.9
        
        # Decision logic
        next_difficulty = current_difficulty
        should_increase = False
        
        if current_difficulty == 'Beginner':
            if performance_score >= AdaptiveQuizEngine.DIFFICULTY_THRESHOLD:
                next_difficulty = 'Intermediate'
                should_increase = True
        
        elif current_difficulty == 'Intermediate':
            if performance_score >= AdaptiveQuizEngine.DIFFICULTY_THRESHOLD:
                next_difficulty = 'Advanced'
                should_increase = True
            elif performance_score < 0.5:
                next_difficulty = 'Beginner'
        
        elif current_difficulty == 'Advanced':
            if performance_score < 0.6:
                next_difficulty = 'Intermediate'
        
        return next_difficulty, should_increase

class InsightGenerator:
    """Generate insights from user performance"""
    
    @staticmethod
    def generate_insights(user_id):
        """Generate performance insights for user"""
        progress_data = ProgressModel.get_user_progress(user_id)
        recent_attempts = QuizAttemptModel.get_recent_attempts(user_id, limit=100)
        
        insights = {
            'weak_topics': [],
            'strong_topics': [],
            'improvement_trend': None,
            'recommended_focus': None,
            'overall_accuracy': 0,
            'total_questions': len(recent_attempts)
        }
        
        if not progress_data:
            return insights
        
        # Calculate overall accuracy
        correct_answers = sum(1 for a in recent_attempts if a['is_correct'])
        insights['overall_accuracy'] = round(
            (correct_answers / len(recent_attempts) * 100) if recent_attempts else 0, 1
        )
        
        # Identify weak and strong topics
        sorted_progress = sorted(progress_data, key=lambda x: x['accuracy'])
        insights['weak_topics'] = [
            {'topic_id': str(p['topic_id']), 'accuracy': p['accuracy']}
            for p in sorted_progress[:2]
        ]
        insights['strong_topics'] = [
            {'topic_id': str(p['topic_id']), 'accuracy': p['accuracy']}
            for p in sorted_progress[-2:]
        ]
        
        # Calculate improvement trend (last 20 attempts vs previous)
        if len(recent_attempts) >= 20:
            recent_correct = sum(1 for a in recent_attempts[:20] if a['is_correct'])
            previous_correct = sum(1 for a in recent_attempts[20:40] if a['is_correct']) if len(recent_attempts) >= 40 else recent_correct
            
            recent_accuracy = recent_correct / 20
            previous_accuracy = previous_correct / min(20, len(recent_attempts) - 20)
            
            trend = round((recent_accuracy - previous_accuracy) * 100, 1)
            insights['improvement_trend'] = "Improving" if trend > 0 else "Declining" if trend < 0 else "Stable"
        
        # Recommendation focus
        if insights['weak_topics']:
            insights['recommended_focus'] = "Focus on weak topics for improvement"
        else:
            insights['recommended_focus'] = "Try advanced challenges to grow"
        
        return insights
