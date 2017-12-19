import flask_sqlalchemy

session_opts = {
    'expire_on_commit': False,
}


def DbClient(app, user, password, host, port, name):
    """
    Orion does not need to provide any addition abstractions over the client object created by
    SQLAlchemy. This function directly returns the object instantiated by creating a SQLAlchemy
    object from the current Flask app.

    :param app: Flask application object.
    :param user: The username of the MySQL user.
    :param password: The password of the MySQL user.
    :param host: The host of the MySQL instance.
    :param port: The port of the MySQL instance.
    :param name: The name of the MySQL database.
    :return: A SQLAlchemy object for interacting with the database.
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{user}:{password}@{host}:{port}/{name}'.format(
        user=user,
        password=password,
        host=host,
        port=port,
        name=name,
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    return flask_sqlalchemy.SQLAlchemy(app, session_options=session_opts)
