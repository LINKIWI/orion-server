import json
from unittest import TestCase

import mock

from orion.clients.config import ConfigClient
from orion.clients.config import _get_recursive_config_key

mock_config_file = json.dumps({'config': {'file': [1, 2, 3]}})


class TestConfigClient(TestCase):
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

    @mock.patch(
        '__builtin__.open'.format(__name__),
        mock.mock_open(read_data=mock_config_file),
        create=True,
    )
    def test_parse_config(self):
        instance = ConfigClient()

        self.assertEqual(instance.config, {'config': {'file': [1, 2, 3]}})

    @mock.patch(
        '__builtin__.open'.format(__name__),
        mock.mock_open(read_data=mock_config_file),
        create=True,
    )
    def test_get_value(self):
        instance = ConfigClient()

        self.assertEqual(instance.get_value('config'), {'file': [1, 2, 3]})
        self.assertEqual(instance.get_value('config.file'), [1, 2, 3])
