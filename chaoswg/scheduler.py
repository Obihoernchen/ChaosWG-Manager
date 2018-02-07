import threading
import time
from datetime import datetime

import schedule

from chaoswg import Task


class TaskScheduler(threading.Thread):

    def __init__(self, interval=60):
        # init a daemonized thread
        threading.Thread.__init__(self, daemon=True)
        self.interval = interval
        # register the schedule every day at 5 o'clock
        schedule.every().day.at('5:00').do(self.schedule_tasks)

    @staticmethod
    def schedule_tasks():
        now = datetime.utcnow()
        schedule_tasks = Task.get_schedule_tasks()

        for task in schedule_tasks:
            if task['last_done'] is not None:
                delta = now - task['last_done']
                if delta.days >= task['schedule_days']:
                    Task.set_todo(task['id'])
            else:
                # Task was not done yet
                Task.set_todo(task['id'])

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(self.interval)
