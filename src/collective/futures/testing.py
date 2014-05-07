# -*- coding:utf-8 -*-
import logging
from plone.app.robotframework import RemoteLibraryLayer
from plone.app.robotframework.remote import RemoteLibrary
from plone.app.testing import (
    PloneSandboxLayer,
    PLONE_FIXTURE,
    IntegrationTesting,
    FunctionalTesting,
)
from plone.testing import z2
from zope.testing.loggingsupport import InstalledHandler


class Futures(RemoteLibrary):

    def start_futures_logging(self):
        self._v_record = InstalledHandler('collective.futures',
                                          level=logging.DEBUG)

    def get_futures_log(self):
        return unicode(self._v_record)

    def stop_futures_logging(self):
        self._v_record.uninstall()

REMOTE_LIBRARY_BUNDLE_FIXTURE = RemoteLibraryLayer(
    bases=(PLONE_FIXTURE,),
    libraries=(Futures,),
    name="RemoteLibraryBundle:RobotRemote"
)


class FuturesTests(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.futures
        self.loadZCML(package=collective.futures)

        import collective.futures.tests
        self.loadZCML(package=collective.futures.tests,
                      name='test_acceptance.zcml')

    def setUpPloneSite(self, portal):
        portal.portal_workflow.setDefaultChain('simple_publication_workflow')

    def testSetUp(self):
        handler = InstalledHandler('collective.futures')


FUTURES_FIXTURE = FuturesTests()

FUTURES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FUTURES_FIXTURE,),
    name='FuturesTests:Integration')

FUTURES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FUTURES_FIXTURE,),
    name='FuturesTests:Functional')

FUTURES_ROBOT_TESTING = FunctionalTesting(
    bases=(FUTURES_FIXTURE,
           REMOTE_LIBRARY_BUNDLE_FIXTURE,
           z2.ZSERVER),
    name='FuturesTests:Robot')
