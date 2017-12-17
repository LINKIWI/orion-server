import time

from sqlalchemy import and_

from orion.handlers.base_handler import BaseHandler
from orion.models.location import Location
from orion.util.request import require_params

# Number of seconds in a month.
NUM_SEC_MONTH = 31 * 24 * 3600


class LocationsHandler(BaseHandler):
    """
    Query location data reported for a user and device.

    The client must specify the following JSON parameters:
        user -- The username for which entries should be fetched
        device -- The corresponding device name for which entries should be fetched

    The client may optionally specify the following JSON parameters:
        offset -- An offset to apply to the selection (default 0)
        limit -- A limit of entries to return (default 10)
        timestamp_start -- The starting Unix timestamp for fetched entries (default a month ago)
        timestamp_end -- The ending Unix timestamp for fetched entries (default now)
    """

    methods = ['POST']
    path = '/api/locations'

    @require_params('user', 'device')
    def run(self, *args, **kwargs):
        offset = self.data.get('offset', 0)
        limit = self.data.get('limit', 10)
        timestamp_start = self.data.get('timestamp_start', int(time.time()) - NUM_SEC_MONTH)
        timestamp_end = self.data.get('timestamp_end', int(time.time()))

        locations = self.ctx.db.session.query(Location).filter_by(
            user=self.data['user'],
            device=self.data['device'],
        ).filter(
            and_(Location.timestamp > timestamp_start, Location.timestamp < timestamp_end)
        ).offset(
            offset
        ).limit(
            limit
        ).all()

        serialized_locations = [
            location.serialize()
            for location in locations
        ]

        return self.success(data=serialized_locations, status=200)
