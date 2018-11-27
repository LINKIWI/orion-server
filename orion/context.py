from orion.clients.cache import CacheClient
from orion.clients.config import ConfigClient
from orion.clients.db import DbClient
from orion.clients.geocode import ReverseGeocodingClient
from orion.clients.stream import StreamClient


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
        self.cache = CacheClient(
            addr=self.config.get_value('redis.addr'),
            prefix='orion',
        )
        self.db = DbClient(
            app,
            user=self.config.get_value('database.user'),
            password=self.config.get_value('database.password'),
            host=self.config.get_value('database.host'),
            port=self.config.get_value('database.port'),
            name=self.config.get_value('database.name'),
        )
        self.geocode = ReverseGeocodingClient(
            mapbox_access_token=self.config.get_value('mapbox_access_token'),
        )
        self.stream = StreamClient(
            kafka_addr=self.config.get_value('kafka.addr'),
            kafka_topic=self.config.get_value('kafka.topic'),
        )
