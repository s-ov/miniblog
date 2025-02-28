import pytest 
from flask import Flask
from app import db
from app.user.models import User
from flask import url_for
from werkzeug.security import generate_password_hash


def create_app(config_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app


@pytest.fixture(scope='module')
def app():
    app = create_app('testing') 
    with app.app_context():
        db.create_all()  
    yield app
    
        
@pytest.fixture
def auth(client):
    """Fixture to handle authentication."""
    def login(email, password):
        response = client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)
        return response
    return login


@pytest.fixture
def client(app):
    """Fixture to provide the Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Fixture to provide the Flask test runner."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Fixture to create a test user."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("testpassword")
        )
        db.session.add(user)
        db.session.commit()
    return user


def test_reset_password_request_authenticated(client, test_user, auth):
    """Ensure logged-in users are redirected away from reset request page."""
    auth.login(email=test_user.email, password="testpassword") 
    response = client.get(url_for('user.reset_password_request'))
    assert response.status_code == 302  
    assert response.location.endswith(url_for('user.index'))


# def test_reset_password_request_invalid_email(client):
#     """Ensure submitting a reset request with an invalid email does nothing."""
#     response = client.post(url_for('user.reset_password_request'), data={
#         "email": "invalid@example.com"
#     }, follow_redirects=True)

#     assert "Check your email" in response.data.decode("utf-8")
#     assert response.status_code == 200  # Should still be on the same page


# def test_reset_password_request_valid_email(client, test_user, mocker):
#     """Ensure submitting a valid email triggers the email sending."""
#     mock_send_email = mocker.patch("app.user.routes.send_reset_email")

#     response = client.post(url_for('user.reset_password_request'), data={
#         "email": test_user.email
#     }, follow_redirects=True)

#     assert mock_send_email.called  # Ensure the email function was called
#     assert "Check your email" in response.data.decode("utf-8") 
#     assert response.status_code == 200

# def test_reset_password_invalid_token(client):
#     """Ensure an invalid reset token redirects to the index page."""
#     response = client.get(url_for('user.reset_password', token="invalidtoken"))
#     assert response.status_code == 302  
#     assert response.location.endswith(url_for('user.index'))

# def test_reset_password_valid_token(client, test_user, mocker):
#     """Ensure a user can reset password using a valid token."""
#     valid_token = test_user.get_reset_token()  
#     mock_verify = mocker.patch("app.user.models.User.verify_reset_password_token", return_value=test_user)

#     response = client.post(url_for('user.reset_password', token=valid_token), data={
#         "password": "newpassword",
#         "confirm_password": "newpassword"
#     }, follow_redirects=True)

#     assert mock_verify.called
#     assert b'Your password has been reset' in response.data  
#     assert response.status_code == 200

# def test_reset_password_authenticated_user_redirect(client, test_user, auth):
#     """Ensure authenticated users cannot access reset password pages."""
#     auth.login(email=test_user.email, password="testpassword")  
#     response = client.get(url_for('user.reset_password', token="some_token"))
    
#     assert response.status_code == 302  
#     assert response.location.endswith(url_for('user.index'))
