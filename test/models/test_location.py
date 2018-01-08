from unittest import TestCase

from orion.models.location import Location


class TestLocation(TestCase):
    def setUp(self):
        self.instance = Location(
            timestamp=1,
            user='user',
            device='device',
            latitude=1.0,
            longitude=2.0,
            accuracy=10,
            battery=100,
            trigger='u',
            connection='m',
            tracker_id='tr',
            address='12345 Orion Rd',
        )

    def test_init(self):
        self.assertEqual(self.instance.timestamp, 1)
        self.assertEqual(self.instance.user, 'user')
        self.assertEqual(self.instance.device, 'device')
        self.assertEqual(self.instance.latitude, 1.0)
        self.assertEqual(self.instance.longitude, 2.0)
        self.assertEqual(self.instance.accuracy, 10)
        self.assertEqual(self.instance.battery, 100)
        self.assertEqual(self.instance.trigger, 'u')
        self.assertEqual(self.instance.connection, 'm')
        self.assertEqual(self.instance.tracker_id, 'tr')
        self.assertEqual(self.instance.address, '12345 Orion Rd')

    def test_serialize_full(self):
        self.assertEqual(self.instance.serialize(), {
            'location_id': None,
            'timestamp': 1,
            'user': 'user',
            'device': 'device',
            'latitude': 1.0,
            'longitude': 2.0,
            'accuracy': 10,
            'battery': 100,
            'connection': 'm',
            'tracker_id': 'tr',
            'address': '12345 Orion Rd',
        })

    def test_serialize_fields_filter(self):
        self.assertEqual(self.instance.serialize(['timestamp', 'latitude']), {
            'timestamp': 1,
            'latitude': 1.0,
        })
