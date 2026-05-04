from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import os
from config.settings import config
from config.database import MongoDBConnection
from routes.api_routes import register_routes

def create_app(config_name='development'):
    """Application factory"""
    
    # Initialize Flask app
    app = Flask(__name__, 
                template_folder='../frontend',
                static_folder='../frontend/static',
                static_url_path='/static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize MongoDB connection
    MongoDBConnection.connect(app.config['MONGODB_URI'])
    
    # Enable CORS for API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register API routes
    register_routes(app)
    
    # Serve frontend
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        if os.path.isfile(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return render_template('index.html')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def server_error(error):
        return {'error': 'Internal server error'}, 500
    
    # Health check
    @app.route('/api/health', methods=['GET'])
    def health():
        return {'status': 'healthy'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    print("🚀 Starting Learning Platform API Server...")
    print("📡 Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
