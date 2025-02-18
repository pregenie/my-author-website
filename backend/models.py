from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)  # URL-friendly unique identifier for the author
    email = db.Column(db.String(120), unique=True, nullable=True)
    name = db.Column(db.String(120), nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    about = db.Column(db.Text, nullable=True)       # New field: about the author (HTML allowed)
    philosophy = db.Column(db.Text, nullable=True)  # New field: philosophy (HTML allowed)

    # Relationships
    blogs = db.relationship('Blog', backref='author', lazy=True)
    books = db.relationship('Book', backref='author', lazy=True)
    site = db.relationship('Site', backref='author', uselist=False)
    social_links = db.relationship('SocialLink', backref='author', lazy=True)

    def set_password(self, password):
        """Generates and sets the password hash for the given password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Checks the given password against the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)


class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    # Optional: Link to a User (if ratings should be associated with users)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)


class Configuration(db.Model):
    __tablename__ = 'configurations'

    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False)
    config_value = db.Column(db.Text, nullable=False)


class Blog(db.Model):
    __tablename__ = 'blogs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(200), nullable=True)
    html_content = db.Column(db.Text, nullable=True)  # New field for HTML partial content
    published = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    publish_date = db.Column(db.Date, default=datetime.date.today, nullable=True)
    show = db.Column(db.Boolean, default=True, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)



class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(200), nullable=True)
    published = db.Column(db.Boolean, default=False)
    amazonUrl = db.Column(db.String(300), nullable=True)
    barnesandnobleUrl = db.Column(db.String(300), nullable=True)
    googlebooksUrl = db.Column(db.String(300), nullable=True)
    # Associate each book with an author.
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class SocialLink(db.Model):
    __tablename__ = 'social_links'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(300), nullable=False)
    icon = db.Column(db.String(200), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    # Optionally associate social links with an author (if each site has its own social links)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)


# New Model: Site – to store site-wide settings for each author
class Site(db.Model):
    __tablename__ = 'sites'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    introduction = db.Column(db.Text, nullable=False)
    navbar = db.Column(db.String(50), nullable=True)
    footer = db.Column(db.String(50), nullable=True)
    heroBackground = db.Column(db.String(300), nullable=True)
    # Associate the site settings with the author (User)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
