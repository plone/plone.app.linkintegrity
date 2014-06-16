try:
    # this import not used except as a test for Zope 2.12+
    from Products.Five.bbb import AcquisitionBBB
    AcquisitionBBB      # make pyflakes happy
    HAS_ZOPE_212 = True
except ImportError:
    HAS_ZOPE_212 = False

import pkg_resources

try:
    pkg_resources.get_distribution('plone.app.multilingual')
except pkg_resources.DistributionNotFound:
    HAS_PAM = False
else:
    HAS_PAM = True

try:
    pkg_resources.get_distribution('Products.LinguaPlone')
except pkg_resources.DistributionNotFound:
    HAS_LINGUAPLONE = False
else:
    HAS_LINGUAPLONE = True


def initialize(context):

    # side effect import to patch the response's retry method
    import monkey

    # Install the wrapper around zpublisher_exception_hook.
    monkey.installExceptionHook()

    # Install the status code for linkintegritynotificationexception
    monkey.installStatusCode()


import monkey2
monkey2  # pyflakes
