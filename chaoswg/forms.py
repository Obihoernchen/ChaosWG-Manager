from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, IntegerField, FloatField, SubmitField
from wtforms.validators import InputRequired, NumberRange, Optional


class LoginForm(FlaskForm):
    name = StringField(u'Username', validators=[InputRequired()])
    password = PasswordField(u'Password', validators=[InputRequired()])

    submit = SubmitField(u'Login')


class CreateTaskForm(FlaskForm):
    task = StringField(u'Task', validators=[InputRequired()])
    base_points = IntegerField(u'Base Points',
                               validators=[InputRequired(), NumberRange(1, 13, 'Value must be between 1 and 13')],
                               default=1)
    time_factor = FloatField(u'Time Factor',
                             validators=[InputRequired(), NumberRange(0.0, 3.0, 'Value must be between 0.0 and 3.0')],
                             default=0.0)
    schedule_days = IntegerField(u'Schedule every X days (optional)',
                                 validators=[Optional(), NumberRange(1, 365, 'Value must be between 1 and 365')])

    submit = SubmitField(u'Create Task')


class CustomTaskForm(FlaskForm):
    task = StringField(u'Custom Task', validators=[InputRequired()])
    points = IntegerField(u'Points', validators=[InputRequired(), NumberRange(1, 13, 'Value must be between 1 and 13')],
                          default=1)

    submit = SubmitField(u'Do Task now')
