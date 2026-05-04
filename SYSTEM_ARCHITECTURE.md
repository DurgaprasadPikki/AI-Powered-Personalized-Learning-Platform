# System Architecture & Design

## 🏗️ Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                                 │
│  HTML5 + CSS3 + Vanilla JavaScript (SPA)                             │
│  • Login/Register Page                                               │
│  • Dashboard with Analytics                                          │
│  • Topic Browsing                                                    │
│  • Interactive Quiz Engine                                           │
│  • Progress Tracking                                                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                      (Fetch API over HTTPS)
                      Authorization: Bearer <JWT>
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                    FLASK REST API LAYER                              │
│                   (localhost:5000)                                   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Route Layer (api_routes.py)                                   │  │
│  │ • /auth/register         (POST)                               │  │
│  │ • /auth/login            (POST)                               │  │
│  │ • /auth/profile          (GET)                                │  │
│  │ • /topics                (GET)                                │  │
│  │ • /topics/<id>           (GET)                                │  │
│  │ • /quiz/questions/<id>   (GET)                                │  │
│  │ • /quiz/submit           (POST)                               │  │
│  │ • /quiz/next/<id>        (GET)                                │  │
│  │ • /quiz/statistics/<id>  (GET)                                │  │
│  │ • /progress/dashboard    (GET)                                │  │
│  │ • /recommendations       (GET)                                │  │
│  │ • /health                (GET)                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                               │                                      │
│                               ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Service Layer (business_logic.py)                             │  │
│  │ • AuthService              (User authentication)               │  │
│  │ • TopicService             (Topic management)                  │  │
│  │ • QuizService              (Quiz operations)                   │  │
│  │ • ProgressService          (Performance tracking)              │  │
│  │ • RecommendationService    (Smart recommendations)             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                               │                                      │
│                               ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ ML Engine (recommendation.py)                                 │  │
│  │ • FeatureExtractor                                            │  │
│  │   - Extract: accuracy, time, recency, consistency             │  │
│  │ • RecommendationEngine                                        │  │
│  │   - Hybrid scoring algorithm                                  │  │
│  │   - Top-N recommendations                                     │  │
│  │ • AdaptiveQuizEngine                                          │  │
│  │   - Difficulty adjustment                                     │  │
│  │   - Performance-based progression                             │  │
│  │ • InsightGenerator                                            │  │
│  │   - Weakness/strength identification                          │  │
│  │   - Trend analysis                                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                               │                                      │
│                               ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Model Layer (data_models.py)                                  │  │
│  │ • UserModel                                                   │  │
│  │ • TopicModel                                                  │  │
│  │ • QuestionModel                                               │  │
│  │ • QuizAttemptModel                                            │  │
│  │ • ProgressModel                                               │  │
│  │ • RecommendationModel                                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                               │                                      │
│                               ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Utilities                                                      │  │
│  │ • JWTHandler (Token creation/verification)                    │  │
│  │ • PasswordHandler (Bcrypt hashing)                            │  │
│  │ • InputValidator (Email/Username/Password validation)         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                      (PyMongo Driver)
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                      MONGODB DATABASE                                │
│                 (localhost:27017 / MongoDB Atlas)                    │
│                                                                      │
│  Collections:                                                        │
│  • users           - User accounts & profiles                        │
│  • topics          - Learning topics (8 topics)                      │
│  • questions       - Quiz questions (17 questions)                   │
│  • quiz_attempts   - Quiz results (user generated)                   │
│  • user_progress   - Aggregated performance stats                    │
│  • recommendations - Cached recommendations                          │
│                                                                      │
│  Indexes:                                                            │
│  • users.email (unique)                                              │
│  • topics.difficulty, .category                                      │
│  • questions.topic_id                                                │
│  • quiz_attempts.user_id + timestamp                                 │
│  • user_progress.user_id + topic_id (unique)                         │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagrams

### 1. User Registration Flow

