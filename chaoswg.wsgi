import sys
import logging

# If you use a virtualenv uncomment the following lines
#activate_this = '/path/to/env/bin/activate_this.py'
#with open(activate_this) as file_:
#    exec(file_.read(), dict(__file__=activate_this))

logging.basicConfig(stream=sys.stderr)

from chaoswg import app as application
from chaoswg import task_scheduler

# Production entry point: start the scheduler here (once per process). The
# dev entry point run.py starts it in the reloader's child process only.
task_scheduler.start()
