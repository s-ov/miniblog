from flask import Flask
from app.extensions import (
    db, migrate, login, mail, moment, babel,
    )
from config import Config


def create_app():
    "Create Flask app with application factory pattern."

    app = Flask(__name__,)
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    from app.user.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from app.user.routes import user_bp
    app.register_blueprint(user_bp)

    from app.posts.routes import posts_bp
    app.register_blueprint(posts_bp)

    from app.workflow.routes import workflow_bp
    app.register_blueprint(workflow_bp, url_prefix='/workflow')

    from app.errors.handlers import errors_bp
    app.register_blueprint(errors_bp)
    
    from app.user.models import User
    from app.posts.models import Post

    @app.shell_context_processor
    def make_shell_context():
        """
        Create a shell context that adds the database instance
        and models to the shell session.
        You can work in < flask shell > without importing.
        """
        return {'db': db, 'User': User, 'Post': Post}

    return app
