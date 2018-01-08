from unittest import TestCase

from orion.handlers.base_handler import BaseHandler


class TestBaseHandler(TestCase):
    def setUp(self):
        self.instance = BaseHandler(ctx={}, data={})

    def test_init(self):
        self.assertIsNotNone(self.instance.ctx)
        self.assertIsNotNone(self.instance.data)
        self.assertIsNotNone(self.instance.methods)
        self.assertIsNone(self.instance.path)

    def test_success(self):
        self.assertEqual(
            self.instance.success({'data': True}, 201),
            ({'success': True, 'message': None, 'data': {'data': True}}, 201),
        )

    def test_error(self):
        self.assertEqual(
            self.instance.error({'data': True}, 502, 'oh noes'),
            ({'success': False, 'message': 'oh noes', 'data': {'data': True}}, 502),
        )

    def test_run(self):
        self.assertRaises(
            NotImplementedError,
            self.instance.run,
        )
