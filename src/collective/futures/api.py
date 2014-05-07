# -*- coding: utf-8 -*-
import cPickle
from zope.globalrequest import getRequest
from experimental.futures.exceptions import (
    FutureNotResolvedError,
    FutureNotSubmittedError
)
from experimental.futures.interfaces import (
    IFutures,
    IPromises
)

_marker = object()


def result(key, default=_marker):
    """Get the required future result. When the future is not available, return
    the given default or raise KeyError. If the future is an exception, it will
    be raised instead of returned. If the future is a KeyError, it will be
    raised as a value of an Exception instead.
    """
    request = getRequest()

    try:
        value = IFutures(request)[key]
    except KeyError:
        if default is not _marker:
            value = default
        elif key in IPromises(request):
            raise FutureNotResolvedError((
                u"Future '{0:s}' has already been submitted, "
                u"but has not been resolved yet.").format(key))
        else:
            raise FutureNotSubmittedError(
                u"Future '{0:s}' has not been resolved yet.".format(key))

    if isinstance(value, Exception):
        raise value

    return value


def submit(key, fn, *args, **kwargs):
    """Submit promise (name, function, arguments.., keyword arguments...)
    for the default (thread) executor

    """
    request = getRequest()
    IPromises(request)[key] = {
        'fn': fn,
        'args': args,
        'kwargs': kwargs
    }
    return True  # to enable submit(...) and ...


def resultOrSubmit(key, placeholder, fn, *args, **kwargs):
    """Get the required future. When the future is not available,
    submit the given promise and return the given placeholder instead.

    """
    try:
        return result(key)
    except FutureNotSubmittedError:
        submit(key, fn, *args, **kwargs)
    return placeholder


def submitMultiprocess(key, fn, *args, **kwargs):
    """Submit promise (name, function, arguments.., keyword arguments...)
    for the process pool executor.

    Args are pickled, because only pickleable futures can be resolved with
    MultiProcessExecutor and unpickleable args raises an exception, which
    cannot be caught.

    """
    request = getRequest()
    IPromises(request)[key] = cPickle.dumps({
        'fn': fn,
        'args': args,
        'kwargs': kwargs
    })
    return True  # to enable submit(...) and ...


def resultOrSubmitMultiprocess(key, placeholder, fn, *args, **kwargs):
    """Get the required future. When the future is not available,
    submit the given promise and return the given placeholder instead
    (for the process pool executor).

    """
    try:
        return result(key)
    except FutureNotSubmittedError:
        submitMultiprocess(key, fn, *args, **kwargs)
    return placeholder
