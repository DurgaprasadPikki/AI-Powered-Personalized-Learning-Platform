# 🧠 AI-Powered Personalized Learning Platform

A production-ready intelligent learning system that dynamically adapts content based on user performance and learning behavior.

## 🎯 Features

✅ **User Authentication**

- Secure registration and login with bcrypt password hashing
- JWT-based authentication
- Session management

✅ **Personalized Dashboard**

- Real-time progress tracking
- Performance analytics with Chart.js visualizations
- Learning insights and recommendations

✅ **Adaptive Learning Module**

- Topics organized by difficulty (Beginner → Intermediate → Advanced)
- Dynamic quiz difficulty adjustment based on performance
- Smart question selection algorithm

✅ **AI Recommendation Engine**

- Analyzes user performance data
- Extracts features: accuracy, time spent, consistency
- Recommends next best topics for learning
- Hybrid scoring system combining multiple signals

✅ **Progress Tracking**

- Quiz history and scoring
- Topic-wise accuracy tracking
- Performance trends and insights
- Weak/strong area identification

## 🏗️ Tech Stack

**Frontend:**

- HTML5, CSS3, Vanilla JavaScript
- Chart.js for visualizations
- Fetch API for backend communication
- LocalStorage for token management

**Backend:**

- Python Flask (REST API)
- PyMongo for MongoDB integration
- Scikit-learn for ML features
- JWT for authentication
- Bcrypt for password hashing

**Database:**

- MongoDB with PyMongo
- Collections: users, topics, questions, quiz_attempts, user_progress, recommendations

**ML/AI:**

- Feature extraction from user behavior
- Recommendation scoring algorithm
- Adaptive difficulty adjustment
- Performance analytics engine

## 📁 Project Structure

```
.
├── backend/
│   ├── config/
│   │   ├── settings.py          # Configuration management
│   │   ├── database.py          # MongoDB connection
│   │   └── __init__.py
│   ├── models/
│   │   ├── data_models.py       # MongoDB models/schemas
│   │   └── __init__.py
│   ├── services/
│   │   ├── business_logic.py    # Business logic layer
│   │   └── __init__.py
│   ├── routes/
│   │   ├── api_routes.py        # REST API endpoints
│   │   └── __init__.py
│   ├── ml_engine/
│   │   ├── recommendation.py    # ML recommendation system
│   │   └── __init__.py
│   ├── utils/
│   │   ├── auth.py              # JWT & password utilities
│   │   └── __init__.py
│   ├── app.py                   # Flask application factory
│   ├── setup_db.py              # Database initialization script
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Environment variables
│
└── frontend/
    ├── index.html               # Main entry point
    ├── static/
    │   ├── css/
    │   │   └── styles.css       # Complete styling
    │   └── js/
    │       ├── api.js           # API client
    │       └── app.js           # Application logic
    └── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MongoDB (running on localhost:27017)
- Node.js (optional, for serving frontend)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (already provided)
# Update configuration if needed

# Initialize database with sample data
python setup_db.py

# Run Flask server
python app.py
```

The backend will start at **http://localhost:5000**

### 2. Frontend Access

Simply navigate to:

```
http://localhost:5000
```

The frontend is served by Flask directly.

### 3. Test Login

Use the sample user credentials created during setup:

```
Email: user@learnai.com
Password: TestPass123
```

## 📊 MongoDB Collections Schema

### users

```json
{
  "_id": ObjectId,
  "email": "user@example.com",
  "username": "learner",
  "password_hash": "hashed_password",
  "created_at": ISODate,
  "updated_at": ISODate,
  "total_points": 150,
  "topics_completed": [],
  "current_level": "Beginner"
}
```

### topics

```json
{
  "_id": ObjectId,
  "name": "Python Basics",
  "description": "Learn fundamental Python programming",
  "category": "Programming",
  "difficulty": "Beginner",
  "content": "Detailed content...",
  "order": 1,
  "prerequisites": [],
  "created_at": ISODate
}
```

### questions

```json
{
  "_id": ObjectId,
  "topic_id": ObjectId,
  "text": "What is Python?",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_answer": "Option A",
  "difficulty": "Beginner",
  "explanation": "Detailed explanation...",
  "created_at": ISODate
}
```

### quiz_attempts

```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "question_id": ObjectId,
  "topic_id": ObjectId,
  "selected_answer": "User's answer",
  "is_correct": true,
  "time_spent": 45,
  "timestamp": ISODate
}
```

### user_progress

```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "topic_id": ObjectId,
  "accuracy": 0.85,
  "avg_time": 45.5,
  "questions_answered": 12,
  "updated_at": ISODate
}
```

## 🔌 REST API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get user profile (requires auth)

### Topics

- `GET /api/topics` - Get all topics (requires auth)
- `GET /api/topics/<topic_id>` - Get topic details (requires auth)

### Quiz

