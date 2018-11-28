import socket
import time

import statsd


class MetricsClient(object):
    """
    Abstractions over statsd metrics emissions.
    """

    def __init__(self, addr, prefix):
        """
        Create a client instance.

        :param addr: IPv4 address of the statsd server.
        :param prefix: String prefix for all emitted metrics.
        """
        self.hostname = socket.gethostname()

        if addr:
            ip, port = addr.split(':')
            self.backend = statsd.StatsClient(ip, int(port), prefix=prefix)
        else:
            self.backend = NoopStatsdClient()

    @property
    def _default_tags(self):
        """
        Default tags to include with every metrics emission.

        :return: Dictionary of default tags.
        """
        return {
            'host': self.hostname,
        }

    @staticmethod
    def _format_metric(metric, tags, tag_delimiter='='):
        """
        Format a metric name to include InfluxDB-style tags.

        :param metric: Metric name.
        :param tags: Dictionary of tags.
        :param tag_delimiter: Tag key-value delimiter; defaults to '=' for InfluxDB-style metrics.
                              Use ':' for Datadog-style metrics.
        :return: Formatted metric name.
        """
        if not tags:
            return metric

        serialized_tags = ','.join(
            '{}{}{}'.format(key, tag_delimiter, value)
            for key, value in tags.iteritems()
        )

        return '{},{}'.format(metric, serialized_tags)


class NoopStatsdClient(object):
    """
    Null object implementing the statsd client interface to noop on all metrics emissions.
    """

    def gauge(self, *args, **kwargs):
        pass

    def incr(self, *args, **kwargs):
        pass

    def timing(self, *args, **kwargs):
        pass


class EventMetricsClient(MetricsClient):
    """
    Metrics client that provides imperative APIs for emitting metrics when events occur.
    """

    def emit_event(self, metric, tags={}):
        """
        Emit a record of an event occurrence. Semantically, the value of this event is monotonically
        increasing.

        :param metric: Metric name.
        :param tags: Dictionary of additional tags to include.
        """
        self.backend.incr(self._format_metric(
            metric='event.{}'.format(metric),
            tags=dict(self._default_tags, **tags),
        ))


class LatencyMetricsClient(MetricsClient):
    """
    Metrics client that provides APIs for measuring latency of operations.
    """

    def profile(self, metric, tags={}):
        """
        Create a context manager for emitting a timing metric describing the latency of an
        operation.

        :param metric: Metric name.
        :param tags: Dictionary of additional tags to include.s
        :return: Context manager for measuring execution duration and emitting metrics.
        """
        def emission_proxy(duration):
            self.backend.timing(
                stat=self._format_metric(
                    metric='latency.{}'.format(metric),
                    tags=dict(self._default_tags, **tags),
                ),
                delta=duration,
            )

        return ExecutionTimer(emission_proxy)


class ExecutionTimer(object):
    """
    Context manager for timing an execution duration.
    """

    def __init__(self, duration_cb):
        """
        Create a context manager instance.

        :param duration_cb: Callback function invoked with the duration, in milliseconds, of the
                            context manager body when complete.
        """
        self.duration_cb = duration_cb

    def __enter__(self):
        self.start_ms = 1000.0 * time.time()

    def __exit__(self, *args, **kwargs):
        end_ms = 1000.0 * time.time()

        self.duration_cb(end_ms - self.start_ms)
