import json
import os
from unittest import TestCase

import mock

from orion.clients.config import ConfigClient
from orion.clients.config import ConfigParam
from orion.clients.config import _get_recursive_config_key
from orion.clients.config import _parse_config_json

mock_required_config = {
    'config': {
        'file': [1, 2, 3],
    },
    'database': {
        'host': 'localhost',
        'port': 3306,
        'user': 'orion',
        'name': 'orion',
        'password': 'password',
    },
}

mock_optional_config = {
    'frontend_url': 'url',
}


class TestConfigUtils(TestCase):
    def test_get_recursive_config_key(self):
        self.assertEqual(
            _get_recursive_config_key({'config': 1}, ['config']),
            1,
        )
        self.assertEqual(
            _get_recursive_config_key({'config': {'nested': 2}}, ['config', 'nested']),
            2,
        )
        self.assertEqual(
            _get_recursive_config_key({'config': {'nested': 2}}, ['config']),
            {'nested': 2},
        )
        self.assertIsNone(_get_recursive_config_key({}, ['unknown']))

    @mock.patch(
        '__builtin__.open'.format(__name__),
        mock.mock_open(read_data=json.dumps(mock_required_config)),
        create=True,
    )
    def test_parse_config_json(self):
        self.assertEqual(_parse_config_json(''), mock_required_config)


class TestConfigParam(TestCase):
    def setUp(self):
        self.key = 'key'
        self.instance = ConfigParam(self.key, '234', False, int)

        if self.key in os.environ:
            del os.environ[self.key]

    def test_is_env_value_defined(self):
        self.assertFalse(self.instance.is_env_value_defined())
        os.environ[self.key] = '234'
        self.assertTrue(self.instance.is_env_value_defined())

    def test_get_env_value(self):
        os.environ[self.key] = '234'
        self.assertEqual(self.instance.get_env_value(), 234)


class TestConfigClient(TestCase):
    def setUp(self):
        # Clear out environment
        for param in ConfigClient.CONFIG_PARAMETERS.values():
            if param.key in os.environ:
                del os.environ[param.key]

    @mock.patch('__builtin__.open'.format(__name__))
    def test_all_required_in_env(self, mock_open):
        os.environ.update({
            'DATABASE_HOST': 'env_localhost',
            'DATABASE_PORT': '3306',
            'DATABASE_NAME': 'env_orion',
            'DATABASE_USER': 'env_orion',
            'DATABASE_PASSWORD': 'env_password',
        })

        instance = ConfigClient()

        self.assertFalse(mock_open.called)
        self.assertEqual(instance.get_value('database.host'), 'env_localhost')
        self.assertEqual(instance.get_value('database.port'), 3306)
        self.assertEqual(instance.get_value('database.name'), 'env_orion')
        self.assertEqual(instance.get_value('database.user'), 'env_orion')
        self.assertEqual(instance.get_value('database.password'), 'env_password')
        self.assertEqual(instance.get_value('frontend_url'), '*')

    @mock.patch(
        '__builtin__.open'.format(__name__),
        mock.mock_open(read_data=json.dumps(mock_required_config)),
        create=True,
    )
    def test_partial_required_in_env(self):
        os.environ.update({
            'DATABASE_HOST': 'env_localhost',
            'DATABASE_PASSWORD': 'env_password',
        })

        instance = ConfigClient()

        self.assertEqual(instance.get_value('database.host'), 'env_localhost')
        self.assertEqual(instance.get_value('database.port'), 3306)
        self.assertEqual(instance.get_value('database.name'), 'orion')
        self.assertEqual(instance.get_value('database.user'), 'orion')
        self.assertEqual(instance.get_value('database.password'), 'env_password')

    @mock.patch(
        '__builtin__.open'.format(__name__),
        mock.mock_open(read_data=json.dumps(mock_required_config)),
        create=True,
    )
    def test_get_value_unrecognized_param(self):
        instance = ConfigClient()

        self.assertRaises(
            ValueError,
            instance.get_value,
            key='unknown',
        )

    @mock.patch(
        '__builtin__.open'.format(__name__),
        mock.mock_open(read_data=json.dumps(dict(mock_required_config, **mock_optional_config))),
        create=True,
    )
    def test_get_value_optional_param(self):
        instance = ConfigClient()

        self.assertEqual(instance.get_value('frontend_url'), 'url')

    @mock.patch(
        '__builtin__.open'.format(__name__),
        mock.mock_open(read_data=json.dumps(mock_required_config)),
        create=True,
    )
    def test_get_value_default(self):
        instance = ConfigClient()

        self.assertEqual(instance.get_value('frontend_url'), '*')
