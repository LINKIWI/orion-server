from unittest import TestCase

import flask_sqlalchemy
import mock

from orion.clients.db import DbClient


class TestDbClient(TestCase):
    def setUp(self):
        self.mock_app = mock.MagicMock()
        self.mock_database_config = {
            'user': 'user',
            'password': 'password',
            'host': 'host',
            'port': 3306,
            'name': 'name',
        }

    @mock.patch.object(flask_sqlalchemy, 'SQLAlchemy', return_value=5)
    def test_sqlalchemy(self, mock_sqlalchemy):
        instance = DbClient(self.mock_app, self.mock_database_config)
        (app,), kwargs = mock_sqlalchemy.call_args

        self.assertEqual(instance, 5)
        self.assertEqual(app, self.mock_app)
        self.assertEqual(type(kwargs['session_options']), dict)
