from datetime import datetime

from flask import Flask, render_template, request, redirect, jsonify
from flask_babel import Babel
from flask_bootstrap import Bootstrap, WebCDN
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from chaoswg.admin import init_admin
from chaoswg.forms import RegisterForm, LoginForm, CreateTaskForm, CustomTaskForm
from chaoswg.helpers import format_datetime_custom, format_timedelta_custom
from chaoswg.models import init_database, create_tables, User, Task, History
from chaoswg.scheduler import TaskScheduler

# from test.testdata import insert_testdata

# init app and load config
app = Flask(__name__)
# read ../default-config.py
app.config.from_pyfile('../default-config.py')
# overwrite with custom config in ../custom-config.py
app.config.from_pyfile('../custom-config.py', silent=True)

# init DB
database = init_database(app)
create_tables()
# Comment out in production
# insert_testdata(database)

# init login manager
login_manager = LoginManager()
login_manager.init_app(app)

# Enable bootstrap support
Bootstrap(app)
# jQuery 3 instead of 1
app.extensions['bootstrap']['cdns']['jquery'] = WebCDN(
    '//cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/'
)

# Enable babel support
app.babel = Babel(app, default_timezone='Europe/Berlin')
# set datetime filter for jinja2
app.jinja_env.filters['datetime'] = format_datetime_custom
app.jinja_env.filters['timedelta'] = format_timedelta_custom

# init admin interface
init_admin(app)

# Create the task scheduler thread
task_scheduler = TaskScheduler()


@app.before_first_request
def start_task_scheduler():
    # Start the task scheduler thread only once even if app is in debug mode
    task_scheduler.start()


@app.route('/')
def index():
    return render_template('index.html', usernames=User.get_usernames())


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if app.config['INVITE_KEY'] != form.invite_key.data:
            # TODO return error message, wrong invite key
            return '', 403
        if User.register(form.name.data, form.password.data):
            # TODO return success message
            return redirect('/login')
        else:
            # TODO return error message, user exists
            return '', 403

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.get_by_name(form.name.data)
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            return redirect('/tasks')

    return render_template('login.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    return User.get(User.id == user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/login')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/users')
@login_required
def get_users():
    users = User.get_all()
    usernames = set()
    for user in users:
        usernames.add(user['username'])
    return render_template('users.html', users=users, usernames=usernames)


@app.route('/history')
@login_required
def get_history():
    return render_template('history.html', usernames=User.get_usernames())


@app.route('/history/<username>')
@login_required
def get_history_user(username):
    return render_template('history_user.html', userhist=History.get_user_history(username), username=username,
                           usernames=User.get_usernames())


@app.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    form = CreateTaskForm()

    if form.validate_on_submit():
        task, created = Task.get_or_create(task=form.task.data, defaults={'base_points': form.base_points.data,
                                                                          'time_factor': form.time_factor.data,
                                                                          'schedule_days': form.schedule_days.data})
        if not created:
            # TODO return error message, task exists
            return '', 403

        # TODO return success message
        return redirect('/tasks')

    return render_template('create_task.html', form=form)


@app.route('/do_custom_task', methods=['GET', 'POST'])
@login_required
def do_custom_task():
    form = CustomTaskForm()

    if form.validate_on_submit():
        # do custom onetime task
        Task.do_custom_task(form.task.data, form.points.data, current_user.get_id())
        return redirect('/tasks')

    return render_template('do_custom_task.html', form=form)


@app.route('/tasks')
@login_required
def get_tasks():
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
                           usernames=User.get_usernames())


@app.route('/set_task_state', methods=['POST'])
@login_required
def set_task_state():
    user_id = current_user.get_id()
    task_id = request.form.get('id', type=int)
    state = request.form.get('state', type=int)
    if None not in (task_id, state, user_id) and state in (0, 1, 2):
        Task.set_state(task_id, state, user_id)
    else:
        # TODO message
        return '', 403
    # New state was set
    return '', 204


#########################
# JSON endpoints for JS #
#########################

@app.route('/json/history/<username>')
@login_required
def get_history_user_json(username):
    return jsonify(History.get_user_history(username))


@app.route('/json/users')
@login_required
def get_users_json():
    return jsonify(User.get_all())


@app.route('/json/history')
@login_required
def get_history_json():
    hist = History.get_full_history()
    result = {}
    for h in hist:
        if h['username'] not in result:
            # initial 0 points
            result[h['username']] = [{
                'time': h['time'],
                'points': 0
            }]
        result[h['username']].append({
            'time': h['time'],
            'points': h['points']
        })

    # same point count till today
    for user in result:
        result[user].append({
            'time': datetime.utcnow(),
            'points': 0
        })

    return jsonify(result)
