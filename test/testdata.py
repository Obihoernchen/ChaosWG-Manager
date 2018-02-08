from werkzeug.security import generate_password_hash

from chaoswg import Task, User


def insert_testdata(database):
    pwhash = generate_password_hash('123456')
    with database.atomic():
        User.get_or_create(username='User1', defaults={'password': pwhash})
        User.get_or_create(username='User2', defaults={'password': pwhash})
        User.get_or_create(username='User3', defaults={'password': pwhash})
        User.get_or_create(username='User4', defaults={'password': pwhash})
        User.get_or_create(username='User5', defaults={'password': pwhash})

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