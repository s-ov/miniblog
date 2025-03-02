from flask_wtf import FlaskForm                     
from flask_wtf.file import FileField, FileAllowed   
from wtforms import (                               
    StringField, 
    TextAreaField,
    PasswordField, 
    BooleanField, 
    SubmitField,
    )                                           
from wtforms.validators import (                    
    ValidationError, 
    DataRequired, 
    Email, 
    EqualTo,
    Length,
    )
from flask_babel import lazy_gettext as _l
from app.user.models import User


class RegistrationForm(FlaskForm):
    "Handle registration form for user"

    username = StringField(_l('Ім\'я:'), validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль:', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторіть пароль:', 
        validators=[
            DataRequired(), 
            EqualTo('password')],
        )
    submit = SubmitField('Реєстрація')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Користувач з таким іменем вже зареєстрований.')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('No such email. First, register.')


class LoginForm(FlaskForm):
    "Handle login form for user"
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

    class Meta:
        csrf = False

    def validate_email(self, field):
        field.data = field.data.strip()


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Повторити пароль', 
        validators=[DataRequired(), EqualTo('password')],
        )
    submit = SubmitField('Змінити пароль')


class EmptyForm(FlaskForm):
    "Handle follow or unfollow action"
    submit = SubmitField('Виконати')


class EditProfileForm(FlaskForm):
    "Handle user profile updating form"

    username = StringField('Ім\'я: ', validators=[DataRequired()])
    bio = TextAreaField('Про мене', validators=[Length(min=0, max=140)])
    submit = SubmitField('Зберегти')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Виберіть інше імя.')
            

class ProfilePictureForm(FlaskForm):
    profile_picture = FileField('Upload Profile Picture', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Upload')


class DeleteAccountForm(FlaskForm):
    """Form to confirm account deletion."""
    password = PasswordField("Enter your password:", validators=[DataRequired()])
    submit = SubmitField("Delete Account")