- `GET /api/quiz/questions/<topic_id>` - Get quiz questions (requires auth)
- `POST /api/quiz/submit` - Submit answer (requires auth)
- `GET /api/quiz/next/<topic_id>` - Get next adaptive question (requires auth)
- `GET /api/quiz/statistics/<topic_id>` - Get topic statistics (requires auth)

### Progress

- `GET /api/progress/dashboard` - Get user dashboard (requires auth)

### Recommendations

- `GET /api/recommendations` - Get personalized recommendations (requires auth)

## 🤖 ML Recommendation Engine

### Algorithm Overview

1. **Feature Extraction**
   - Accuracy: Percentage of correct answers
   - Time Efficiency: Speed vs accuracy ratio
   - Recency Score: Weight recent attempts higher
   - Consistency Score: Stability of performance
   - Attempt Status: Whether topic was attempted

2. **Scoring Function**

   ```
   Score = (0.3 × DifficultyScore) +
           (0.3 × WeaknessScore) +
           (0.2 × EngagementScore) +
           (0.2 × AttemptFactor)
   ```

3. **Adaptive Difficulty**
   - **Beginner → Intermediate**: If accuracy ≥ 75%
   - **Intermediate → Advanced**: If accuracy ≥ 75%
   - **Decrease**: If accuracy < 50%

### Example Recommendation Output

```json
{
  "recommendations": [
    {
      "topic_id": "507f1f77bcf86cd799439011",
      "topic_name": "Object-Oriented Programming",
      "difficulty": "Intermediate",
      "score": 0.845,
      "reason": "Needs improvement"
    },
    {
      "topic_id": "507f1f77bcf86cd799439012",
      "topic_name": "Data Structures",
      "difficulty": "Intermediate",
      "score": 0.712,
      "reason": "Keep practicing"
    }
  ],
  "generated_at": "2024-05-04T10:30:00Z"
}
```

## 🔐 Security Features

✅ **Password Security**

- Bcrypt hashing with 12 rounds
- Minimum requirements: 8 chars, uppercase, digit

✅ **API Security**

- JWT token-based authentication
- 30-day token expiration
- Bearer token in Authorization header

✅ **Input Validation**

- Email format validation
- Username validation (3-20 chars, alphanumeric)
- CORS enabled for secure cross-origin requests

✅ **Data Protection**

- Password hashes never exposed
- Sensitive data excluded from API responses

## 📈 Performance Metrics

The platform tracks and displays:

- **Overall Accuracy**: Percentage of correct answers across all topics
- **Average Time**: Time spent per question
- **Improvement Trend**: Comparing recent vs previous performance
- **Weak/Strong Areas**: Topics needing improvement vs mastered topics
- **Topic Progress**: Accuracy and question count per topic

## 🧪 Testing the System

### 1. Register New User

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@learnai.com",
    "password": "TestPass123"
  }'
```

### 3. Get Topics

```bash
curl -X GET http://localhost:5000/api/topics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Get Recommendations

```bash
curl -X GET http://localhost:5000/api/recommendations \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🎓 Learning Path

The platform recommends a learning progression:

```
Python Basics → Data Structures → OOP → Advanced Python
     ↓              ↓
Web Dev Basics → JavaScript → Advanced JS
     ↓
Database Design → Machine Learning
```

## 📝 Sample Data

The `setup_db.py` script creates:

- **8 Topics** across 4 categories
- **17 Questions** with varying difficulty levels
- **1 Sample User** with progress data
- **2 Progress Records** showing topic engagement

## 🔄 Development Workflow

1. **Backend Changes**: Edit Python files in `/backend`
2. **Restart Server**: Kill and restart Flask
3. **Frontend Changes**: Edit HTML/CSS/JS files
4. **Reload Browser**: Changes appear immediately

## 📊 Database Maintenance

### View All Topics

```python
db.topics.find()
```

### View User Progress

```python
db.user_progress.find({"user_id": ObjectId("...")})
```

### View Quiz Attempts

```python
db.quiz_attempts.find({"user_id": ObjectId("...")})
```

## 🐛 Troubleshooting

**MongoDB Connection Error**

- Ensure MongoDB is running: `mongod`
- Check connection string in `.env`

**JWT Token Errors**

- Clear browser localStorage
- Re-login to get new token

**CORS Issues**

- Flask-CORS is configured
- Check browser console for details

**Port Already in Use**

- Change port in `app.py`: `app.run(port=5001)`

## 📚 Further Enhancements

- [ ] Email verification for registration
- [ ] Password reset functionality
- [ ] User achievements and badges
- [ ] Social learning features
- [ ] Mobile app version
- [ ] Advanced analytics dashboard
- [ ] Spaced repetition algorithm
- [ ] Video content support
- [ ] Peer discussion forum
- [ ] Certificate generation

## 📄 License

This project is provided as-is for educational purposes.

## 💡 Support

For issues or questions, refer to the inline code comments and API documentation above.

---

**Built with ❤️ for personalized learning through AI**
