## API Documentation

### Base URL

```
http://localhost:5000/api
```

### Authentication

All endpoints except `/auth/register` and `/auth/login` require JWT token in header:

```
Authorization: Bearer <token>
```

---

## 1. Authentication Endpoints

### Register User

**POST** `/auth/register`

Creates a new user account.

**Request:**

```json
{
  "email": "user@example.com",
  "username": "learner123",
  "password": "SecurePass123"
}
```

**Response (201):**

```json
{
  "message": "Registration successful",
  "user_id": "507f1f77bcf86cd799439011"
}
```

**Errors:**

- 400: Invalid email format
- 400: Username must be 3-20 chars
- 400: Password too weak
- 400: Email already registered

---

### Login User

**POST** `/auth/login`

Authenticates user and returns JWT token.

**Request:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**

```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "username": "learner123",
    "total_points": 150,
    "current_level": "Intermediate"
  }
}
```

**Errors:**

- 401: Invalid credentials

---

### Get User Profile

**GET** `/auth/profile` ⚠️ Requires Auth

Returns authenticated user's profile information.

**Response (200):**

```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "username": "learner123",
  "total_points": 350,
  "current_level": "Intermediate",
  "topics_completed": ["507f1f77bcf86cd799439012"],
  "created_at": "2024-05-04T10:00:00Z"
}
```

---

## 2. Topics Endpoints

### Get All Topics

**GET** `/topics` ⚠️ Requires Auth

Retrieves all available learning topics.

**Query Parameters:**

- None

**Response (200):**

```json
{
  "topics": [
    {
      "topic_id": "507f1f77bcf86cd799439012",
      "name": "Python Basics",
      "description": "Learn fundamental Python programming",
      "difficulty": "Beginner",
      "category": "Programming"
    },
    {
      "topic_id": "507f1f77bcf86cd799439013",
      "name": "Object-Oriented Programming",
      "description": "Understand classes, inheritance, polymorphism",
      "difficulty": "Intermediate",
      "category": "Programming"
    }
  ]
}
```

---

### Get Topic Details

**GET** `/topics/<topic_id>` ⚠️ Requires Auth

Retrieves detailed information about a specific topic.

**Path Parameters:**

- `topic_id` (string, required): MongoDB ObjectId of the topic

**Response (200):**

```json
{
  "topic_id": "507f1f77bcf86cd799439012",
  "name": "Python Basics",
  "description": "Learn fundamental Python programming",
  "difficulty": "Beginner",
  "category": "Programming",
  "content": "# Python Basics\n- Variables and data types\n- Operators and expressions\n- ..."
}
```

**Errors:**

- 404: Topic not found

---

## 3. Quiz Endpoints

### Get Quiz Questions

**GET** `/quiz/questions/<topic_id>` ⚠️ Requires Auth

Retrieves questions for a specific topic.

**Path Parameters:**

- `topic_id` (string, required): MongoDB ObjectId of the topic

**Query Parameters:**

- `difficulty` (string, optional): "Beginner", "Intermediate", or "Advanced"
- `limit` (integer, optional, default=5): Number of questions to return

**Response (200):**

```json
{
  "questions": [
    {
      "question_id": "507f1f77bcf86cd799439014",
      "text": "What is the correct way to declare a variable?",
      "options": ["var x = 5", "x = 5", "declare x = 5", "variable x = 5"],
      "difficulty": "Beginner"
    }
  ]
}
```

**Errors:**

- 404: No questions found

---

### Submit Answer

**POST** `/quiz/submit` ⚠️ Requires Auth

Submits a quiz answer and returns correctness with explanation.

**Request:**

```json
{
  "question_id": "507f1f77bcf86cd799439014",
  "selected_answer": "x = 5",
  "time_spent": 45
}
```

**Response (200):**

```json
{
  "correct": true,
  "explanation": "Python uses simple assignment syntax without keywords.",
  "points_earned": 10
}
```

**Errors:**

- 400: Missing required fields
- 404: Question not found

---

### Get Next Adaptive Question

**GET** `/quiz/next/<topic_id>` ⚠️ Requires Auth

Gets the next question with difficulty adjusted based on current performance.

**Path Parameters:**

- `topic_id` (string, required): MongoDB ObjectId of the topic

**Response (200):**

```json
{
  "question": {
    "question_id": "507f1f77bcf86cd799439014",
    "text": "What is the correct way to declare a variable?",
    "options": ["option1", "option2", "option3", "option4"],
    "difficulty": "Beginner"
  },
  "current_difficulty": "Beginner",
  "stats": {
    "accuracy": 85.0,
    "avg_time": 38.5,
    "questions_answered": 12,
    "correct_answers": 10
  }
}
```

