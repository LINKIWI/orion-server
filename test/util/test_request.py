from unittest import TestCase

import mock

from orion.util.request import require_params


class MockHandler(object):
    def __init__(self, data, error):
        self.data = data
        self.error = error

    @require_params('a', 'b')
    def method(self, ret):
        return ret


class TestRequest(TestCase):
    def test_require_params_missing(self):
        mock_error_factory = mock.MagicMock(return_value=False)
        instance = MockHandler(
            data={'a': 4},
            error=mock_error_factory,
        )

        self.assertFalse(instance.method(ret=True))
        _, kwargs = mock_error_factory.call_args
        self.assertEqual(kwargs['data'], ['b'])
        self.assertEqual(kwargs['status'], 400)

    def test_require_params_valid(self):
        mock_error_factory = mock.MagicMock(return_value=False)
        instance = MockHandler(
            data={'a': 4, 'b': 5},
            error=mock_error_factory,
        )

        self.assertTrue(instance.method(ret=True))
        self.assertEqual(mock_error_factory.call_count, 0)
