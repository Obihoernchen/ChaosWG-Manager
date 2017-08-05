from flask import Flask, render_template, request, redirect, url_for, abort
from flask_bootstrap import Bootstrap, WebCDN
from flask_babel import Babel, format_datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
# from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.peewee import ModelView
# from flask_restful import Resource, Api
from models import *
from forms import *

login_manager = LoginManager()


def format_datetime_custom(value):
    if value is None:
        return 'Not yet'
    return format_datetime(value, 'dd.MM.yy HH:mm')


class ChaosWG(Flask):
    def __init__(self, import_name, **kwargs):
        super(ChaosWG, self).__init__(import_name, **kwargs)

        # Secret key for sessions
        self.secret_key = '%\x9a\xed\xb2.\x84\xbb\x82R\xe4n\x99P=uF;{\x08\x0c6\xc5\xb7I'

        # Enable bootstrap support
        Bootstrap(self)
        # jQuery 3 instead of 1
        self.extensions['bootstrap']['cdns']['jquery'] = WebCDN(
            '//cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/'
        )
        # Enable babel support
        self.babel = Babel(self, default_timezone='Europe/Berlin')

        # set datetime filter for jinja2
        self.jinja_env.filters['datetime'] = format_datetime_custom

        # init LoginManager
        login_manager.init_app(self)

        # init flask admin
        # self.admin = Admin(self, index_view=MyAdminIndexView(), name='ChaosWG Admin', template_mode='bootstrap3')
        # self.admin.add_view(MyModelView(Task))
        # self.admin.add_view(MyModelView(User))
        # self.admin.add_view(MyModelView(Room))

        # Routes
        self.route('/')(self.index)
        self.route('/login', methods=['GET', 'POST'])(self.login)
        self.route('/logout')(self.logout)
        self.route('/get_users')(self.get_users)
        self.route('/get_tasks')(self.get_tasks)
        self.route('/set_task_state', methods=['POST'])(self.set_task_state)
        self.route('/get_user_history/<username>')(self.get_history)
        # TODO check methods
        self.route('/create_task', methods=['GET', 'POST'])(self.create_task)

    def index(self):
        return render_template('index.html', users=User.get_all())

    def login(self):
        form = LoginForm()

        if form.validate_on_submit():
            user = User.get_by_name(form.name.data)
            if user and user.check_password(form.password.data):
                login_user(user, remember=True)
                return redirect('/get_tasks')

        return render_template('login.html', form=form)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(User.id == user_id)

    @login_manager.unauthorized_handler
    def unauthorized(self):
        return redirect('/login')

    @login_required
    def logout(self):
        logout_user()
        return redirect('/')

    @login_required
    def get_users(self):
        return render_template('users.html', users=User.get_all())

    @login_required
    def get_history(self, username):
        return render_template('history.html', userhist=History.get_user_history(username), username=username,
                               users=User.get_all())

    @login_required
    def create_task(self):
        form = CreateTaskForm()

        if form.validate_on_submit():
            task, created = Task.get_or_create(task=form.task.data, base_points=form.base_points.data,
                                               time_factor=form.time_factor.data)
            if not created:
                # TODO return error message, task exists
                return '', 403
            else:
                # TODO return success message
                return redirect('/get_tasks')

        return render_template('create_task.html', form=form)

    @login_required
    def get_tasks(self):
        tasks = Task.get_all()
        backlog = [t for t in tasks if t.state == Task.BACKLOG]
        todo = [t for t in tasks if t.state == Task.TODO]
        done = [t for t in tasks if t.state == Task.DONE]

        progress = {
            'backlog': len(backlog) / len(tasks) * 100,
            'todo': len(todo) / len(tasks) * 100,
            'done': len(done) / len(tasks) * 100
        }

        return render_template('tasks.html', backlog=backlog, todo=todo, done=done, progress=progress,
                               users=User.get_all())

    @login_required
    def set_task_state(self):
        # TODO proper use user session variable
        user_id = current_user.get_id()
        task_id = request.form.get('id', type=int)
        state = request.form.get('state', type=int)
        if None not in (task_id, state, user_id) and state in (0, 1, 2):
            Task.set_state(task_id, state, user_id)
        else:
            # TODO message
            return '', 403
        return '', 204
