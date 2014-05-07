# -*- coding: utf-8 -*-


class FuturesException(Exception):
    """Futures related exception"""


class FutureNotSubmittedError(FuturesException):
    """Requested future has not yet been submitted"""


class FutureNotResolvedError(FuturesException):
    """Requested future has not yet been resolved"""
