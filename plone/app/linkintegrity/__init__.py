# test for Zope 2.12 -- the first eggified Zope
import pkg_resources
try:
    dist=pkg_resources.get_distribution('Zope2')
    HAS_ZOPE_212 = True
except pkg_resources.DistributionNotFound:
    HAS_ZOPE_212 = False

def initialize(context):

    # side effect import to patch the response's retry method
    import monkey

    # If < Zope 2.12, install the wrapper around zpublisher_exception_hook.
    # The patch is not needed or wanted in Zope 2.12, which already includes
    # the error view lookup in its ZPublisherExceptionHook, and which sometimes
    # expects the error message to be returned instead of raised depending on 
    # the response's handle_errors attribute.
    if not HAS_ZOPE_212:
        monkey.installExceptionHook()
