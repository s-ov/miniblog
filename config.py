import os 

basedir = os.path.abspath(os.path.dirname(__name__))


class Config:
    "Class configures Flask project"
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'y6&8##ou-w00il7l-ne/.<ve)00r-g5u7e!=s22s@'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                                             'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 5
    LANGUAGES = ['en', 'es']
    DEBUG = os.environ.get("FLASK_DEBUG", False)

    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app/static/uploads/profile_pics')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['s.ovsiuk@gmail.com']
