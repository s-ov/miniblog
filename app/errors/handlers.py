from flask import Blueprint, render_template
from app import db
from app.errors import bp as errors_bp

errors_bp = Blueprint(
    'errors', __name__, template_folder='templates',
    )


@errors_bp.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html', title='404'), 404


@errors_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html', title='500'), 500
