import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

# Initialize extensions.
db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()

def create_app(config_object='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Initialize extensions.
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # Register API blueprint, if applicable.
    from api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Route to serve the landing page from the frontend folder.
    @app.route('/')
    def index():
        # "frontend" is relative to the current working directory.
        return send_from_directory('frontend', 'index.html')

    return app

# Create a module-level app instance.
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

