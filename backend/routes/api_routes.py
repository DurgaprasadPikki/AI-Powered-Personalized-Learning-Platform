from flask import Blueprint, request, jsonify
from services.business_logic import AuthService, TopicService, QuizService, ProgressService, RecommendationService
from utils.auth import require_auth

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
topics_bp = Blueprint('topics', __name__, url_prefix='/api/topics')
quiz_bp = Blueprint('quiz', __name__, url_prefix='/api/quiz')
progress_bp = Blueprint('progress', __name__, url_prefix='/api/progress')
recommendation_bp = Blueprint('recommendations', __name__, url_prefix='/api/recommendations')

# ======================== AUTH ROUTES ========================

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['email', 'username', 'password']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success, message, user_id = AuthService.register(
            data['email'].strip(),
            data['username'].strip(),
            data['password']
        )
        
        if success:
            return jsonify({
                'message': message,
                'user_id': user_id
            }), 201
        else:
            return jsonify({'error': message}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['email', 'password']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success, message, token, user_data = AuthService.login(
            data['email'].strip(),
            data['password']
        )
        
        if success:
            return jsonify({
                'message': message,
                'token': token,
                'user': user_data
            }), 200
        else:
            return jsonify({'error': message}), 401
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get user profile"""
    try:
        user_profile = AuthService.get_user_profile(request.user_id)
        
        if not user_profile:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user_profile), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ======================== TOPICS ROUTES ========================

@topics_bp.route('', methods=['GET'])
@require_auth
def get_topics():
    """Get all topics"""
    try:
        topics = TopicService.get_all_topics()
        return jsonify({'topics': topics}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@topics_bp.route('/<topic_id>', methods=['GET'])
@require_auth
def get_topic_details(topic_id):
    """Get topic details"""
    try:
        topic = TopicService.get_topic_details(topic_id)
        
        if not topic:
            return jsonify({'error': 'Topic not found'}), 404
        
        return jsonify(topic), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ======================== QUIZ ROUTES ========================

@quiz_bp.route('/questions/<topic_id>', methods=['GET'])
@require_auth
def get_quiz_questions(topic_id):
    """Get questions for quiz"""
    try:
        difficulty = request.args.get('difficulty')
        limit = int(request.args.get('limit', 5))
        
        questions = TopicService.get_questions_for_topic(topic_id, difficulty, limit)
        
        if not questions:
            return jsonify({'error': 'No questions found'}), 404
        
        return jsonify({'questions': questions}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/submit', methods=['POST'])
@require_auth
def submit_answer():
    """Submit quiz answer"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['question_id', 'selected_answer', 'time_spent']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        is_correct, explanation, points = QuizService.submit_answer(
            request.user_id,
            data['question_id'],
            data['selected_answer'],
            data['time_spent']
        )
        
        return jsonify({
            'correct': is_correct,
            'explanation': explanation,
            'points_earned': points
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/next/<topic_id>', methods=['GET'])
@require_auth
def get_next_question(topic_id):
    """Get next adaptive question"""
    try:
        next_q = QuizService.get_next_question(request.user_id, topic_id)
        
        return jsonify(next_q), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/statistics/<topic_id>', methods=['GET'])
@require_auth
def get_quiz_stats(topic_id):
    """Get quiz statistics for topic"""
    try:
        stats = QuizService.get_topic_statistics(request.user_id, topic_id)
        return jsonify(stats), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ======================== PROGRESS ROUTES ========================

@progress_bp.route('/dashboard', methods=['GET'])
@require_auth
def get_dashboard():
    """Get user dashboard"""
    try:
        dashboard = ProgressService.get_user_dashboard(request.user_id)
        
        if not dashboard:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(dashboard), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ======================== RECOMMENDATION ROUTES ========================

@recommendation_bp.route('', methods=['GET'])
@require_auth
def get_recommendations():
    """Get personalized recommendations"""
    try:
        recommendations = RecommendationService.get_recommendations(request.user_id)
        return jsonify(recommendations), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def register_routes(app):
    """Register all blueprints with Flask app"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(topics_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(recommendation_bp)
