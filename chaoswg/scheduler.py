import time
import schedule
import threading
from datetime import datetime

from chaoswg import Task


class TaskScheduler():
    INTERVAL = 60

    def __init__(self):
        schedule.every().day.at('5:00').do(self.schedule_tasks)

        schedule_thread = threading.Thread(target=self.__run, daemon=True)
        schedule_thread.start()

    @staticmethod
    def schedule_tasks():
        now = datetime.utcnow()
        schedule_tasks = Task.get_schedule_tasks()

        for task in schedule_tasks:
            if task['last_done'] is not None:
                delta = now - task['last_done']
                if delta.days() >= task['schedule_days']:
                    Task.set_todo(task['id'])
            else:
                # Task was not done yet
                Task.set_todo(task['id'])

    @classmethod
    def __run(cls):
        while True:
            schedule.run_pending()
            time.sleep(cls.INTERVAL)
