import collections

from orion.handlers.base_handler import BaseHandler
from orion.models.location import Location


class UsersHandler(BaseHandler):
    """
    Query all known users and associated devices.
    """

    methods = ['GET']
    path = '/api/users'

    def run(self, *args, **kwargs):
        def reduction(acc, location):
            acc[location.user].append(location.device)
            return acc

        locations = self.ctx.db.session.query(Location.user, Location.device).distinct().all()
        user_devices = reduce(reduction, locations, collections.defaultdict(list))
        # Reshape from a map of user -> device to an array containing objects with user and devices
        formatted_user_devices = [
            {'user': user, 'devices': devices}
            for user, devices in user_devices.iteritems()
        ]

        self.ctx.metrics_event.emit_event('query_users')

        return self.success(data=formatted_user_devices, status=200)
