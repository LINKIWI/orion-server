from flask_sqlalchemy import SQLAlchemy

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
        user=database_config['user'],
        password=database_config['password'],
        host=database_config['host'],
        name=database_config['name'],
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    return SQLAlchemy(app, session_options=session_opts)
