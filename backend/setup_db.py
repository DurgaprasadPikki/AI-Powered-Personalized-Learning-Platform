"""
MongoDB Setup Script - Initialize database with sample data
Run this after starting MongoDB: python setup_db.py
"""
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime
import json

MONGO_URI = 'mongodb://localhost:27017/learning_platform'

def setup_database():
    """Initialize database with sample topics, questions, and users"""
    
    client = MongoClient(MONGO_URI)
    db = client.learning_platform
    
    print("🗂️  Setting up Learning Platform Database...")
    
    # Clear existing collections
    for collection in db.list_collection_names():
        db[collection].drop()
    print("✓ Cleared existing collections")
    
    # ==================== TOPICS ====================
    topics = [
        {
            'name': 'Python Basics',
            'description': 'Learn fundamental Python programming concepts',
            'category': 'Programming',
            'difficulty': 'Beginner',
            'content': '# Python Basics\n- Variables and data types\n- Operators and expressions\n- Control flow (if/else)\n- Loops and iterations\n- Functions and scope',
            'order': 1,
            'prerequisites': []
        },
        {
            'name': 'Data Structures',
            'description': 'Master lists, dictionaries, sets, and tuples',
            'category': 'Programming',
            'difficulty': 'Beginner',
            'content': '# Data Structures\n- Lists: creation, indexing, slicing\n- Dictionaries: key-value pairs\n- Sets: unique elements\n- Tuples: immutable sequences\n- Common operations and methods',
            'order': 2,
            'prerequisites': []
        },
        {
            'name': 'Object-Oriented Programming',
            'description': 'Understand classes, inheritance, and polymorphism',
            'category': 'Programming',
            'difficulty': 'Intermediate',
            'content': '# Object-Oriented Programming\n- Classes and objects\n- Instance and class variables\n- Methods and constructors\n- Inheritance and polymorphism\n- Encapsulation and abstraction',
            'order': 3,
            'prerequisites': ['Python Basics']
        },
        {
            'name': 'Web Development Basics',
            'description': 'Introduction to web development with HTML and CSS',
            'category': 'Web',
            'difficulty': 'Beginner',
            'content': '# Web Development Basics\n- HTML structure and semantics\n- CSS styling and layouts\n- Responsive design\n- Flexbox and Grid\n- Best practices',
            'order': 4,
            'prerequisites': []
        },
        {
            'name': 'JavaScript Fundamentals',
            'description': 'Core JavaScript concepts and DOM manipulation',
            'category': 'Web',
            'difficulty': 'Beginner',
            'content': '# JavaScript Fundamentals\n- Variables, types, and operators\n- Functions and scope\n- DOM manipulation\n- Event handling\n- Async and promises',
            'order': 5,
            'prerequisites': []
        },
        {
            'name': 'Advanced Python',
            'description': 'Decorators, generators, context managers, and more',
            'category': 'Programming',
            'difficulty': 'Advanced',
            'content': '# Advanced Python\n- Decorators and closures\n- Generators and iterators\n- Context managers\n- Metaclasses\n- Performance optimization',
            'order': 6,
            'prerequisites': ['Object-Oriented Programming']
        },
        {
            'name': 'Machine Learning',
            'description': 'Introduction to ML concepts and algorithms',
            'category': 'AI/ML',
            'difficulty': 'Advanced',
            'content': '# Machine Learning\n- Supervised vs unsupervised learning\n- Linear regression and classification\n- Decision trees and random forests\n- Clustering algorithms\n- Model evaluation and validation',
            'order': 7,
            'prerequisites': ['Python Basics']
        },
        {
            'name': 'Database Design',
            'description': 'SQL, NoSQL, and database normalization',
            'category': 'Database',
            'difficulty': 'Intermediate',
            'content': '# Database Design\n- Relational databases and SQL\n- NoSQL databases\n- Data normalization\n- Indexing and optimization\n- ACID properties',
            'order': 8,
            'prerequisites': ['Python Basics']
        }
    ]
    
    topic_ids = {}
    for topic in topics:
        result = db.topics.insert_one(topic)
        topic_ids[topic['name']] = str(result.inserted_id)
    print(f"✓ Created {len(topics)} topics")
    
    # ==================== QUESTIONS ====================
    questions = [
        # Python Basics
        {
            'topic_id': ObjectId(topic_ids['Python Basics']),
            'text': 'What is the correct way to declare a variable in Python?',
            'options': [
                'var x = 5',
                'x = 5',
                'declare x = 5',
                'variable x = 5'
            ],
            'correct_answer': 'x = 5',
            'difficulty': 'Beginner',
            'explanation': 'Python uses simple assignment syntax without keywords like var or declare.'
        },
        {
            'topic_id': ObjectId(topic_ids['Python Basics']),
            'text': 'Which of the following is NOT a valid Python data type?',
            'options': [
                'int',
                'str',
                'boolean',
                'list'
            ],
            'correct_answer': 'boolean',
            'difficulty': 'Beginner',
            'explanation': 'Python uses "bool" not "boolean". It includes True and False values.'
        },
        {
            'topic_id': ObjectId(topic_ids['Python Basics']),
            'text': 'What is the output of print(5 // 2)?',
            'options': [
                '2.5',
                '2',
                '3',
                'Error'
            ],
            'correct_answer': '2',
            'difficulty': 'Beginner',
            'explanation': '// is the floor division operator, which returns the integer part of division.'
        },
        {
            'topic_id': ObjectId(topic_ids['Python Basics']),
            'text': 'How do you create a comment in Python?',
            'options': [
                '// This is a comment',
                '/* This is a comment */',
                '# This is a comment',
                '-- This is a comment'
            ],
            'correct_answer': '# This is a comment',
            'difficulty': 'Beginner',
            'explanation': 'Python uses # for single-line comments and triple quotes for multi-line comments.'
        },
        {
            'topic_id': ObjectId(topic_ids['Python Basics']),
            'text': 'What does the len() function return?',
            'options': [
                'The length of a string',
                'The number of items in a list or tuple',
                'The number of characters/items in a sequence',
                'All of the above'
            ],
            'correct_answer': 'All of the above',
            'difficulty': 'Beginner',
            'explanation': 'len() works on any sequence type including strings, lists, tuples, etc.'
        },
        
        # Data Structures
        {
            'topic_id': ObjectId(topic_ids['Data Structures']),
            'text': 'How do you access the first element of a list in Python?',
            'options': [
                'list[1]',
                'list[0]',
                'list.first()',
                'list.get(0)'
            ],
            'correct_answer': 'list[0]',
            'difficulty': 'Beginner',
            'explanation': 'Python uses 0-based indexing, so the first element is at index 0.'
        },
        {
            'topic_id': ObjectId(topic_ids['Data Structures']),
            'text': 'Which data structure is used for key-value pairs?',
            'options': [
                'List',
                'Tuple',
                'Dictionary',
                'Set'
            ],
            'correct_answer': 'Dictionary',
            'difficulty': 'Beginner',
            'explanation': 'Dictionaries store data as key-value pairs, similar to maps in other languages.'
        },
        {
            'topic_id': ObjectId(topic_ids['Data Structures']),
            'text': 'What is a set in Python?',
            'options': [
                'An ordered collection of items',
                'An unordered collection of unique items',
                'A collection of key-value pairs',
                'A fixed-size array'
            ],
            'correct_answer': 'An unordered collection of unique items',
            'difficulty': 'Intermediate',
            'explanation': 'Sets are unordered and automatically eliminate duplicates.'
        },
        
        # OOP
        {
            'topic_id': ObjectId(topic_ids['Object-Oriented Programming']),
            'text': 'What is a class in object-oriented programming?',
            'options': [
                'A function that returns objects',
                'A blueprint for creating objects',
                'A type of variable',
                'A method that initializes variables'
            ],
            'correct_answer': 'A blueprint for creating objects',
            'difficulty': 'Intermediate',
            'explanation': 'A class is a template or blueprint that defines the structure and behavior of objects.'
        },
        {
            'topic_id': ObjectId(topic_ids['Object-Oriented Programming']),
            'text': 'What is inheritance in OOP?',
            'options': [
                'Copying code from one class to another',
                'Creating new classes based on existing ones',
                'Calling methods from parent classes',
                'All of the above'
            ],
            'correct_answer': 'Creating new classes based on existing ones',
            'difficulty': 'Intermediate',
            'explanation': 'Inheritance allows child classes to inherit properties and methods from parent classes.'
        },
        
        # Web Development
        {
            'topic_id': ObjectId(topic_ids['Web Development Basics']),
            'text': 'Which HTML tag is used for the largest heading?',
            'options': [
                '<h6>',
                '<h1>',
                '<heading>',
                '<title>'
            ],
            'correct_answer': '<h1>',
            'difficulty': 'Beginner',
            'explanation': '<h1> is the largest heading tag, with <h6> being the smallest.'
        },
        {
            'topic_id': ObjectId(topic_ids['Web Development Basics']),
            'text': 'What does CSS stand for?',
            'options': [
                'Computer Style Sheets',
                'Cascading Style Sheets',
                'Creative Style System',
                'Code Style Standard'
            ],
            'correct_answer': 'Cascading Style Sheets',
            'difficulty': 'Beginner',
            'explanation': 'CSS is Cascading Style Sheets, used for styling HTML elements.'
        },
        
        # JavaScript
        {
            'topic_id': ObjectId(topic_ids['JavaScript Fundamentals']),
            'text': 'What is the difference between let and var in JavaScript?',
            'options': [
                'No difference',
                'let has block scope, var has function scope',
                'var has block scope, let has function scope',
                'let cannot be reassigned'
            ],
            'correct_answer': 'let has block scope, var has function scope',
            'difficulty': 'Intermediate',
            'explanation': 'let provides block-level scope while var is function-scoped, making let safer.'
        },
        {
            'topic_id': ObjectId(topic_ids['JavaScript Fundamentals']),
            'text': 'How do you add an event listener in JavaScript?',
            'options': [
                'element.listen("click", function)',
                'element.addEventListener("click", function)',
                'element.on("click", function)',
                'element.attach("click", function)'
            ],
            'correct_answer': 'element.addEventListener("click", function)',
            'difficulty': 'Intermediate',
            'explanation': 'addEventListener is the standard method for attaching event listeners in JavaScript.'
        },
        
        # Advanced Python
        {
            'topic_id': ObjectId(topic_ids['Advanced Python']),
            'text': 'What is a decorator in Python?',
            'options': [
                'A function that adds styling',
                'A function that modifies another function or class',
                'A type of error handler',
                'A module import statement'
            ],
            'correct_answer': 'A function that modifies another function or class',
            'difficulty': 'Advanced',
            'explanation': 'Decorators are functions that modify other functions by wrapping them.'
        },
        
        # Machine Learning
        {
            'topic_id': ObjectId(topic_ids['Machine Learning']),
            'text': 'What is supervised learning?',
            'options': [
                'Learning without labels',
                'Learning from labeled training data',
                'Learning by observing humans',
                'A type of reinforcement learning'
            ],
            'correct_answer': 'Learning from labeled training data',
            'difficulty': 'Advanced',
            'explanation': 'Supervised learning uses labeled data with known outcomes to train models.'
        },
        
        # Database Design
        {
            'topic_id': ObjectId(topic_ids['Database Design']),
            'text': 'What is database normalization?',
            'options': [
                'Standardizing all data to lowercase',
                'Organizing data to reduce redundancy',
                'Backing up the database',
                'Converting to NoSQL'
            ],
            'correct_answer': 'Organizing data to reduce redundancy',
            'difficulty': 'Intermediate',
            'explanation': 'Normalization is the process of organizing data to minimize redundancy and dependency.'
        }
    ]
    
    db.questions.insert_many(questions)
    print(f"✓ Created {len(questions)} questions")
    
    # ==================== SAMPLE USER ====================
    from utils.auth import PasswordHandler
    
    sample_user = {
        'email': 'user@learnai.com',
        'username': 'learner',
        'password_hash': PasswordHandler.hash_password('TestPass123'),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'total_points': 150,
        'topics_completed': [],
        'current_level': 'Beginner'
    }
    
    result = db.users.insert_one(sample_user)
    user_id = str(result.inserted_id)
    print(f"✓ Created sample user (email: user@learnai.com, password: TestPass123)")
    
    # ==================== SAMPLE PROGRESS ====================
    sample_progress = [
        {
            'user_id': result.inserted_id,
            'topic_id': ObjectId(list(topic_ids.values())[0]),
            'accuracy': 0.85,
            'avg_time': 45.5,
            'questions_answered': 12,
            'updated_at': datetime.utcnow()
        },
        {
            'user_id': result.inserted_id,
            'topic_id': list(topic_ids.values())[1],
            'accuracy': 0.72,
            'avg_time': 38.2,
            'questions_answered': 8,
            'updated_at': datetime.utcnow()
        }
    ]
    
    db.user_progress.insert_many(sample_progress)
    print("✓ Created sample progress data")
    
    print("\n✅ Database setup complete!")
    print(f"\n📝 Sample User Credentials:")
    print(f"   Email: user@learnai.com")
    print(f"   Password: TestPass123")
    
    client.close()

if __name__ == '__main__':
    setup_database()
