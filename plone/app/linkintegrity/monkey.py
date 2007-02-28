# the following code is "stolen" from (or maybe it was inspired by? :))
# FiveException (http://codespeak.net/svn/z3/FiveException)

from zope.component import queryMultiAdapter
from Zope2.App.startup import zpublisher_exception_hook
from ZPublisher.Publish import Retry


def zpublisher_exception_hook_wrapper(published, REQUEST, t, v, traceback):
    """ wrapper around the zope2 zpublisher's error hook """
    try:
        # if we got a retry exception, we just propagate it instead of
        # trying to log it (like FiveException does)
        if t is Retry:
            v.reraise()
        # first we try to find a view/adapter for the current exception and
        # let the original function try to handle the exception if we can't
        # find one...
        view = queryMultiAdapter((v, REQUEST), name='index.html', default=None)
        if view is None:
            zpublisher_exception_hook(published, REQUEST, t, v, traceback)
        else:
            # otherwise render the view and raise the rendered string like
            # raise_standardErrorMessage does...
            view = view.__of__(published)
            message = view()
            raise t, message, traceback
    finally:
        traceback = None


def installExceptionHook():
    # notes from FiveException:
    #   really hairy hack to get the modules dictionary from the
    #   default argument of get_module_info. We need to modify this in order
    #   modify the err_hook (which is zpublisher_exception_hook) after Zope
    #   has already started up
    from ZPublisher.Publish import get_module_info
    from AccessControl.SecurityManagement import noSecurityManager
    #   we need to call this once to initialize the modules dictionary
    get_module_info('Zope2')
    modules = get_module_info.func_defaults[0]
    (bobo_before, bobo_after, object, realm, debug_mode, err_hook,
     validated_hook, transactions_manager) = modules['Zope2']
    if bobo_before is None:
        # Make sure bobo_before for Zope2 is set correctly, otherwhise the
        # Zope security machinery breaks down. Since we are called before
        # Zope2.App.startup has setup its __bobo_before__ hook and
        # get_module_info will cache that information we need to set that
        # explicitly ourselves.
        bobo_before = noSecurityManager
    modules['Zope2'] = (bobo_before, bobo_after, object, realm,
                        debug_mode, zpublisher_exception_hook_wrapper,
                        validated_hook, transactions_manager)



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

