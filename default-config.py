import os

# Statement for enabling the development environment
DEBUG = False

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with
# SQLite for this example
DATABASE = os.path.join(BASE_DIR, 'chaoswg.sqlite')

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
# THREADS_PER_PAGE = 2

# Note: form CSRF protection is enabled by default in Flask-WTF 1.x
# (the old CSRF_ENABLED config switch was removed); tokens are signed with
# SECRET_KEY (see below).

##########################################################
# Overwrite the following default keys in user-config.py #
##########################################################

# CSRF tokens are signed with WTF_CSRF_SECRET_KEY or, as a fallback,
# SECRET_KEY below (Flask-WTF 1.x no longer reads CSRF_SESSION_KEY).

# Secret key for signing cookies (and CSRF tokens)
SECRET_KEY = "Iq8IBfxayJGLFa70XDHIVqF9g0mLaqv4"

# Invite key is needed for registration
INVITE_KEY = "IWantToHelpNow!!!FZZ§(AfajDJD2djdaFA29da"
