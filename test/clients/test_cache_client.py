import redis
from redis.exceptions import ConnectionError
from unittest import TestCase
import mock
import time

from orion.clients import cache
from orion.clients.cache import CacheException
from orion.clients.cache import MemoryTTLCache
from orion.clients.cache import RedisProxyClient
from orion.clients.cache import CacheClient


class TestMemoryTTLCache(TestCase):
    def setUp(self):
        self.cache = MemoryTTLCache()

    def test_get_nonexistent(self):
        self.assertIsNone(self.cache.get('key'))

    def test_set_get_within_ttl(self):
        with self._patch_time(1):
            self.cache.set('key', 'value', 1000)
            self.assertEqual(self.cache.get('key'), 'value')

    def test_set_get_past_ttl(self):
        with self._patch_time(1):
            self.cache.set('key', 'value', 1000)

        with self._patch_time(3):
            self.assertIsNone(self.cache.get('key'))

    def test_delete_within_ttl(self):
        with self._patch_time(1):
            self.cache.set('key', 'value', 1000)
            self.assertEqual(self.cache.get('key'), 'value')
            self.cache.delete('key')
            self.assertIsNone(self.cache.get('key'))

    def test_delete_past_ttl(self):
        with self._patch_time(1):
            self.cache.set('key', 'value', 1000)

        with self._patch_time(3):
            self.cache.delete('key')
            self.assertIsNone(self.cache.get('key'))

    @staticmethod
    def _patch_time(timestamp):
        return mock.patch.object(time, 'time', return_value=timestamp)


class TestRedisProxyClient(TestCase):
    @mock.patch.object(redis, 'Redis')
    def setUp(self, *args):
        self.cache = RedisProxyClient('localhost:6379')

    def test_get_redis(self):
        self.cache.redis.get.return_value = 'redis'

        self.assertEqual(self.cache.get('key'), 'redis')
        self.cache.redis.get.assert_called_with('key')

    def test_get_failover(self):
        self.cache.redis.get.return_value = 'redis'
        self.cache.redis.get.side_effect = ConnectionError

        self.assertNotEqual(self.cache.get('key'), 'redis')
        self.cache.redis.get.assert_called_with('key')

    def test_set_memory_dark_write(self):
        self.cache.set('key', 'value', 1000)
        self.cache.redis.set.assert_called_with('key', 'value', px=1000)

        self.cache.redis.set.side_effect = ConnectionError
        self.cache.set('key', 'value', 1000)

    def test_delete_memory_dark_write(self):
        self.cache.delete('key')
        self.cache.redis.delete.assert_called_with('key')

        self.cache.redis.delete.side_effect = ConnectionError
        self.cache.delete('key')


class TestCacheClient(TestCase):
    @mock.patch.object(cache, 'MemoryTTLCache')
    @mock.patch.object(cache, 'RedisProxyClient')
    def setUp(self, *args):
        self.redis_client = CacheClient('localhost:6379', 'prefix')
        self.memory_client = CacheClient(None, 'prefix')

    def test_rw_client(self):
        rw_client = self.redis_client.rw_client('namespace', 'key')

        rw_client.get()
        self.redis_client.backend.get.assert_called_with(key='prefix:namespace:key:')

        rw_client.set('value', 1000)
        self.redis_client.backend.set.assert_called_with(
            key='prefix:namespace:key:',
            value='value',
            ttl=1000,
        )

        rw_client.delete()
        self.redis_client.backend.delete.assert_called_with(key='prefix:namespace:key:')

    def test_format_key_valid(self):
        self.assertEqual(
            self.redis_client._format_key('namespace', 'key', {'a': 'b', 'c': 4}),
            'prefix:namespace:key:a=b&c=4',
        )

    def test_format_key_invalid(self):
        self.assertRaises(
            CacheException,
            self.redis_client._format_key,
            namespace='namespace',
            key='key',
            tags={'a': '='},
        )
