# This should be used for development/debugging purposes only
# Use a proper WSGI server for production use

import os

from chaoswg import app, task_scheduler

if __name__ == '__main__':
    # debug=True always enables the Werkzeug reloader, which executes this
    # file twice: in the parent (watchdog) process and in the child that
    # serves requests. Only the child (marked by WERKZEUG_RUN_MAIN) starts
    # the scheduler, otherwise every scheduled job would run twice.
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        task_scheduler.start()
    app.run(host='127.0.0.1', port=5000, debug=True)
