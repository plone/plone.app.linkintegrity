from zope.interface import implements
from interfaces import ILinkIntegrityNotificationException
from OFS.ObjectManager import BeforeDeleteException


class LinkIntegrityNotificationException(BeforeDeleteException):
    """ an exception indicating a prevented link integrity breach """
    implements(ILinkIntegrityNotificationException)
