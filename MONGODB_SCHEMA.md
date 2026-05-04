## MongoDB Collections Design

### users

Stores user account information and learning progress tracking.

```javascript
db.createCollection("users")
db.users.createIndex({ email: 1 }, { unique: true })

// Example document:
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "email": "user@example.com",
  "username": "learner123",
  "password_hash": "$2b$12$...",
  "created_at": ISODate("2024-05-04T10:00:00Z"),
  "updated_at": ISODate("2024-05-04T15:30:00Z"),
  "total_points": 350,
  "topics_completed": [
    "507f1f77bcf86cd799439012",
    "507f1f77bcf86cd799439013"
  ],
  "current_level": "Intermediate"
}
```

### topics

Contains learning topics organized by difficulty and category.

```javascript
db.createCollection("topics")
db.topics.createIndex({ difficulty: 1 })
db.topics.createIndex({ category: 1 })

// Example document:
{
  "_id": ObjectId("507f1f77bcf86cd799439012"),
  "name": "Python Basics",
  "description": "Learn fundamental Python programming concepts",
  "category": "Programming",
  "difficulty": "Beginner",
  "content": "# Python Basics\n- Variables and data types\n- ...",
  "order": 1,
  "prerequisites": [],
  "created_at": ISODate("2024-05-04T10:00:00Z")
}
```

### questions

Quiz questions linked to topics with metadata.

```javascript
db.createCollection("questions")
db.questions.createIndex({ topic_id: 1 })
db.questions.createIndex({ difficulty: 1 })

// Example document:
{
  "_id": ObjectId("507f1f77bcf86cd799439014"),
  "topic_id": ObjectId("507f1f77bcf86cd799439012"),
  "text": "What is the correct way to declare a variable in Python?",
  "options": [
    "var x = 5",
    "x = 5",
    "declare x = 5",
    "variable x = 5"
  ],
  "correct_answer": "x = 5",
  "difficulty": "Beginner",
  "explanation": "Python uses simple assignment syntax without keywords.",
  "created_at": ISODate("2024-05-04T10:00:00Z")
}
```

### quiz_attempts

Records every quiz attempt for performance tracking.

```javascript
db.createCollection("quiz_attempts")
db.quiz_attempts.createIndex({ user_id: 1, timestamp: -1 })
db.quiz_attempts.createIndex({ topic_id: 1 })

// Example document:
{
  "_id": ObjectId("507f1f77bcf86cd799439015"),
  "user_id": ObjectId("507f1f77bcf86cd799439011"),
  "question_id": ObjectId("507f1f77bcf86cd799439014"),
  "topic_id": ObjectId("507f1f77bcf86cd799439012"),
  "selected_answer": "x = 5",
  "is_correct": true,
  "time_spent": 35,
  "timestamp": ISODate("2024-05-04T14:25:00Z")
}
```

### user_progress

Aggregated progress data per user per topic (for fast queries).

```javascript
db.createCollection("user_progress")
db.user_progress.createIndex({ user_id: 1, topic_id: 1 }, { unique: true })

// Example document:
{
  "_id": ObjectId("507f1f77bcf86cd799439016"),
  "user_id": ObjectId("507f1f77bcf86cd799439011"),
  "topic_id": ObjectId("507f1f77bcf86cd799439012"),
  "accuracy": 0.85,
  "avg_time": 38.5,
  "questions_answered": 15,
  "current_difficulty": "Intermediate",
  "updated_at": ISODate("2024-05-04T15:30:00Z")
}
```

### recommendations

Caches latest recommendations for users.

```javascript
db.createCollection("recommendations")
db.recommendations.createIndex({ user_id: 1 }, { unique: true })

// Example document:
{
  "_id": ObjectId("507f1f77bcf86cd799439017"),
  "user_id": ObjectId("507f1f77bcf86cd799439011"),
  "recommended_topics": [
    {
      "topic_id": "507f1f77bcf86cd799439018",
      "topic_name": "Object-Oriented Programming",
      "difficulty": "Intermediate",
      "score": 0.85,
      "reason": "Needs improvement"
    },
    {
      "topic_id": "507f1f77bcf86cd799439019",
      "topic_name": "Data Structures",
      "difficulty": "Intermediate",
      "score": 0.72,
      "reason": "Keep practicing"
    }
  ],
  "generated_at": ISODate("2024-05-04T15:30:00Z")
}
```

## Relationships

```
users (1) ──── (M) topics
  |
  ├─── (M) questions
  |
  ├─── (M) quiz_attempts
  |
  ├─── (M) user_progress ──── (1) topics
  |
  └─── (1) recommendations
```

## Key Indexes

| Collection      | Index                         | Purpose                 |
| --------------- | ----------------------------- | ----------------------- |
| users           | { email: 1 }                  | Fast login lookups      |
| topics          | { difficulty: 1 }             | Filter by level         |
| questions       | { topic_id: 1 }               | Get questions for topic |
| quiz_attempts   | { user_id: 1, timestamp: -1 } | User quiz history       |
| user_progress   | { user_id: 1, topic_id: 1 }   | Fast progress lookup    |
| recommendations | { user_id: 1 }                | Cache recommendations   |

## Sample Query Patterns

### Get user's recent quiz attempts

```javascript
db.quiz_attempts
  .find({
    user_id: ObjectId("..."),
    timestamp: { $gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) },
  })
  .sort({ timestamp: -1 })
  .limit(20);
```

### Get user's accuracy by topic

```javascript
db.user_progress.aggregate([
  { $match: { user_id: ObjectId("...") } },
  {
    $lookup: {
      from: "topics",
      localField: "topic_id",
      foreignField: "_id",
      as: "topic",
    },
  },
  { $sort: { accuracy: -1 } },
]);
```

### Find users needing help (low accuracy)

```javascript
db.user_progress
  .find({
    accuracy: { $lt: 0.5 },
  })
  .sort({ updated_at: -1 });
```

## Data Integrity Rules

1. **Foreign Key Integrity**
   - topic_id in questions must reference valid topics
   - user_id in quiz_attempts must reference valid users
   - question_id in quiz_attempts must reference valid questions

2. **Unique Constraints**
   - Email must be unique per user
   - One user_progress per user-topic combination

3. **Data Validation**
   - Accuracy values: 0 ≤ accuracy ≤ 1
   - Time spent: > 0 seconds
   - Questions must have exactly 4 options

4. **Audit Trail**
   - All collections have created_at/updated_at timestamps
   - quiz_attempts cannot be deleted (immutable)
