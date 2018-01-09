from unittest import TestCase

import mock

from orion.handlers.users_handler import UsersHandler
from orion.models.location import Location


class TestUsersHandler(TestCase):
    def setUp(self):
        self.mock_ctx = mock.MagicMock()

    def test_metadata(self):
        handler = UsersHandler(ctx=self.mock_ctx)

        self.assertEqual(handler.methods, ['GET'])
        self.assertEqual(handler.path, '/api/users')

    def test_results_valid(self):
        self.mock_ctx.db.session.query().distinct().all.return_value = [
            mock.MagicMock(user='user1', device='device1'),
            mock.MagicMock(user='user1', device='device2'),
            mock.MagicMock(user='user1', device='device3'),
            mock.MagicMock(user='user2', device='device4'),
            mock.MagicMock(user='user2', device='device5'),
        ]

        handler = UsersHandler(ctx=self.mock_ctx)
        resp, status = handler.run()
        args, _ = self.mock_ctx.db.session.query.call_args

        self.assertTrue(resp['success'])
        self.assertEqual(status, 200)
        self.assertEqual(
            resp['data'],
            [
                {'user': 'user2', 'devices': ['device4', 'device5']},
                {'user': 'user1', 'devices': ['device1', 'device2', 'device3']},
            ],
        )

    def test_results_empty(self):
        self.mock_ctx.db.session.query().distinct().all.return_value = []

        handler = UsersHandler(ctx=self.mock_ctx)
        resp, status = handler.run()
        args, _ = self.mock_ctx.db.session.query.call_args

        self.assertTrue(resp['success'])
        self.assertEqual(status, 200)
        self.assertEqual(resp['data'], [])
        self.assertEqual(args, (Location.user, Location.device))
