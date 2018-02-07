from datetime import datetime

from peewee import (CharField, IntegerField, DateTimeField, SmallIntegerField, ForeignKeyField,
                    FloatField, DoesNotExist, SqliteDatabase)
from playhouse.flask_utils import FlaskDB
from werkzeug.security import generate_password_hash, check_password_hash

db_wrapper = FlaskDB()


def init_database(app):
    db_wrapper._db = SqliteDatabase(app.config['DATABASE'], pragmas=(('journal_mode', 'wal'),))
    db_wrapper.init_app(app)
    return db_wrapper.database


def create_tables():
    db_wrapper.database.connect()
    db_wrapper.database.create_tables([User, Task, History], safe=True)
    db_wrapper.database.close()


def insert_testdata():
    # pwhash = generate_password_hash('123456')
    with db_wrapper.database.atomic():
        # User.get_or_create(username='User1', defaults={'password': pwhash})
        # User.get_or_create(username='User2', defaults={'password': pwhash})
        # User.get_or_create(username='User3', defaults={'password': pwhash})
        # User.get_or_create(username='User4', defaults={'password': pwhash})
        # User.get_or_create(username='User5', defaults={'password': pwhash})

        Task.get_or_create(task='Kühlschrankcheck',
                           defaults={'base_points': 2, 'time_factor': 0.0, 'state': Task.BACKLOG})
        Task.get_or_create(task='Grünabfall',
                           defaults={'base_points': 1, 'time_factor': 0.0, 'state': Task.BACKLOG})
        Task.get_or_create(task='Fenster putzen',
                           defaults={'base_points': 3, 'time_factor': 0.0, 'state': Task.BACKLOG})
        Task.get_or_create(task='Ofen reinigen',
                           defaults={'base_points': 3, 'time_factor': 0.0, 'state': Task.BACKLOG})
        Task.get_or_create(task='Tiefkühler enteisen',
                           defaults={'base_points': 8, 'time_factor': 0.0, 'state': Task.BACKLOG})
        Task.get_or_create(task='Saugen + Wischen',
                           defaults={'base_points': 13, 'time_factor': 0.0, 'state': Task.TODO})
        Task.get_or_create(task='großes Bad',
                           defaults={'base_points': 8, 'time_factor': 0.0, 'state': Task.TODO})
        Task.get_or_create(task='kleines Bad',
                           defaults={'base_points': 3, 'time_factor': 0.0, 'state': Task.DONE})
        Task.get_or_create(task='Rasen mähen + harken',
                           defaults={'base_points': 13, 'time_factor': 0.0, 'state': Task.TODO})
        Task.get_or_create(task='Küche putzen',
                           defaults={'base_points': 2, 'time_factor': 0.0, 'state': Task.DONE})
        Task.get_or_create(task='Abwaschen',
                           defaults={'base_points': 2, 'time_factor': 0.0, 'state': Task.DONE})
        Task.get_or_create(task='Einkaufen',
                           defaults={'base_points': 3, 'time_factor': 0.0, 'state': Task.DONE})
        Task.get_or_create(task='Pappe entsorgen',
                           defaults={'base_points': 2, 'time_factor': 0.0, 'state': Task.DONE})
        Task.get_or_create(task='Müll entsorgen',
                           defaults={'base_points': 1, 'time_factor': 0.0, 'state': Task.DONE})
        Task.get_or_create(task='Glas wegbringen',
                           defaults={'base_points': 2, 'time_factor': 0.0, 'state': Task.DONE})
        Task.get_or_create(task='Geschirrspüler ausräumen',
                           defaults={'base_points': 2, 'time_factor': 0.0, 'state': Task.DONE})


class ModelBase(db_wrapper.Model):
    @classmethod
    def get_all(cls):
        return list(cls.select().dicts())


class User(ModelBase):
    username = CharField(unique=True)
    password = CharField()
    points = IntegerField(default=0)
    last_update = DateTimeField(default=datetime.utcnow)

    @classmethod
    def get_all(cls):
        """
        without password
        :return:
        """
        return list(cls.select(cls.username, cls.points, cls.last_update).dicts())

    @classmethod
    def get_by_name(cls, username):
        try:
            return cls.get(cls.username == username)
        except DoesNotExist:
            return False

    @classmethod
    def get_usernames(cls):
        query = cls.select(cls.username)
        result = set()
        for user in query:
            result.add(user.username)
        return result

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # Flask-Login required functions
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username


class Task(ModelBase):
    task = CharField(unique=True)
    base_points = SmallIntegerField()
    time_factor = FloatField(default=0.0)
    state = SmallIntegerField(index=True, default=0)
    BACKLOG = 0
    TODO = 1
    DONE = 2
    todo_time = DateTimeField(null=True)
    last_done = DateTimeField(null=True)
    schedule_days = SmallIntegerField(null=True)

    @property
    def points(self):
        """
        Calculate real point value based on time_factor.
        :return:
        """
        now = datetime.utcnow()
        # set last_time to now if todo_time is not set.
        last_time = now if not self.todo_time else self.todo_time
        real_points = self.base_points + (self.time_factor * (now - last_time).days)
        return int(real_points)

    @classmethod
    def get_all(cls):
        """
        Overwrite get_all() method because we want to have active tasks only and
        need the property but dicts() doesn't work with it
        :return:
        """
        return list(cls.select().order_by(cls.base_points.desc()))

    @classmethod
    def set_state(cls, task_id, state, user_id):
        now = datetime.utcnow()
        points_obtained = 0
        with db_wrapper.database.atomic():
            # update task state and time
            task = cls.get(cls.id == task_id)
            task.state = state
            if state == cls.DONE:
                points_obtained = task.points
                task.todo_time = None
                task.last_done = now
            elif state == cls.TODO:
                task.todo_time = now
            elif state == cls.BACKLOG:
                task.todo_time = None
            task.save()

            # update user points if new state is DONE (user got points)
            if points_obtained > 0:
                User.update(points=User.points + points_obtained, last_update=now).where(
                    User.id == user_id).execute()

                # add to history
                History.create(task=task.task, user=user_id, points=points_obtained, time=now)

    @classmethod
    def set_todo(cls, task_id):
        now = datetime.utcnow()
        task = cls.get(cls.id == task_id)
        task.state = cls.TODO
        task.todo_time = now
        task.save()

    @classmethod
    def get_schedule_tasks(cls):
        return list(
            cls.select(cls.id, cls.last_done, cls.schedule_days)
                .where((cls.schedule_days.is_null(False)) & (cls.state != cls.TODO)).dicts())

    @staticmethod
    def do_custom_task(task, points, user_id):
        now = datetime.utcnow()
        with db_wrapper.database.atomic():
            # update user points
            User.update(points=User.points + points, last_update=now).where(User.id == user_id).execute()
            # add to history
            History.create(task=task, user=user_id, points=points, time=now)


class History(ModelBase):
    task = CharField()
    user = ForeignKeyField(User)
    points = SmallIntegerField()
    time = DateTimeField(default=datetime.utcnow())

    @classmethod
    def get_user_history(cls, user):
        return list(
            cls.select(cls.time, cls.task, cls.points)
                .join(User, on=(cls.user == User.id))
                .where(User.username == user)
                .order_by(cls.time.desc()).dicts())

    @classmethod
    def get_full_history(cls):
        return list(
            cls.select(cls.time, cls.points, User.username)
                .join(User, on=(cls.user == User.id))
                .order_by(cls.time.asc()).dicts())
