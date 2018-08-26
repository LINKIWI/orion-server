from unittest import TestCase

import kafka
import mock

from orion.clients.stream import NoopProducer
from orion.clients.stream import StreamClient
from orion.models.location import Location


class StreamClientTest(TestCase):
    def setUp(self):
        self.mock_location = Location(
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

    @mock.patch.object(kafka, 'KafkaProducer')
    def test_init_kafka_producer(self, mock_producer):
        client = StreamClient(kafka_addr='addr', kafka_topic='topic')

        self.assertTrue(mock_producer.called)
        self.assertEqual(client.topic, 'topic')

    @mock.patch.object(kafka, 'KafkaProducer')
    def test_init_noop_producer(self, mock_producer):
        client = StreamClient(kafka_addr=None, kafka_topic='topic')

        self.assertFalse(mock_producer.called)
        self.assertEqual(client.topic, 'topic')

    @mock.patch.object(kafka, 'KafkaProducer')
    def test_emit_location(self, mock_producer):
        client = StreamClient(kafka_addr='addr', kafka_topic='topic')
        resp = client.emit_location(self.mock_location)

        self.assertTrue(mock_producer().send.calledWith('topic', self.mock_location))
        self.assertIsNone(resp)

    def test_noop_producer(self):
        producer = NoopProducer()

        self.assertIsNone(producer.send())
        self.assertIsNone(producer.send(1, 2, 3))
