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

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True


##########################################################
# Overwrite the following default keys in user-config.py #
##########################################################

# Use a secure, unique and absolutely secret key for signing the data
CSRF_SESSION_KEY = "tBhlIlMKzzqK2ml5Dh4bq3D25lA53NZO"

# Secret key for signing cookies
SECRET_KEY = "Iq8IBfxayJGLFa70XDHIVqF9g0mLaqv4"

# Invite key is needed for registration
INVITE_KEY = "IWantToHelpNow!!!FZZ§(AfajDJD2djdaFA29da"
