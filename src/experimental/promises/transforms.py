# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.component import adapts
from plone.transformchain.interfaces import ITransform
from zope.interface import implements

from experimental.promises.interfaces import (
    IContainsPromises,
    IPromises
)
from experimental.promises.iterators import PromiseWorkerStreamIterator


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
            return PromiseWorkerStreamIterator(
                IPromises(self.request), self.request, self.request.response)
        else:
            return None
