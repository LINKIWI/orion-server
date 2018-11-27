import json

from flask import request

from orion.handlers.base_handler import BaseHandler
from orion.models.location import Location


class PublishHandler(BaseHandler):
    """
    Add an entry to the database for every reported location. This API is compliant with the JSON
    payload shipped by the official Android OwnTracks client, the definition of which is described
    here: http://owntracks.org/booklet/tech/json/

    Note that this endpoint itself does not concern itself with authenticating requests or users.
    It is expected that this authentication occurs at the web server (Apache/nginx) level; by the
    time a request reaches this service, it is assumed that the requesting user is valid and
    permitted to access this resource.
    """

    methods = ['POST']
    path = '/api/publish'

    def run(self, *args, **kwargs):
        # Sometimes the client tries to send a reportLocation cmd. If server
        # responds with non-200, all further location updates get backed up behind it.
        # Handle with empty 200 response
        if self.data['_type'] == 'cmd' and self.data['action'] == 'reportLocation':
            return self.success(status=200)

        if self.data['_type'] != 'location':
            return self.error(status=400, message='Not a location publish.')

        if self.data.get('topic'):
            _, user, device = self.data.get('topic').split('/')
        else:
            user = request.headers.get('X-Limit-U')
            device = request.headers.get('X-Limit-D')

        lat = self.data.get('lat')
        lon = self.data.get('lon')
        address = self._extract_address(lat, lon)

        location = Location(
            timestamp=self.data.get('tst'),
            user=user,
            device=device,
            latitude=lat,
            longitude=lon,
            accuracy=self.data.get('acc'),
            battery=self.data.get('batt'),
            trigger=self.data.get('t'),
            connection=self.data.get('conn'),
            tracker_id=self.data.get('tid'),
            address=address,
        )

        self.ctx.db.session.add(location)
        self.ctx.db.session.commit()

        self.ctx.stream.emit_location(location)

        return self.success(status=201)

    def _extract_address(self, lat, lon):
        """
        Extract a reverse geocoded address from a (latitude, longitude) coordinate, fronted by a
        cache keyed by the coordinate itself.

        :param lat: Latitude of the coordinate.
        :param lon: Longitude of the coordinate.
        :return: String representation of the coordinate's address.
        """
        def approx_coord(coord):
            # Reduce the precision of the coordinate for purposes of the cache key, in an effort to
            # approximately cluster coordinates within a small area to the same reverse-geocoded
            # address. This helps reduce API QPS to Mapbox, since coordinates within a few meters
            # of one another will likely resolve to the same address anyway.
            return int(round(coord / 10e-6))

        cache = self.ctx.cache.rw_client(
            namespace='publish',
            key='reverse-geocode-feature',
            tags={'lat': approx_coord(lat), 'lon': approx_coord(lon)},
        )

        cached_feature = cache.get()
        if cached_feature is None:
            feature = self.ctx.geocode.reverse_geocode(lat, lon)
            if not feature:
                return

            cache.set(json.dumps(feature), ttl=24 * 60 * 60 * 1000)  # 24 hour cache TTL
            return self._extract_address(lat, lon)

        return json.loads(cached_feature).get('place_name')
