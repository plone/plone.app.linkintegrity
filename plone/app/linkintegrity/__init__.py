try:
    # this import not used except as a test for Zope 2.12+
    from Products.Five.bbb import AcquisitionBBB
    AcquisitionBBB      # make pyflakes happy
    HAS_ZOPE_212 = True
except ImportError:
    HAS_ZOPE_212 = False

import pkg_resources

