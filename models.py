from datetime import datetime
from peewee import *
from playhouse.flask_utils import FlaskDB

DATABASE = 'chaoswg.sqlite'

flaskDb = FlaskDB()


def init_database(app):
    db = SqliteDatabase(DATABASE)
    app.config['DATABASE'] = db
    flaskDb.init_app(app)
    return db


def create_tables(db):
    db.connect()
    db.create_tables([User, Room, Task, History], safe=True)
    db.close()


def insert_testdata(db):
    with db.atomic():
        User.get_or_create(username='User1')
        User.get_or_create(username='User2')
        User.get_or_create(username='User3')
        User.get_or_create(username='User4')
        User.get_or_create(username='User5')

        Room.get_or_create(room='Bibliothek')
        Room.get_or_create(room='Flur')
        Room.get_or_create(room='Küche')
        Room.get_or_create(room='großes Bad')
        Room.get_or_create(room='kleines Bad')
        Room.get_or_create(room='Abstellzimmer')
        Room.get_or_create(room='Dachterasse')

        Task.get_or_create(task='Kühlschrankcheck', base_points=2, state=Task.BACKLOG)
        Task.get_or_create(task='Grünabfall', base_points=1, state=Task.BACKLOG)
        Task.get_or_create(task='Fenster putzen', base_points=3, state=Task.BACKLOG)
        Task.get_or_create(task='Ofen reinigen', base_points=5, state=Task.BACKLOG)
        Task.get_or_create(task='Tiefkühler enteisen', base_points=8, state=Task.BACKLOG)
        Task.get_or_create(task='Saugen + Wischen', base_points=13, state=Task.TODO)
        Task.get_or_create(task='Holzstuhl entsorgen', base_points=2, state=Task.TODO)
        Task.get_or_create(task='großes Bad', base_points=8, state=Task.TODO)
        Task.get_or_create(task='kleines Bad', base_points=3, state=Task.DONE)
        Task.get_or_create(task='Rasen mähen + harken', base_points=13, state=Task.TODO)
        Task.get_or_create(task='Küche putzen', base_points=3, state=Task.DONE)
        Task.get_or_create(task='Abwaschen', base_points=2, state=Task.DONE)
        Task.get_or_create(task='Einkaufen', base_points=3, state=Task.DONE)
        Task.get_or_create(task='Pappe entsorgen', base_points=2, state=Task.DONE)
        Task.get_or_create(task='Müll entsorgen', base_points=1, state=Task.DONE)
        Task.get_or_create(task='Glas wegbringen', base_points=2, state=Task.DONE)
        Task.get_or_create(task='GS ausräumen', base_points=2, state=Task.DONE)


class BaseModel(flaskDb.Model):
    @classmethod
    def get_all(cls):
        # return [m for m in cls.select().dicts()]
        return list(cls.select().dicts())


class User(BaseModel):
    username = CharField(unique=True)
    points = IntegerField(default=0)
    last_update = DateTimeField(default=datetime.utcnow)


class Room(flaskDb.Model):
    room = CharField(unique=True)


class Task(BaseModel):
    task = CharField(unique=True)
    base_points = SmallIntegerField()
    time_factor = FloatField(default=0.0)
    state = SmallIntegerField(index=True, default=0, constraints=([Check('state >= 0'), Check('state <= 2')]))
    BACKLOG = 0
    TODO = 1
    DONE = 2
    room = ForeignKeyField(Room, null=True)
    last_done = DateTimeField(null=True)

    @property
    def points(self):
        """
        Calculate real point value based on time_factor.
        :return:
        """
        now = datetime.utcnow()
        # set last_time to now if last_done is not set.
        last_time = now if not self.last_done else self.last_done
        real_points = self.base_points + (self.time_factor * (now - last_time).days)
        return int(real_points)

    @classmethod
    def get_all(cls):
        """
        Overwrite get_all() method because we need the property and dicts() doesn't
        work with it
        :return:
        """
        return list(cls.select())

    # @staticmethod
    # def get_tasks(state):
    #    return list(Task.select().where(Task.state == state).dicts())

    @staticmethod
    def set_state(id, state, user_id):
        # TODO with db.atomic
        # update task state and time
        task = Task.get(Task.id == id)
        task.state = state
        points_obtained = 0
        if state == Task.DONE:
            points_obtained = task.points
            task.last_done = datetime.utcnow()
        task.save()

        # update user points if new state is DONE
        if points_obtained > 0:
            User.update(points=User.points + points_obtained).where(User.id == user_id).execute()

            # add to history
            History.create(task=task.id, user=user_id, points=points_obtained)


class History(BaseModel):
    task = ForeignKeyField(Task)
    user = ForeignKeyField(User)
    points = SmallIntegerField()
    time = DateTimeField(default=datetime.utcnow())

    @staticmethod
    def get_user_history(user):
        return list(
            History.select(History.time, Task.task, History.points)
                .join(User, on=(History.user == User.id))
                .join(Task, on=(History.task == Task.id))
                .where(User.username == user).dicts())
