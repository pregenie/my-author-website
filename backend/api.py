import datetime
from urllib.parse import urlparse
import psycopg2
from functools import wraps
from flask import Blueprint, request, jsonify
from models import db, User, Rating, Configuration, Blog, Book, SocialLink, Site, bcrypt

api_bp = Blueprint('api', __name__)

# -------------------------
# Utility Function
# -------------------------
def generate_slug(username):
    """Generate a URL-friendly slug from the username."""
    return username.lower().replace(" ", "-")

# -------------------------
# Authentication Decorator
# -------------------------
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        # For demonstration, we use a hard-coded token.
        if token != 'secret-token':
            return jsonify({'message': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

# -------------------------
# API Endpoints
# -------------------------

@api_bp.route('/login', methods=['POST'])
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
    # For simplicity, we return a static token.
    return jsonify({'token': 'secret-token', 'username': user.username, 'slug': user.slug})

@api_bp.route('/register', methods=['POST'])
def register():
    """
    Registers a new author.
    Expects JSON payload with "username", "email", "password", and optionally "name".
    """
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    name = data.get('name', username)
    if not username or not email or not password:
        return jsonify({'message': 'Missing required fields'}), 400
    # Check if a user with the same username or email exists
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'message': 'Author account already exists'}), 400
    new_user = User(
        username=username,
        email=email,
        name=name,
        slug=generate_slug(username)
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Registration successful', 'slug': new_user.slug})

@api_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Initiates a password reset for the author.
    Expects JSON payload with "email".
    (This endpoint simulates sending a reset email.)
    """
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'message': 'Email is required'}), 400
    # In a real implementation, verify the email and send a reset token.
    return jsonify({'message': f'Password reset instructions sent to {email}'})

@api_bp.route('/properties', methods=['PUT'])
@require_auth
def update_properties():
    """
    Updates the author's properties.
    Expects JSON payload with "name", "email", "username", and optionally "password".
    """
    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({'message': 'Username is required to update properties.'}), 400
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'Author not found'}), 404
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    if 'username' in data:
        user.username = data['username']
        user.slug = generate_slug(data['username'])
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    db.session.commit()
    return jsonify({'message': 'Properties updated successfully', 'slug': user.slug})

@api_bp.route('/config', methods=['GET'])
def get_config():
    """
    Returns all configuration key-value pairs.
    """
    configs = Configuration.query.all()
    config_dict = {conf.config_key: conf.config_value for conf in configs}
    return jsonify(config_dict)

@api_bp.route('/config', methods=['PUT'])
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

@api_bp.route('/rate', methods=['POST'])
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

@api_bp.route('/ratings/<blog_id>', methods=['GET'])
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

@api_bp.route('/author/<slug>', methods=['GET'])
def get_author_site(slug):
    """
    Returns the full site data for a given author by slug.
    Includes author info, site settings, blogs, books, and social links.
    """
    user = User.query.filter_by(slug=slug).first()
    if not user:
        return jsonify({'message': 'Author not found'}), 404

    # Retrieve site settings for this author
    site = Site.query.filter_by(user_id=user.id).first()
    site_data = {}
    if site:
        site_data = {
            "title": site.title,
            "author": site.author,
            "introduction": site.introduction,
            "navbar": site.navbar,
            "footer": site.footer,
            "heroBackground": site.heroBackground
        }

    # Retrieve blogs
    blogs = Blog.query.filter_by(author_id=user.id).all()
    blogs_list = [{
        "title": blog.title,
        "subtitle": blog.subtitle,
        "description": blog.description,
        "image": blog.image,
        "published": blog.published,
        "name": blog.name,
        "publish_date": blog.publish_date.isoformat() if blog.publish_date else None,
        "show": blog.show
    } for blog in blogs]

    # Retrieve books
    books = Book.query.filter_by(author_id=user.id).all()
    books_list = [{
        "title": book.title,
        "description": book.description,
        "image": book.image,
        "published": book.published,
        "amazonUrl": book.amazonUrl,
        "barnesandnobleUrl": book.barnesandnobleUrl,
        "googlebooksUrl": book.googlebooksUrl
    } for book in books]

    # Retrieve social links
    socials = SocialLink.query.filter_by(user_id=user.id).all()
    socials_list = [{
        "name": social.name,
        "url": social.url,
        "icon": social.icon,
        "color": social.color
    } for social in socials]

    return jsonify({
        "author": {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "slug": user.slug
        },
        "site": site_data,
        "blogs": blogs_list,
        "books": books_list,
        "socialLinks": socials_list
    })

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
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print("Using database URI:", db_uri)
    create_database_if_not_exists(db_uri)

    with app.app_context():
        upgrade()

    app.run(debug=True, host='0.0.0.0')
