# -*- coding: utf-8 -*-
from ZPublisher import HTTPResponse
from ZPublisher.HTTPRequest import HTTPRequest

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

import transaction
import unittest

orig_status_codes = HTTPResponse.status_codes
orig_set = HTTPRequest.set


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.request, IFormLayer)

        transaction.commit()

        # Get a testbrowser
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader('Referer', self.portal.absolute_url())
        self.browser.addHeader(
            'Authorization',
            'Basic {0:s}:{1:s}'.format(TEST_USER_NAME, TEST_USER_PASSWORD))

        setRoles(self.portal, TEST_USER_ID, ['Manager', ])

    def _disable_event_count_helper(self):
        # so here's yet another monkey patch ;), but only to avoid having
        # to change almost all the tests after introducing the setting of
        # the helper value in 'folder_delete', which prevents presenting
        # the user with multiple confirmation forms; this patch prevents
        # setting the value and is meant to disable this optimization in
        # some of the tests written so far, thereby not invalidating them...
        def set(self, key, value, set_orig=orig_set):
            if key == 'link_integrity_events_to_expect':
                value = 0
            orig_set(self, key, value)
        HTTPRequest.set = set

    def tearDown(self):
        HTTPResponse.status_codes = orig_status_codes
        HTTPRequest.set = orig_set

    def _get_token(self, obj):
        return getMultiAdapter(
            (obj, self.request), name='authenticator').token()

    def _set_response_status_code(self, key, value):
        HTTPResponse.status_codes[key.lower()] = value


class DXBaseTestCase(BaseTestCase):
    """Base testcase for testing Dexterity content types"""

    layer = testing.PLONE_APP_LINKINTEGRITY_DX_INTEGRATION_TESTING

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


class ATBaseTestCase(BaseTestCase):
    """Base testcase for testing Archetypes content types"""

    layer = testing.PLONE_APP_LINKINTEGRITY_AT_INTEGRATION_TESTING

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
