try:
    # this import not used except as a test for Zope 2.12+
    from Products.Five.bbb import AcquisitionBBB
    HAS_ZOPE_212 = True
except ImportError:
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
