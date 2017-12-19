from orion.clients.config import ConfigClient
from orion.clients.db import DbClient


class Context(object):
    """
    Global application context containing all necessary clients.
    """

    def __init__(self, app):
        """
        Create an application context object,

        :param app: Flask application instance.
        """
        self.config = ConfigClient()
        self.db = DbClient(
            app,
            user=self.config.get_value('database.user'),
            password=self.config.get_value('database.password'),
            host=self.config.get_value('database.host'),
            port=self.config.get_value('database.port'),
            name=self.config.get_value('database.name'),
        )
