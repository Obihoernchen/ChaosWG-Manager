from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, IntegerField, FloatField, SubmitField
from wtforms.validators import InputRequired, NumberRange


class LoginForm(FlaskForm):
    name = StringField(u'Username', validators=[InputRequired()])
    password = PasswordField(u'Password', validators=[InputRequired()])

    submit = SubmitField(u'Login')


class CreateTaskForm(FlaskForm):
    task = StringField(u'Task', validators=[InputRequired()])
    base_points = IntegerField(u'Base Points', validators=[NumberRange(1, 13, 'Value must be between 1 and 13')])
    time_factor = FloatField(u'Time Factor', validators=[NumberRange(0.0, 3.0, 'Value must be between 0.0 and 3.0')])
    # room = StringField(u'Room', validators=[InputRequired()])

    submit = SubmitField(u'Create Task')


class CustomTaskForm(FlaskForm):
    task = StringField(u'Custom Task', validators=[InputRequired()])
    points = IntegerField(u'Points', validators=[NumberRange(1, 13, 'Value must be between 1 and 13')])
    # room = StringField(u'Room', validators=[InputRequired()])

    submit = SubmitField(u'Do Task now')
