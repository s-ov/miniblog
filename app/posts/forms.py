from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import (
    DataRequired, Length,
    )


class PostForm(FlaskForm):
    "Class for post form"
    post = TextAreaField('Скажи свою думку', 
                        validators=[
                                DataRequired(), 
                                Length(min=2, max=140),
                                ],
                        )
    submit = SubmitField('Опублікувати')