```
┌─────────────────┐
│ User Register   │
└────────┬────────┘
         │ Email, Username, Password
         ▼
┌─────────────────────────────┐
│ InputValidator              │
│ • Email format ✓            │
│ • Username length ✓         │
│ • Password strength ✓       │
└────────┬────────────────────┘
         │ Valid
         ▼
┌─────────────────────────────┐
│ PasswordHandler             │
│ • Hash with Bcrypt (12)     │
│ • Salt generation           │
└────────┬────────────────────┘
         │ Password Hash
         ▼
┌─────────────────────────────┐
│ UserModel.create_user()     │
│ Insert into MongoDB users   │
└────────┬────────────────────┘
         │ user_id
         ▼
┌─────────────────────────────┐
│ Return Success + user_id    │
└─────────────────────────────┘
```

### 2. Login & Authentication Flow

```
┌─────────────────┐
│ User Login      │
└────────┬────────┘
         │ Email, Password
         ▼
┌─────────────────────────────┐
│ UserModel.get_user_by_email │
│ Query MongoDB users         │
└────────┬────────────────────┘
         │ User Document
         ▼
┌─────────────────────────────┐
│ PasswordHandler             │
│ • Verify password hash      │
│ • Compare with stored hash  │
└────────┬────────────────────┘
         │ Valid
         ▼
┌─────────────────────────────┐
│ JWTHandler.create_token()   │
│ • User ID in payload        │
│ • 30-day expiration         │
│ • Sign with JWT_SECRET      │
└────────┬────────────────────┘
         │ JWT Token
         ▼
┌─────────────────────────────┐
│ Return Token + User Data    │
└──────────┬──────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Store in Browser             │
│ localStorage.auth_token      │
└──────────────────────────────┘
```

### 3. Quiz Submission & Adaptive Difficulty

```
┌──────────────────────┐
│ User Answers Question│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────┐
│ QuizService.submit_answer()      │
│ • Get question from DB           │
│ • Compare answer                 │
│ • Calculate points               │
└──────────┬───────────────────────┘
           │ is_correct, points
           ▼
┌──────────────────────────────────┐
│ QuizAttemptModel.record_attempt()│
│ • Insert into quiz_attempts      │
│ • Store: question, answer, time  │
└──────────┬───────────────────────┘
           │ attempts recorded
           ▼
┌──────────────────────────────────┐
│ Calculate Statistics             │
│ • Accuracy = correct/total       │
│ • Avg Time = sum(time)/count     │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ AdaptiveQuizEngine               │
│ • Compare accuracy to threshold  │
│ • IF accuracy >= 75%             │
│    → INCREASE difficulty         │
│ • ELSE IF accuracy < 50%         │
│    → DECREASE difficulty         │
│ • ELSE → KEEP current            │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ ProgressModel.update_progress()  │
│ • Insert/Update user_progress    │
│ • Store: accuracy, avg_time      │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Return Feedback                  │
│ • Correct/Incorrect              │
│ • Explanation                    │
│ • Points earned                  │
│ • Next difficulty                │
└──────────────────────────────────┘
```

### 4. Recommendation Generation

```
┌──────────────────────────┐
│ User Requests            │
│ Recommendations          │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ RecommendationEngine.get_recommendations
│ → Fetch all topics                   │
│ → Get user progress data             │
└────────┬─────────────────────────────┘
         │ user_id, all_topics
         ▼
┌──────────────────────────────────────┐
│ FeatureExtractor                     │
│ For each topic:                      │
│ • accuracy (0-1)                     │
│ • avg_time (normalized)              │
│ • questions_answered (normalized)    │
│ • recency_score (days_ago)           │
│ • consistency_score (std_dev)        │
│ • time_efficiency (accuracy/time)    │
│ • attempted (boolean)                │
│ • difficulty (numeric)               │
└────────┬─────────────────────────────┘
         │ feature_dict
         ▼
┌──────────────────────────────────────┐
│ _calculate_recommendation_score()    │
│ For each topic:                      │
│                                      │
│ difficulty_score = level_map         │
│ weakness_score = 1 - accuracy        │
│ engagement_score = weighted avg      │
│ attempt_factor = 1 or 0.7            │
│                                      │
│ final = 0.3×diff + 0.3×weak +       │
│         0.2×engage + 0.2×attempt     │
└────────┬─────────────────────────────┘
         │ scored_topics
         ▼
┌──────────────────────────────────────┐
│ Sort by score (descending)           │
│ Return top 3 recommendations         │
└────────┬─────────────────────────────┘
         │ top_3
         ▼
┌──────────────────────────────────────┐
│ RecommendationModel.save()           │
│ Cache in recommendations collection  │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Return to Frontend                   │
│ [topic_name, difficulty, score,      │
│  reason, ...]                        │
└──────────────────────────────────────┘
```

