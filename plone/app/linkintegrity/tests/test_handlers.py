# -*- coding: utf-8 -*-
from plone.app.linkintegrity.handlers import findObject
from plone.app.linkintegrity.testing import create
from plone.app.linkintegrity.tests.base import DXBaseTestCase
from plone.app.testing import logout

import six


class FindObjectTests:
    """ testing the handlers.findObject function """

    def test_relative_to_portal_root_1(self):
        obj, components = findObject(self.portal.doc1, '/plone/doc2')
        self.assertEqual(obj.absolute_url_path(), '/plone/doc2')
        self.assertEqual(components, '')

    def test_relative_to_portal_root_2(self):
        # Prevent regression.
        # See https://github.com/plone/plone.app.linkintegrity/pull/17
        obj, components = findObject(self.portal.doc1, '/doc2')
        self.assertEqual(obj.absolute_url_path(), '/plone/doc2')
        self.assertEqual(components, '')

    def test_webserver_rewrites_portal_name(self):
        # test the case where a webserver rewrites the portal name,
        # e.g. for Apache:
        # RewriteRule ^/wssitename(.*)$ http://localhost:8080/VirtualHostBase/http/my.domain.com:80/plonesitename/VirtualHostRoot/_vh_wssitename$1  # noqa
        self.portal.REQUEST.other['VirtualRootPhysicalPath'] = ('', 'plone')
        self.portal.REQUEST._script = ['plone_foo']
        obj, components = findObject(self.portal.doc1, '/plone_foo/doc2')
        self.assertEqual(obj.absolute_url_path(), '/plone_foo/doc2')
        self.assertEqual(obj.getPhysicalPath(), ('', 'plone', 'doc2'))
        self.assertEqual(components, '')

    def test_uuid_link(self):
        # Test that objects can be found from uuid links.
        create(self.portal, 'Document', id='target', title='Target')
        target = self.portal.target
        target_uid = target.UID()
        path = "../resolveuid/{}".format(target_uid)

        # We logout.  This is to check that findObject also finds objects
        # that are not visible to the current user, like a private page.
        # See https://github.com/plone/plone.app.linkintegrity/issues/79
        # Note that in the Archetypes tests this is no problem,
        # but for Dexterity it is.  Likely they use a different workflow.
        logout()

        obj, components = findObject(self.portal.doc1, path)
        self.assertEqual(obj.absolute_url_path(), '/plone/target')
        self.assertEqual(components, path)


class ReferenceGenerationDXTestCase(DXBaseTestCase, FindObjectTests):
    """findObject testcase for dx content types"""

if six.PY2:
    from plone.app.linkintegrity.tests.base import ATBaseTestCase

    class ReferenceGenerationATTestCase(ATBaseTestCase, FindObjectTests):
        """findObject testcase for at content types"""
