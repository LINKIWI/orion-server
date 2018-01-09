import time
from unittest import TestCase

import mock

from orion.handlers.locations_handler import LocationsHandler
from orion.handlers.locations_handler import NUM_SEC_MONTH
from test.fixtures.location import location_factory


class TestLocationsHandler(TestCase):
    def setUp(self):
        self.mock_ctx = mock.MagicMock()

    def test_metadata(self):
        handler = LocationsHandler(ctx=self.mock_ctx)

        self.assertEqual(handler.methods, ['POST'])
        self.assertEqual(handler.path, '/api/locations')

    @mock.patch.object(time, 'time', return_value=NUM_SEC_MONTH)
    def test_locations_query_valid(self, mock_time):
        mock_locations = [
            location_factory(latitude=1.0, longitude=2.0),
            location_factory(latitude=3.0, longitude=4.0),
            location_factory(latitude=5.0, longitude=6.0),
        ]
        query_chain = self.mock_ctx.db.session.query().filter_by().filter().offset().limit().all
        query_chain.return_value = mock_locations

        mock_data = {
            'user': 'user',
            'device': 'device',
        }

        handler = LocationsHandler(ctx=self.mock_ctx, data=mock_data)
        resp, status = handler.run()
        _, query_filter_by_kwargs = self.mock_ctx.db.session.query().filter_by.call_args

        self.assertTrue(resp['success'])
        self.assertEqual(status, 200)
        self.assertEqual(query_filter_by_kwargs['user'], 'user')
        self.assertEqual(query_filter_by_kwargs['device'], 'device')
        self.assertTrue(mock_time.called)
        self.assertEqual(resp['data'], [location.serialize() for location in mock_locations])
