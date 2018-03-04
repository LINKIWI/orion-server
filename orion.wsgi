import logging
import os
import site
import sys

ENV_DIR = 'env'

# Set current working directory
here = os.path.dirname(os.path.abspath(__file__))
os.chdir(here)
sys.path.insert(0, here)

# Add the virtualenv's site-packages
site.addsitedir(os.path.join(here, ENV_DIR, 'local/lib/python2.7/site-packages'))

# Activate the virtualenv
activate_env = os.path.join(here, ENV_DIR, 'bin/activate_this.py')
try:
    execfile(activate_env, dict(__file__=activate_env))
except IOError:
    logging.error("""Orion expects a virtual Python environment in the folder
    `{}/{}`. You can change the ENV_DIR
    variable in `./orion.wsgi` if your environment is located in a different
    folder.""".format(here, ENV_DIR))
    raise

from orion.app import create_app

application = create_app()