---

### Get Quiz Statistics

**GET** `/quiz/statistics/<topic_id>` ⚠️ Requires Auth

Returns user's performance statistics for a specific topic.

**Path Parameters:**

- `topic_id` (string, required): MongoDB ObjectId of the topic

**Response (200):**

```json
{
  "accuracy": 85.0,
  "avg_time": 38.5,
  "questions_answered": 12,
  "correct_answers": 10
}
```

---

## 4. Progress Endpoints

### Get User Dashboard

**GET** `/progress/dashboard` ⚠️ Requires Auth

Retrieves comprehensive dashboard data including stats, insights, and progress.

**Response (200):**

```json
{
  "user": {
    "username": "learner123",
    "total_points": 350,
    "current_level": "Intermediate"
  },
  "statistics": {
    "topics_studied": 5,
    "average_accuracy": 82.5,
    "total_time_spent": 245.5,
    "total_questions_answered": 87
  },
  "insights": {
    "weak_topics": [
      {
        "topic_id": "507f1f77bcf86cd799439012",
        "accuracy": 0.65
      }
    ],
    "strong_topics": [
      {
        "topic_id": "507f1f77bcf86cd799439013",
        "accuracy": 0.92
      }
    ],
    "improvement_trend": "Improving",
    "recommended_focus": "Focus on weak topics",
    "overall_accuracy": 82.5,
    "total_questions": 87
  },
  "progress_by_topic": [
    {
      "topic_id": "507f1f77bcf86cd799439012",
      "accuracy": 85.0,
      "questions_answered": 12
    }
  ]
}
```

---

## 5. Recommendation Endpoints

### Get Personalized Recommendations

**GET** `/recommendations` ⚠️ Requires Auth

Returns AI-generated topic recommendations based on user performance.

**Response (200):**

```json
{
  "recommendations": [
    {
      "topic_id": "507f1f77bcf86cd799439015",
      "topic_name": "Object-Oriented Programming",
      "difficulty": "Intermediate",
      "score": 0.85,
      "reason": "Needs improvement"
    },
    {
      "topic_id": "507f1f77bcf86cd799439016",
      "topic_name": "Data Structures",
      "difficulty": "Intermediate",
      "score": 0.72,
      "reason": "Keep practicing"
    },
    {
      "topic_id": "507f1f77bcf86cd799439017",
      "topic_name": "Advanced Python",
      "difficulty": "Advanced",
      "score": 0.68,
      "reason": "Ready for next level"
    }
  ],
  "generated_at": "2024-05-04T15:30:00Z"
}
```

---

## 6. Health Check Endpoint

### Health Check

**GET** `/health`

Simple health check endpoint (no auth required).

**Response (200):**

```json
{
  "status": "healthy"
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "error": "Error description"
}
```

### Common HTTP Status Codes

| Code | Meaning                      |
| ---- | ---------------------------- |
| 200  | Success                      |
| 201  | Created                      |
| 400  | Bad Request                  |
| 401  | Unauthorized (invalid token) |
| 404  | Not Found                    |
| 500  | Server Error                 |

---

## Rate Limiting

Currently no rate limiting implemented. For production, consider:

- Flask-Limiter extension
- 100 requests per minute per IP
- 1000 requests per hour per user

---

## CORS Policy

Frontend and backend can run on different domains. CORS is enabled for:

- Origins: `*` (all domains)
- Methods: GET, POST, PUT, DELETE, OPTIONS
- Headers: Content-Type, Authorization

For production, restrict to specific domains:

```python
CORS(app, resources={
    r"/api/*": {"origins": ["https://yourdomain.com"]}
})
```

---

## JWT Token Details

**Token Type:** HS256

**Claims:**

```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "exp": 1715000000,
  "iat": 1712408000
}
```

**Expiration:** 30 days

**Validation:**

- Check signature with JWT_SECRET
- Check expiration time
- Reject expired tokens with 401 status

---

## Response Time Targets

| Endpoint            | Target (ms) |
| ------------------- | ----------- |
| Login               | < 200       |
| Get Topics          | < 100       |
| Submit Answer       | < 150       |
| Get Dashboard       | < 300       |
| Get Recommendations | < 250       |

---

## Testing with cURL

### Register

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "username": "testuser", "password": "TestPass123"}'
```

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@learnai.com", "password": "TestPass123"}'
```

### Get Topics

```bash
curl -X GET http://localhost:5000/api/topics \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Submit Answer

```bash
curl -X POST http://localhost:5000/api/quiz/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"question_id": "507f1f77bcf86cd799439014", "selected_answer": "x = 5", "time_spent": 45}'
```
