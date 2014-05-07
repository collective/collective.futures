# -*- coding: utf-8 -*-
from zope.annotation import (
    IAnnotations,
    IAttributeAnnotatable
)
from zope.component import adapter
from zope.interface import (
    implementer,
    alsoProvides
)

from collective.futures.interfaces import (
    IPromises,
    IFutures,
    IContainsPromises
)


PROMISES_KEY = 'collective.promises'
FUTURES_KEY = 'collective.futures.futures'


@implementer(IPromises)
@adapter(IAttributeAnnotatable)
def get_promises(request):
    alsoProvides(request, IContainsPromises)
    annotations = IAnnotations(request)
    annotations.setdefault(PROMISES_KEY, {})
    return annotations.get(PROMISES_KEY)


@implementer(IFutures)
@adapter(IAttributeAnnotatable)
def get_futures(request):
    annotations = IAnnotations(request)
    annotations.setdefault(FUTURES_KEY, {})
    return annotations.get(FUTURES_KEY)
