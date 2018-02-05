import sys
import logging

# If you use a virtualenv uncomment the following lines
#activate_this = '/path/to/env/bin/activate_this.py'
#with open(activate_this) as file_:
#    exec(file_.read(), dict(__file__=activate_this))

logging.basicConfig(stream=sys.stderr)

# Set your path here
sys.path.insert(0,"/srv/ChaosWG-Manager/")

from chaoswg import app as application
