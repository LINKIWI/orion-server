import os
import json

DEFAULT_CONFIG_PATH = '/etc/orion/config.json'


def _get_recursive_config_key(config, key):
    """
    Get the config value identified by the list of nested key values.

    :param config: Configuration dictionary.
    :param key: List of nested keys (in-order) for which the value should be retrieved.
    :return: The value in the configuration dictionary corresponding to the nested key.
    """
    return _get_recursive_config_key(config[key[0]], key[1:]) if len(key) else config


class ConfigClient(object):
    """
    Client for reading values from the Orion configuration file.
    """

    def __init__(self, path=DEFAULT_CONFIG_PATH):
        """
        Create a config reader client. The client will prioritize paths passed via the ORION_CONFIG
        environment variable over those passed as an argument to this client's constructor.

        :param path: Path to the config file.
        """
        self.path = os.environ.get('ORION_CONFIG', path)
        self.config = self._parse_config()

    def get_value(self, key):
        """
        Get the JSON-parsed configuration value corresponding to an optionally nested key. The key
        may denote nested keys by delimiting them with a single dot (.), e.g.

            config_client.get_value('database.host')

        :param key: String key in the configuration dictionary.
        :return: The value of that key in the configuration dictionary.
        """
        return _get_recursive_config_key(self.config, key.split('.'))

    def _parse_config(self):
        """
        Parse the config file JSON into a Python dictionary.

        :return: Python dictionary parsed from the JSON config file.
        """
        with open(self.path, 'r') as config_file:
            return json.loads(config_file.read())
