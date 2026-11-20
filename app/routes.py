from functools import wraps
from flask import jsonify, request
from flask_login import current_user, login_required, login_user, logout_user
from app import app,db
from app.models import User
import os
ADMIN_KEY = os.getenv("ADMIN_KEY")

def role_required(role):
    def decorator (f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role != role:
                return jsonify({"error": "Access denied"}), 403
            return f(*args, **kwargs)

        return decorated_function
    return decorator

@app.route('/')
def home():
    return jsonify({
        "message": "Admin User API is running successfully!"
    }), 200

@app.route('/signup', methods = ['POST'])
def signup():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already in use"}), 409
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already in use"}), 409
    role = data.get('role', 'user')
    if role == 'admin' and (not ADMIN_KEY or data.get('admin_key') != ADMIN_KEY):
        return jsonify({"error":"Invalid admin key"}), 403

    user = User(username=data['username'], email=data.get('email', f"{data['username']}@test.com"),role=data.get('role', 'user'))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message":"User created successfully"}), 201

@app.route('/login', methods = ['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({"message":"User logged in"}), 200
    return jsonify({"error": "Invalid credentials"})

@app.route('/user/dashboard')
@login_required
@role_required('user')
def user_dashboard():
    return jsonify({
        "message": "Welcome User",
        "username": current_user.username,
        "role": current_user.role
    }), 200

@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    return jsonify({
        "message": "Welcome Admin",
        "username": current_user.username,
        "role": current_user.role
    }), 200

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "User logged out successfully"}), 200