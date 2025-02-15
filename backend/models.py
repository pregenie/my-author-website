from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Assume that the Flask app and SQLAlchemy instance are created in app.py.
# If using an application factory pattern, adjust the import accordingly.
db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

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
