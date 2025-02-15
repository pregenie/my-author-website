import os
import sys
from urllib.parse import urlparse
import psycopg2

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate, upgrade
from functools import wraps

# Create the Flask app
app = Flask(__name__)

# Set default DATABASE_URL if not provided via environment
default_db_uri = 'postgresql://postgres:postgres@localhost/my_author_website_db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', default_db_uri)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

# Import our data models from models.py.
# models.py should define: db, bcrypt, and the models: User, Rating, Configuration
from models import User, Rating, Configuration


# -------------------------
# Authentication Decorator
# -------------------------
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        # For demonstration, we check against a hard-coded token.
        if token != 'secret-token':
            return jsonify({'message': 'Unauthorized'}), 401
        return f(*args, **kwargs)

    return decorated


# -------------------------
# API Endpoints
# -------------------------

@app.route('/api/login', methods=['POST'])
def login():
    """
    Validates user credentials and returns a token if successful.
    Expects JSON payload with "username" and "password".
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # For simplicity, return a static token.
    return jsonify({'token': 'secret-token', 'username': user.username})


@app.route('/api/config', methods=['GET'])
def get_config():
    """
    Returns all configuration key-value pairs.
    """
    configs = Configuration.query.all()
    config_dict = {conf.config_key: conf.config_value for conf in configs}
    return jsonify(config_dict)


@app.route('/api/config', methods=['PUT'])
@require_auth
def update_config():
    """
    Updates configuration settings.
    Expects a JSON payload with key-value pairs.
    """
    data = request.get_json()
    for key, value in data.items():
        conf = Configuration.query.filter_by(config_key=key).first()
        if conf:
            conf.config_value = value
        else:
            conf = Configuration(config_key=key, config_value=value)
            db.session.add(conf)
    db.session.commit()
    return jsonify({'message': 'Configuration updated'})


@app.route('/api/rate', methods=['POST'])
def submit_rating():
    """
    Records a rating for a blog post.
    Expects JSON payload with "blog_id" and "rating" (an integer 1–5).
    """
    data = request.get_json()
    blog_id = data.get('blog_id')
    rating_value = data.get('rating')

    if not blog_id or not rating_value:
        return jsonify({'message': 'Missing blog_id or rating'}), 400

    try:
        rating_value = int(rating_value)
        if rating_value < 1 or rating_value > 5:
            raise ValueError()
    except ValueError:
        return jsonify({'message': 'Rating must be an integer between 1 and 5'}), 400

    rating = Rating(blog_id=blog_id, rating=rating_value)
    db.session.add(rating)
    db.session.commit()
    return jsonify({'message': 'Rating submitted'})


@app.route('/api/ratings/<blog_id>', methods=['GET'])
def get_ratings(blog_id):
    """
    Returns the average rating and count for a given blog post.
    """
    ratings = Rating.query.filter_by(blog_id=blog_id).all()
    if not ratings:
        return jsonify({'average': None, 'count': 0})

    total = sum(r.rating for r in ratings)
    count = len(ratings)
    avg = total / count
    return jsonify({'average': avg, 'count': count})


# -------------------------
# Database Creation Helper
# -------------------------
def create_database_if_not_exists(db_uri):
    """
    Checks whether the target database exists.
    If it doesn't, connects to the default 'postgres' database and creates it.
    """
    url = urlparse(db_uri)
    user = url.username
    password = url.password
    host = url.hostname or 'localhost'
    port = url.port or 5432
    dbname = url.path.lstrip('/')  # remove leading slash

    # Connect to the default database "postgres" to check if our target exists.
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True
    except Exception as e:
        print("Error connecting to PostgreSQL server:", e)
        sys.exit(1)

    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
    exists = cur.fetchone()
    if not exists:
        print(f"Database '{dbname}' does not exist. Creating it...")
        try:
            cur.execute(f'CREATE DATABASE "{dbname}"')
            print(f"Database '{dbname}' created successfully.")
        except Exception as e:
            print("Error creating database:", e)
    else:
        print(f"Database '{dbname}' already exists.")

    cur.close()
    conn.close()


# -------------------------
# Main Entry Point
# -------------------------
if __name__ == '__main__':
    # Use the configured DATABASE_URL (or default) and create the database if it doesn't exist.
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print("Using database URI:", db_uri)
    create_database_if_not_exists(db_uri)

    # Apply any pending migrations automatically.
    with app.app_context():
        upgrade()

    # Start the Flask application.
    app.run(debug=True, host='0.0.0.0')
