from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from .settings import Config

class MongoDBConnection:
    """MongoDB connection manager"""
    
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def connect(cls, uri=None):
        """Establish MongoDB connection"""
        if cls._client is None:
            uri = uri or Config.MONGODB_URI
            try:
                cls._client = MongoClient(uri, serverSelectionTimeoutMS=5000)
                cls._client.admin.command('ping')
                cls._db = cls._client.get_default_database()
                print(f"✓ Connected to MongoDB: {cls._db.name}")
                return cls._db
            except ServerSelectionTimeoutError as e:
                print(f"✗ Failed to connect to MongoDB: {e}")
                raise
    
    @classmethod
    def get_db(cls):
        """Get database instance"""
        if cls._db is None:
            cls.connect()
        return cls._db
    
    @classmethod
    def close(cls):
        """Close MongoDB connection"""
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None
            print("✓ MongoDB connection closed")

# Convenience function
def get_db():
    """Get MongoDB database instance"""
    return MongoDBConnection.get_db()