---

## 🔐 Security Architecture

```
┌────────────────────────────────────────────────────────┐
│                  SECURITY LAYERS                       │
└────────────────────────────────────────────────────────┘

Layer 1: Input Validation (Client & Server)
├── Email format validation
├── Username alphanumeric check
├── Password strength requirements
└── Data type validation

Layer 2: Authentication
├── Bcrypt hashing (12 rounds)
│  └── Never store plaintext passwords
├── JWT token generation
│  └── 30-day expiration
└── Bearer token validation
   └── On every protected request

Layer 3: API Security
├── CORS configuration
│  └── Restrict to frontend origin
├── Error handling
│  └── No sensitive data exposure
└── Rate limiting
   └── (Optional: Flask-Limiter)

Layer 4: Data Protection
├── MongoDB indexes for queries
├── Connection pooling
├── Secure error messages
└── Audit trail (timestamps)

Layer 5: HTTPS/SSL (Production)
├── SSL certificate
├── Redirect HTTP → HTTPS
└── Security headers
   └── X-Content-Type-Options: nosniff
   └── X-Frame-Options: DENY
   └── X-XSS-Protection: 1; mode=block
```

---

## 📊 Scalability Architecture

```
Current Single-Instance Setup:
┌────────────┐
│  Browser   │
└─────┬──────┘
      │
┌─────▼───────────────┐
│  Flask (1 process)  │
└─────┬───────────────┘
      │
┌─────▼─────────────────┐
│  MongoDB (Local)      │
└───────────────────────┘


Scalable Multi-Instance Setup:
┌─────────────────────────────────────────────┐
│          Nginx Reverse Proxy                │
│      (Load Balancer, SSL Termination)       │
└──┬──────────────────────────┬──────────────┘
   │                          │
┌──▼──────────┐       ┌──────▼──────┐
│ Flask App 1 │       │ Flask App N  │
│ (Gunicorn)  │ _____ │ (Gunicorn)   │
└──┬──────────┘       └──────┬──────┘
   │                         │
   │  ┌──────────────────────┘
   │  │
┌──▼──▼──────────────────────────────┐
│     Redis Cache                    │
│   (Frequent queries)               │
└──┬───────────────────────────────┬─┘
   │                               │
┌──▼─────────────────────────────┐ │
│   MongoDB Replica Set          │ │
│   (Sharded for large datasets) │ │
└────────────────────────────────┘ │
                                    │
┌──────────────────────────────────┘
│
▼
CDN (Static Assets)
```

---

## 🎯 Request/Response Cycle

```
1. USER BROWSER SENDS REQUEST
   ├── Method: GET/POST
   ├── URL: /api/endpoint
   ├── Headers:
   │  ├── Content-Type: application/json
   │  └── Authorization: Bearer JWT_TOKEN
   └── Body: JSON data (if POST/PUT)

2. FLASK ROUTE HANDLER
   ├── Parse request
   ├── Validate token
   ├── Extract user_id
   └── Call service layer

3. SERVICE LAYER
   ├── Implement business logic
   ├── Call model layer
   ├── Call ML engine if needed
   └── Return structured response

4. MODEL LAYER
   ├── Query MongoDB
   ├── Transform data
   └── Return results

5. SERVICE AGGREGATES RESPONSE
   ├── Combine data
   ├── Format response
   └── Return to route

6. ROUTE RETURNS JSON
   ├── Status code (200, 201, 400, 401, 404, 500)
   └── Body: JSON response

7. BROWSER RECEIVES RESPONSE
   ├── Parse JSON
   ├── Update UI
   ├── Show result to user
   └── Store data if needed
```

