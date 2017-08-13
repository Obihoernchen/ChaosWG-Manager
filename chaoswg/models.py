from datetime import datetime

from peewee import (CharField, IntegerField, DateTimeField, SmallIntegerField, ForeignKeyField,
                    FloatField, BooleanField, DoesNotExist)
from playhouse.flask_utils import FlaskDB
from werkzeug.security import generate_password_hash, check_password_hash

db_wrapper = FlaskDB()


def init_database(app):
    db_wrapper.init_app(app)
    return db_wrapper.database


def create_tables():
    db_wrapper.database.connect()
    db_wrapper.database.create_tables([User, Room, Task, History], safe=True)
    db_wrapper.database.close()


def insert_testdata():
    pwhash = generate_password_hash('123456')
    with db_wrapper.database.atomic():
        # User.get_or_create(username='User1', defaults={'password': pwhash})
        # User.get_or_create(username='User2', defaults={'password': pwhash})
        # User.get_or_create(username='User3', defaults={'password': pwhash})
        # User.get_or_create(username='User4', defaults={'password': pwhash})
        # User.get_or_create(username='User5', defaults={'password': pwhash})

        Room.get_or_create(room='Bibliothek')
        Room.get_or_create(room='Flur')
        Room.get_or_create(room='Küche')
        Room.get_or_create(room='großes Bad')
        Room.get_or_create(room='kleines Bad')
        Room.get_or_create(room='Abstellzimmer')
        Room.get_or_create(room='Dachterrasse')

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
        Task.get_or_create(task='GS ausräumen',
                           defaults={'base_points': 2, 'time_factor': 0.0, 'state': Task.DONE})


class BaseModel(db_wrapper.Model):
    @classmethod
    def get_all(cls):
        return list(cls.select().dicts())


class User(BaseModel):
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


class Room(db_wrapper.Model):
    room = CharField(unique=True)


class Task(BaseModel):
    task = CharField(unique=True)
    base_points = SmallIntegerField()
    time_factor = FloatField(default=0.0)
    state = SmallIntegerField(index=True, default=0)
    BACKLOG = 0
    TODO = 1
    DONE = 2
    room = ForeignKeyField(Room, null=True)
    todo_time = DateTimeField(null=True)
    last_done = DateTimeField(null=True)

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
    def set_state(cls, id, state, user_id):
        # TODO db.atomic?
        # update task state and time
        task = cls.get(cls.id == id)
        # do not update if state doesn't change. Actually allow this again
        # if task.state != state:
        now = datetime.utcnow()
        task.state = state
        points_obtained = 0
        if state == cls.DONE:
            points_obtained = task.points
            task.last_done = now
        elif state == cls.TODO:
            task.todo_time = now
        task.save()

        # update user points if new state is DONE (user got points)
        if points_obtained > 0:
            User.update(points=User.points + points_obtained, last_update=now).where(
                User.id == user_id).execute()

            # add to history
            History.create(task=task.task, user=user_id, points=points_obtained, time=now)

    @staticmethod
    def do_custom_task(task, points, user_id):
        now = datetime.utcnow()
        # update user points
        User.update(points=User.points + points, last_update=now).where(User.id == user_id).execute()
        # add to history
        History.create(task=task, user=user_id, points=points, time=now)


class History(BaseModel):
    task = CharField()
    user = ForeignKeyField(User)
    points = SmallIntegerField()
    time = DateTimeField(default=datetime.utcnow())

    @classmethod
    def get_user_history(cls, user):
        return list(
            cls.select(cls.time, cls.task, cls.points)
                .join(User, on=(cls.user == User.id))
                .where(User.username == user).dicts())
