from flask_wtf import FlaskForm
from wtforms.fields import *
from wtforms.validators import InputRequired


class LoginForm(FlaskForm):
    name = StringField(u'Username', validators=[InputRequired()])
    password = PasswordField(u'Password', validators=[InputRequired()])

    submit = SubmitField(u'Login')