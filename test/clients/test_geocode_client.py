from unittest import TestCase

import googlemaps
import mock
from googlemaps.exceptions import ApiError

from orion.clients.geocode import ReverseGeocodingClient

# The Google Maps API client library makes sure that the API key is shaped properly, and all keys
# start with this prefix
GOOGLE_API_KEY_PREFIX = 'AIza'


class ReverseGeocodingClientTest(TestCase):
    def setUp(self):
        self.auth_client = ReverseGeocodingClient(GOOGLE_API_KEY_PREFIX)
        self.unauth_client = ReverseGeocodingClient()

    def test_init(self):
        self.assertIsNotNone(self.auth_client.gmaps_client)
        self.assertIsNone(self.unauth_client.gmaps_client)

    @mock.patch.object(googlemaps.Client, 'reverse_geocode')
    def test_reverse_geocode_valid(self, mock_reverse_geocode):
        mock_reverse_geocode.return_value = [
            {'formatted_address': 'address'},
            {'formatted_address': 'less-accurate-address'},
        ]

        result = self.auth_client.reverse_geocode('lat', 'lon')

        self.assertTrue(mock_reverse_geocode.calledWith('lat', 'lon'))
        self.assertEqual(result, 'address')

    @mock.patch.object(googlemaps.Client, 'reverse_geocode')
    def test_reverse_geocode_no_api_key(self, mock_reverse_geocode):
        result = self.unauth_client.reverse_geocode('lat', 'lon')

        self.assertFalse(mock_reverse_geocode.called)
        self.assertIsNone(result)

    @mock.patch.object(googlemaps.Client, 'reverse_geocode', side_effect=ApiError('error'))
    def test_reverse_geocode_api_failure(self, mock_reverse_geocode):
        result = self.auth_client.reverse_geocode('lat', 'lon')

        self.assertTrue(mock_reverse_geocode.calledWith('lat', 'lon'))
        self.assertIsNone(result)
