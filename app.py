from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap, WebCDN
from flask_babel import Babel, format_datetime
# from flask_restful import Resource, Api
from models import *


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

        # Routes
        self.route('/')(self.index)
        self.route('/get_users')(self.get_users)
        self.route('/get_tasks')(self.get_tasks)
        self.route('/set_task_state', methods=['POST'])(self.set_task_state)
        self.route('/get_user_history/<username>')(self.get_history)
        self.route('/create_task', methods=['POST'])(self.create_task)

        # set datetime filter for jinja2
        self.jinja_env.filters['datetime'] = format_datetime_custom

    def index(self):
        return render_template('index.html', users=User.get_all())

    def get_users(self):
        return render_template('users.html', users=User.get_all())

    def get_history(self, username):
        return render_template('history.html', userhist=History.get_user_history(username), username=username,
                               users=User.get_all())

    def create_task(self):
        bla = request.form.get('bla')
        return 'TODO'

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

    def set_task_state(self):
        # TODO proper use user session variable
        user_id = 1
        task_id = request.form.get('id', type=int)
        state = request.form.get('state', type=int)
        if None not in (task_id, state, user_id) and state in (0, 1, 2):
            Task.set_state(task_id, state, user_id)
        else:
            pass
        # TODO else and proper return code
        return 'OK'
