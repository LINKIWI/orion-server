import json
import os

DEFAULT_CONFIG_PATH = '/etc/orion/config.json'


def _get_recursive_config_key(config, key):
    """
    Get the config value identified by the list of nested key values.

    :param config: Configuration dictionary.
    :param key: List of nested keys (in-order) for which the value should be retrieved.
    :return: The value in the configuration dictionary corresponding to the nested key.
    """
    return _get_recursive_config_key(config.get(key[0]), key[1:]) if len(key) else config


def _parse_config_json(path):
    """
    Parse the config file JSON into a Python dictionary.

    :param path: Path to the config file on disk.
    :return: Python dictionary parsed from the JSON config file.
    """
    with open(path, 'r') as config_file:
        return json.loads(config_file.read())


class ConfigParam(object):
    """
    Describes an available configuration parameter.
    """

    def __init__(self, key, default='', required=True, transform=lambda val: val):
        """
        Create a configuration parameter definition.

        :param key: Environment variable corresponding to this config param.
        :param default: Default value.
        :param required: True if the param is required.
        :param transform: Unary function describing how the raw environment variable value should
                          be transformed before use (e.g. typecast).
        """
        self.key = key
        self.default = default
        self.required = required
        self.transform = transform

    def is_env_value_defined(self):
        """
        Check if the config param is defined in the environment.

        :return: True  if the config param is defined in the environment; False otherwise.
        """
        return self.key in os.environ

    def get_env_value(self):
        """
        Retrieve the value of the config param as specified in the environment.

        :return: The value of the config param in the environment if available; None otherwise.
        """
        return self.transform(os.environ.get(self.key))


class ConfigClient(object):
    """
    Client for reading values from the Orion configuration file.
    """

    # Map of available configuration parameters to the equivalent key that might be specified as an
    # environment variable.
    CONFIG_PARAMETERS = {
        'database.host': ConfigParam('DATABASE_HOST', required=True, transform=str),
        'database.port': ConfigParam('DATABASE_PORT', required=True, transform=int),
        'database.name': ConfigParam('DATABASE_NAME', required=True, transform=str),
        'database.user': ConfigParam('DATABASE_USER', required=True, transform=str),
        'database.password': ConfigParam('DATABASE_PASSWORD', required=True, transform=str),
        'frontend_url': ConfigParam('FRONTEND_URL', required=False, transform=str),
    }

    def __init__(self, path=DEFAULT_CONFIG_PATH):
        """
        Create a config reader client. The client will prioritize paths passed via the ORION_CONFIG
        environment variable over those passed as an argument to this client's constructor.

        :param path: Path to the config file.
        """
        required_config_params = [
            param
            for param in self.CONFIG_PARAMETERS.values()
            if param.required
        ]

        if any(not param.is_env_value_defined() for param in required_config_params):
            # At least one required param is not defined in the environment; read the config file on
            # disk and hope that it's defined there
            self.config = _parse_config_json(os.environ.get('ORION_CONFIG', path))

    def get_value(self, key):
        """
        Get the environment or config file configuration value corresponding to an optionally nested
        key. The key may denote nested keys by delimiting them with a single dot (.), e.g.

            config_client.get_value('database.host')

        :param key: String key in the configuration dictionary.
        :return: The value of that key in the configuration dictionary.
        """
        config_param = self.CONFIG_PARAMETERS.get(key)
        if not config_param:
            raise ValueError('Configuration parameter key `{key}` is not recognized!'.format(
                key=key,
            ))

        # Prefer, in order:
        # 1. The value of the config key as defined in the environment
        # 2. The value of the config key as defined in the config file
        # 3. The default value specified in the config param definition
        return config_param.transform(
            (config_param.is_env_value_defined() and config_param.get_env_value()) or
            _get_recursive_config_key(self.config, key.split('.')) or
            config_param.default
        )
