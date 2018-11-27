import urllib

import requests


class ReverseGeocodingClient(object):
    """
    Client for looking up the address of a coordinate using the Mapbox API.
    """

    def __init__(self, mapbox_access_token=None):
        """
        Create a reverse geocoding client instance.

        :param mapbox_access_token: Mapbox access token. If not supplied, all reverse geocoding
                                    calls will skip the API call and return None.
        """
        self.mapbox_access_token = mapbox_access_token

    @property
    def _default_params(self):
        return {
            'access_token': self.mapbox_access_token,
        }

    def reverse_geocode(self, lat, lon):
        """
        Look up the formatted address of a coordinate expressed as a latitude and longitude.

        :param lat: Latitude of the coordinate to reverse geocode.
        :param lon: Longitude of the coordinate to reverse geocode.
        :return: Dictionary describing reverse geocode metadata for this coordinate if available;
                 None otherwise.
        """
        data = self._geocode(
            mode='mapbox.places',
            query='{},{}'.format(lon, lat),
            params={'types': 'address'},
        )

        if not data or not data['features']:
            return

        return data['features'][0]

    def _geocode(self, mode, query, params={}):
        """
        Execute a blocking request to the Mapbox geocoding API.

        :param mode: Geocoding mode/endpoint; for V5, one of 'mapbox.places' or 'mapbox.places-permanent'.
        :param query: Geocoding query to perform, as a string.
        :param params: Dictionary of parameters to the endpoint.
        """
        if not self.mapbox_access_token:
            return

        resp = requests.get(
            url='https://api.mapbox.com/geocoding/v5/{mode}/{query}.json?{qs}'.format(
                mode=mode,
                query=query,
                qs=urllib.urlencode(dict(self._default_params, **params)),
            ),
        )

        if resp.status_code == 200:
            return resp.json()
