# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.interface.common.mapping import IMapping


class IPromises(IMapping):
    """Dictionary like container for named promise functions"""


class IContainsPromises(Interface):
    """Marker interfaces for requests with futures with unresolved futures"""


class IFutures(IMapping):
    """Dictionary like container for futures resolved by futures"""