---

## 🗄️ Database Relationship Diagram

```
┌─────────────────┐
│     USERS       │
├─────────────────┤
│ _id (PK)        │
│ email (UNIQUE)  │
│ username        │
│ password_hash   │
│ total_points    │
│ current_level   │
│ created_at      │
└────────┬────────┘
         │
         │ (1:N) creates
         │
         ├────────────────────────────────┬──────────────────────────┐
         │                                │                          │
         ▼                                ▼                          ▼
    ┌──────────────────┐        ┌──────────────────┐      ┌──────────────────┐
    │  QUIZ_ATTEMPTS   │        │  USER_PROGRESS   │      │ RECOMMENDATIONS  │
    ├──────────────────┤        ├──────────────────┤      ├──────────────────┤
    │ _id (PK)         │        │ _id (PK)         │      │ _id (PK)         │
    │ user_id (FK)     │        │ user_id (FK)     │      │ user_id (FK)     │
    │ question_id (FK) │        │ topic_id (FK)    │      │ topics[] array   │
    │ is_correct       │        │ accuracy         │      │ generated_at     │
    │ time_spent       │        │ avg_time         │      └──────────────────┘
    │ timestamp        │        │ questions_ans.   │
    └────────┬─────────┘        │ updated_at       │
             │                  └────────┬─────────┘
             │                          │
             │ (N:1) references         │ (N:1) references
             │                          │
             ▼                          ▼
        ┌──────────────┐            ┌──────────────┐
        │  QUESTIONS   │◄──────────►│   TOPICS     │
        ├──────────────┤  (N:1)     ├──────────────┤
        │ _id (PK)     │            │ _id (PK)     │
        │ topic_id (FK)│            │ name         │
        │ text         │            │ difficulty   │
        │ options[]    │            │ category     │
        │ correct_ans. │            │ content      │
        │ explanation  │            │ order        │
        └──────────────┘            └──────────────┘

Relationships:
• users (1) ──→ (N) quiz_attempts
• users (1) ──→ (N) user_progress
• users (1) ──→ (1) recommendations
• topics (1) ──→ (N) questions
• topics (1) ──→ (N) user_progress
• questions (1) ──→ (N) quiz_attempts
```

---

## 🔄 State Management

### Frontend State

```
app = {
  currentUser: {
    user_id: string,
    email: string,
    username: string,
    total_points: number,
    current_level: string
  },

  currentTopic: {
    topic_id: string,
    name: string,
    difficulty: string,
    content: string
  },

  currentQuiz: {
    topicId: string,
    questions: Array,
    currentQuestionIndex: number,
    answers: Array,
    correctCount: number,
    startTime: number
  },

  charts: {
    performance: Chart,
    trend: Chart
  }
}
```

### Backend State

```
Request Context:
request.user_id = "extracted from JWT"

Database Sessions:
MongoDB Connection (singleton)
  → Maintained across requests
  → Connection pooling

Token Validation:
JWT Payload = {
  user_id: string,
  exp: timestamp,
  iat: timestamp
}
```

---

## ⚡ Performance Optimization Points

```
Database Level:
├── Indexing on frequently queried fields
├── Connection pooling
├── Batch inserts for sample data
└── Aggregate queries for stats

API Level:
├── Minimize response payload
├── Cache recommendations (30 min)
├── Cache topics (1 hour)
└── Pagination for large datasets

Frontend Level:
├── LocalStorage for token
├── CSS minification (production)
├── JS minification (production)
├── Lazy loading of charts
└── Efficient DOM updates

Infrastructure Level:
├── Gunicorn with multiple workers
├── Nginx caching headers
├── Gzip compression
├── CDN for static assets
└── Database read replicas
```

---

All systems work together to create a **scalable, secure, and intelligent learning platform!** 🎓🚀
