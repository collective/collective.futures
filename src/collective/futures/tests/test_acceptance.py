# -*- coding: utf-8 -*- #
import logging
import threading
import unittest

from Products.Five.browser import BrowserView

import robotsuite
from plone.testing import layered
from zope.interface import noLongerProvides
from collective.futures.interfaces import IContainsPromises
from collective.futures.testing import FUTURES_ROBOT_TESTING
from collective import futures


logger = logging.getLogger('collective.futures')


def echo(value):
    logger.info(u'thread: {0:s}'.format(threading.currentThread()))
    logger.info(u'echo: {0:s}'.format(value))
    return value


class ResultView(BrowserView):
    def content(self):
        try:
            return futures.result('futures.testing')
        except futures.FutureNotSubmittedError:
            futures.submit('futures.testing', echo, u'testing-result')
            return u'testing placeholder'


class ResultOrSubmitView(BrowserView):
    def content(self):
        return futures.resultOrSubmit('futures.testing', u'placeholder',
                                      echo, u'testing-result-or-submit')


class ResultOrSubmitPlaceholderView(BrowserView):
    def content(self):
        try:
            return futures.resultOrSubmit('futures.testing', u'placeholder',
                                          echo, u'testing-result-or-submit')
        finally:
            noLongerProvides(self.request, IContainsPromises)


class ResultMultiprocessView(BrowserView):
    def content(self):
        try:
            return futures.result('futures.testing')
        except futures.FutureNotSubmittedError:
            futures.submitMultiprocess('futures.testing',
                                       echo, u'testing-result-multiprocess')
            return u'testing placeholder'


class ResultOrSubmitMultiprocessView(BrowserView):
    def content(self):
        return futures.resultOrSubmitMultiprocess(
            'futures.testing', u'placeholder',
            echo, u'testing-result-or-submit-multiprocess')


class TransactionAbortView(BrowserView):
    """For testing that transactions are properly aborted if submitted
    futures exist

    """
    def content(self):
        try:
            futures.result('futures.testing')
            return getattr(self.context, '_futures_flag', u'transaction-abort')
        except futures.FutureNotSubmittedError:
            setattr(self.context, '_futures_flag', u'transaction-commit')
            setattr(self.context, '_p_changed', True)
            futures.submit('futures.testing', echo, u'testing-result')
            return u'testing placeholder'


class TransactionCommitView(TransactionAbortView):
    """For testing that transaction can be committed with force to override
    the default behavior

    """
    def content(self):
        try:
            return super(TransactionCommitView, self).content()
        finally:
            import transaction
            transaction.commit()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite('test_acceptance.robot'),
                layer=FUTURES_ROBOT_TESTING),
    ])
    return suite
