# the following code is "stolen" from (or maybe it was inspired by? :))
# FiveException (http://codespeak.net/svn/z3/FiveException)

from Zope2.App.startup import zpublisher_exception_hook
from ZPublisher.Publish import Retry
from ZPublisher.Publish import get_module_info


def zpublisher_exception_hook_wrapper(published, REQUEST, t, v, traceback):
    """ wrapper around the zope2 zpublisher's error hook """
    try:
        # if we got a retry exception, we just propagate it instead of
        # trying to log it (like FiveException does)
        if t is Retry:
            v.reraise()
        return zpublisher_exception_hook(published, REQUEST, t, v, traceback)
    finally:
        traceback = None


def proxy_get_module_info(*args, **kwargs):
    results = list(get_module_info(*args, **kwargs))
    if results[5] is zpublisher_exception_hook:
        results[5] = zpublisher_exception_hook_wrapper
    return tuple(results)


def installExceptionHook():
    import ZPublisher.Publish
    ZPublisher.Publish.get_module_info = proxy_get_module_info


def installStatusCode():
    from ZPublisher import HTTPResponse
    HTTPResponse.status_codes['linkintegritynotificationexception'] = 200


def retry(self):
    """ re-initialize a response object to be used in a retry attempt """
    # this implementation changes the original one so that the response
    # instance is reused instead of replaced with a new one (after a Retry
    # exception was raised);  this fixes a bug in zopedoctests' http()
    # function (Testing/ZopeTestCase/zopedoctest/functional.py:113);
    # the doctest code assumes that the HTTPResponse instance passed to
    # publish_module() (line 177) is used to handle to complete request, so
    # it can be used to get the status, headers etc later on (lines 183-186);
    # normally this is okay, but raising a Retry will create a new response
    # instance, which will then hold that data (relevant for evaluating the
    # doctest) while the original (passed in) instance is still empty...
    #
    # so to fix this (quickly) retry() now cleans up and returns itself:
    self.__init__(stdout=self.stdout, stderr=self.stderr)
    return self

from ZPublisher.HTTPResponse import HTTPResponse
HTTPResponse.retry = retry
