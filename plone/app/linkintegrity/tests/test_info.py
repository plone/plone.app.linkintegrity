import unittest


class TestLinkIntegrityInfo(unittest.TestCase):
    
    def test_confirmedItems_decodes_oids_with_colons(self):
        oid1 = '\x00' * 8
        oid2 = ':' * 8
        info = ('%s:%s' % (oid1, oid2)).encode('base64')
        class DummyContext(object):
            environ = {'link_integrity_info': info}
        
        from plone.app.linkintegrity.info import LinkIntegrityInfo
        info = LinkIntegrityInfo(DummyContext())
        confirmed = info.confirmedItems()
        self.assertEqual(2, len(confirmed))
