import json

import kafka


class StreamClient(object):
    """
    Client for emitting location publish events to a Kafka message broker.
    """

    def __init__(self, kafka_addr, kafka_topic):
        """
        Client for producing location messages to a Kafka broker.

        :param kafka_addr: Address to the Kafka broker.
        :param kafka_topic: Name of the Kafka topic to which messages should be published.
        """
        # Bypass event publishing entirely when no broker address is specified.
        producer_factory = (kafka_addr and kafka.KafkaProducer) or NoopProducer

        self.topic = kafka_topic
        self.producer = producer_factory(
            bootstrap_servers=kafka_addr,
            value_serializer=json.dumps,
        )

    def emit_location(self, location):
        """
        Emit a single location event.

        :param location: Location model instance describing a published location.
        """
        self.producer.send(self.topic, location.serialize())


class NoopProducer(object):
    """
    Kafka producer stub that noops on all operations.
    """

    def __init__(self, *args, **kwargs):
        pass

    def send(self, *args, **kwargs):
        pass
