import os

import flask_sqlalchemy

session_opts = {
    'expire_on_commit': False,
}


def DbClient(app, database_config):
    """
    Orion does not need to provide any addition abstractions over the client object created by
    SQLAlchemy. This function directly returns the object instantiated by creating a SQLAlchemy
    object from the current Flask app.

    :param app: Flask application object.
    :param database_config: Dictionary describing the database configuration details.
    :return: A SQLAlchemy object for interacting with the database.
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{user}:{password}@{host}/{name}'.format(
        user=os.environ.get('DATABASE_USER', database_config['user']),
        password=os.environ.get('DATABASE_PASSWORD', database_config['password']),
        host=os.environ.get('DATABASE_HOST', database_config['host']),
        name=os.environ.get('DATABASE_NAME', database_config['name']),
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    return flask_sqlalchemy.SQLAlchemy(app, session_options=session_opts)
