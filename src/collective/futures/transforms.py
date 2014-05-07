# -*- coding: utf-8 -*-
import transaction

from zope.interface import Interface
from zope.component import adapts
from plone.transformchain.interfaces import ITransform
from zope.interface import implements

from collective.futures.interfaces import (
    IContainsPromises,
    IPromises
)
from collective.futures.iterators import PromiseWorkerStreamIterator


class PromisesTransform(object):
    implements(ITransform)
    adapts(Interface, IContainsPromises)

    order = 7000  # before p.a.theming and p.a.blocks

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def transformString(self, result, encoding):
        return self.transformIterable([result], encoding)

    def transformUnicode(self, result, encoding):
        return self.transformIterable([result], encoding)

    def transformIterable(self, result, encoding):
        if IPromises(self.request):
            transaction.abort()  # apparently safe in IPubBeforeCommitEvent
            return PromiseWorkerStreamIterator(
                IPromises(self.request), self.request, self.request.response)
        else:
            return None
