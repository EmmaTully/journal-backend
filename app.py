from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

# Enable CORS
CORS(app, origins=['http://localhost:*', 'http://127.0.0.1:*', 'https://*.github.io'])

# Initialize JWT
jwt = JWTManager(app)

# Simple file-based database (for demo - in production use a real database)
USERS_FILE = 'users.json'

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Journal backend is running'})

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Load existing users
        users = load_users()
        
        # Check if user already exists
        if email in users:
            return jsonify({'error': 'User already exists'}), 409
        
        # Create new user
        users[email] = {
            'email': email,
            'name': name,
            'password_hash': generate_password_hash(password),
            'created_at': str(datetime.now()),
            'papers': []  # Store submitted papers
        }
        
        # Save users
        save_users(users)
        
        # Create access token
        access_token = create_access_token(identity=email)
        
        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': {
                'email': email,
                'name': name
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Load users
        users = load_users()
        
        # Check if user exists
        if email not in users:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password
        user = users[email]
        if not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create access token
        access_token = create_access_token(identity=email)
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'email': email,
                'name': user.get('name', '')
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile (protected route)"""
    try:
        email = get_jwt_identity()
        users = load_users()
        
        if email not in users:
            return jsonify({'error': 'User not found'}), 404
        
        user = users[email]
        return jsonify({
            'email': email,
            'name': user.get('name', ''),
            'created_at': user.get('created_at', ''),
            'papers_count': len(user.get('papers', []))
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit-paper', methods=['POST'])
@jwt_required()
def submit_paper():
    """Submit a paper (protected route)"""
    try:
        email = get_jwt_identity()
        data = request.get_json()
        
        # Get paper details
        paper = {
            'title': data.get('title'),
            'authors': data.get('authors'),
            'abstract': data.get('abstract'),
            'submitted_at': str(datetime.now()),
            'status': 'submitted',
            'id': len(load_users().get(email, {}).get('papers', [])) + 1
        }
        
        # Load users and add paper
        users = load_users()
        if email not in users:
            return jsonify({'error': 'User not found'}), 404
        
        if 'papers' not in users[email]:
            users[email]['papers'] = []
        
        users[email]['papers'].append(paper)
        save_users(users)
        
        return jsonify({
            'message': 'Paper submitted successfully',
            'paper': paper
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/my-papers', methods=['GET'])
@jwt_required()
def get_my_papers():
    """Get user's submitted papers (protected route)"""
    try:
        email = get_jwt_identity()
        users = load_users()
        
        if email not in users:
            return jsonify({'error': 'User not found'}), 404
        
        papers = users[email].get('papers', [])
        return jsonify({'papers': papers}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GPT Review endpoint (placeholder for now)
@app.route('/api/gpt-review', methods=['POST'])
@jwt_required()
def gpt_review():
    """Simulate GPT review (placeholder - would integrate with actual GPT API)"""
    try:
        data = request.get_json()
        paper_content = data.get('content', '')
        
        # Simulate review based on content
        # In production, this would call OpenAI/Anthropic API
        is_recognition_science = 'recognition' in paper_content.lower() or 'golden ratio' in paper_content.lower()
        
        if is_recognition_science:
            review_result = {
                'passed': True,
                'score': 9.2,
                'feedback': {
                    'strengths': [
                        'Outstanding mathematical rigor',
                        'Zero free parameters',
                        'Clear methodology'
                    ],
                    'suggestions': [
                        'Consider additional examples'
                    ]
                }
            }
        else:
            review_result = {
                'passed': False,
                'score': 6.5,
                'feedback': {
                    'major_issues': [
                        'Mathematical proofs need strengthening',
                        'Insufficient literature review'
                    ],
                    'minor_issues': [
                        'Formatting consistency'
                    ]
                }
            }
        
        return jsonify(review_result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Import datetime here to avoid issues
    from datetime import datetime
    
    print("Starting Journal Backend Server...")
    print("API Endpoints:")
    print("  POST   /api/register     - Register new user")
    print("  POST   /api/login        - Login user")
    print("  GET    /api/profile      - Get user profile (requires auth)")
    print("  POST   /api/submit-paper - Submit paper (requires auth)")
    print("  GET    /api/my-papers    - Get user's papers (requires auth)")
    print("  POST   /api/gpt-review   - GPT review (requires auth)")
    print("\nServer running on http://localhost:5555")
    
    app.run(debug=True, port=5555) 