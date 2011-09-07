from Products.PloneTestCase import PloneTestCase
from Products.Five.testbrowser import Browser


def getBrowser(loggedIn=False):
    """ instantiate and return a testbrowser for convenience """
    browser = Browser()
    browser.handleErrors = True
    if loggedIn:
        user = PloneTestCase.default_user
        pwd = PloneTestCase.default_password
        browser.addHeader('Authorization', 'Basic %s:%s' % (user, pwd))
    return browser
