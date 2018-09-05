# -*- coding: utf-8 -*-
import StringIO
import cPickle
import collections
import logging
import threading
from App.config import getConfiguration
from ZPublisher.Iterators import IStreamIterator
from ZServer.HTTPResponse import ChannelPipe
from ZServer.Producers import iterator_producer
from ZServer.PubCore.ZEvent import Wakeup
from concurrent import futures
from zope.interface import implements
from collective.futures.interfaces import IFutures


logger = logging.getLogger('collective.futures')


def echo(value=None):
    """Dummy replacement for broken futures"""
    return value


def safe_loads(s):
    """Load pickled promise"""
    try:
        return cPickle.loads(s)
    except Exception as e:
        return echo, e


def safe_promise(value):
    """Parse promise value into its fn, args and kwargs"""

    if isinstance(value, dict):
        fn = value.get('fn') or echo
        args = value.get('args') or []
        kwargs = value.get('kwargs') or {}

    elif isinstance(value, collections.Iterable) and len(value):
        fn = value[0] or echo
        args = value[1:]
        kwargs = {}

    else:
        fn = value or echo
        args = []
        kwargs = {}

    return fn or echo, args, kwargs


def safe_submit(executor, value):
    """Parse promise value into its fn, args and kwargs and submit
    it for the given executor"""
    fn, args, kwargs = safe_promise(value)
    return executor.submit(fn, *args, **kwargs)


class zhttp_channel_wrapper(object):

    def __init__(self, channel):
        self._channel = channel

        self._mutex = threading.Lock()
        self._deferred = None
        self._released = False

    def _push(self, producer, send=1):
        self._channel.push(producer, send)

    def push(self, producer, send=1):
        if not isinstance(producer, iterator_producer):
            return  # trash all but promise iterator
        if not isinstance(producer.iterator, PromiseWorkerStreamIterator):
            return  # trash all but promise iterator

        with self._mutex:
            if not self._released:
                self._deferred = (producer, send)
            else:
                self._push(producer, send)

    def release(self):
        with self._mutex:
            if self._deferred is not None:
                self._push(*self._deferred)
            self._released = True
        Wakeup()

    def __getattr__(self, key):
        return getattr(self._channel, key)


def worker(promises, callback):
    # Read the product config
    product_config = getattr(getConfiguration(), 'product_config', {}) or {}
    configuration = product_config.get('collective.promises') or {}
    try:
        max_workers = int(configuration.get('max_workers', 5))
    except ValueError:
        max_workers = 5

    # Resolve promises into futures
    thread_executor = futures.ThreadPoolExecutor(max_workers=max_workers)
    process_executor = futures.ProcessPoolExecutor(max_workers=max_workers)

    futures_to_promises = dict([
        (safe_submit(process_executor, safe_loads(value)), name)
        for name, value in promises.items()
        if isinstance(value, str)
    ])
    logger.debug(
        'multiprocess: {0:s}'.format(', '.join(futures_to_promises.values())))
    futures_to_promises.update(dict([
        (safe_submit(thread_executor, value), name)
        for name, value in promises.items()
        if not isinstance(value, str)
    ]))
    logger.debug(
        'all: {0:s}'.format(', '.join(futures_to_promises.values())))

    for future in futures.as_completed(futures_to_promises):
        promise = futures_to_promises[future]
        try:
            value = future.result()
        except Exception as e:
            logger.exception('Future resolved into exception:')
            value = e
        callback(promise, value)

    process_executor.shutdown(wait=True)
    thread_executor.shutdown(wait=True)


class PromiseWorkerStreamIterator(StringIO.StringIO):

    implements(IStreamIterator)

    def __init__(self, promises, request, response):
        # Mimic 'file' because someone may expect IStreamIterator to be one
        StringIO.StringIO.__init__(self)

        # Reset response
        self._zrequest = request.retry()
        self._zrequest.retry_count -= 1
        self._zrequest.response.stdout = ChannelPipe(response.stdout._request)
        response._retried_response = None

        # Wrap channel
        self._channel = response.stdout._channel
        self._wrapped_channel = zhttp_channel_wrapper(self._channel)
        response.stdout._channel = self._wrapped_channel

        # Enable stream iterator support
        response.setStatus(302)  # required by plone.protect
        response.setHeader('content-length', '0')  # required by ZPublisher

        # Init futures and futures
        self._promises = promises
        self._futures = {}
        self._futures_previous = IFutures(request)

        # Init Lock
        self._mutex = threading.Lock()

        # Fire the worker
        thread = threading.Thread(target=worker,
                                  args=(self._promises, self.record))
        thread.start()

    def record(self, name, value):
        with self._mutex:
            self._futures[name] = value
            if set(self._promises).issubset(set(self._futures)):
                self._wrapped_channel.release()

    def next(self):
        if self._futures:
            IFutures(self._zrequest).update(self._futures)
            IFutures(self._zrequest).update(self._futures_previous)
            self._futures = {}  # mark consumed to raise StopIteration

            from ZServer.PubCore import handle
            handle('Zope2', self._zrequest, self._zrequest.response)
        else:
            raise StopIteration

    def __len__(self):
        return 0  # promise worker cannot return any sane value
