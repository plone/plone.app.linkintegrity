# -*- coding: utf-8 -*-
from plone.app.linkintegrity import testing
from plone.app.relationfield.behavior import IRelatedItems
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.textfield import RichTextValue
from plone.testing.z2 import Browser
from z3c.form.interfaces import IFormLayer
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.lifecycleevent import modified

import six
import unittest


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.request, IFormLayer)

        # Get a testbrowser
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader('Referer', self.portal.absolute_url())
        self.browser.addHeader(
            'Authorization',
            'Basic {0:s}:{1:s}'.format(TEST_USER_NAME, TEST_USER_PASSWORD))

        # Do an initial page load to make sure the bundles get compiled
        # (which currently commits a transaction)
        # before we render exception views
        self.browser.open(self.portal.absolute_url())

        setRoles(self.portal, TEST_USER_ID, ['Manager', ])

    def _get_token(self, obj):
        return getMultiAdapter(
            (obj, self.request), name='authenticator').token()


class DXBaseTestCase(BaseTestCase):
    """Base testcase for testing Dexterity content types"""

    layer = testing.PLONE_APP_LINKINTEGRITY_DX_FUNCTIONAL_TESTING

    def _set_text(self, obj, text):
        obj.text = RichTextValue(text)
        modified(obj)

    def _get_text(self, obj):
        return obj.text.raw

    def _set_related_items(self, obj, items):
        assert IRelatedItems.providedBy(obj)
        setattr(obj, 'relatedItems', items)
        modified(obj)

    def _get_related_items(self, obj):
        return obj.relatedItems


if six.PY2:
    class ATBaseTestCase(BaseTestCase):
        """Base testcase for testing Archetypes content types"""

        layer = testing.PLONE_APP_LINKINTEGRITY_AT_FUNCTIONAL_TESTING

        def _set_text(self, obj, text):
            obj.setText(text, mimetype='text/html')
            modified(obj)

        def _get_text(self, obj):
            # This is the equivalent to obj.text in dexterity. No transforms,
            # no rewritten relative urls
            return obj.getText(raw=1).raw

        def _set_related_items(self, obj, items):
            obj.setRelatedItems(items)
            modified(obj)

        def _get_related_items(self, obj):
            return obj.getRelatedItems()
